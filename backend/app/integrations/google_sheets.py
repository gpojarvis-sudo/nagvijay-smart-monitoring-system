"""
Google Sheets Integration - Two-way sync
For bulk target management and achievement import
"""
from __future__ import annotations
import re

from typing import List, Dict, Any, Optional
import json

import structlog
from google.oauth2 import service_account
from googleapiclient.discovery import build

from app.core.config import get_settings

logger = structlog.get_logger(__name__)
settings = get_settings()


SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]


class GoogleSheetsIntegration:
    """Google Sheets sync client"""
    
    def __init__(self):
        self.service = None
        self.credentials = None
        
        if settings.GOOGLE_SHEETS_CREDENTIALS_JSON:
            try:
                creds_info = json.loads(settings.GOOGLE_SHEETS_CREDENTIALS_JSON)
                self.credentials = service_account.Credentials.from_service_account_info(
                    creds_info, scopes=SCOPES
                )
                self.service = build("sheets", "v4", credentials=self.credentials)
                logger.info("sheets_client_initialized")
            except Exception as e:
                logger.error("sheets_init_failed", error=str(e))
        else:
            logger.warning("sheets_credentials_not_configured")
    
    def is_configured(self) -> bool:
        return self.service is not None
    
    async def read_sheet(self, spreadsheet_id: str, range_name: str = "Sheet1!A1:Z1000") -> List[List[str]]:
        """Read sheet data"""
        
        if not self.is_configured():
            raise ValueError("Google Sheets not configured - set GOOGLE_SHEETS_CREDENTIALS_JSON")
        
        try:
            result = self.service.spreadsheets().values().get(
                spreadsheetId=spreadsheet_id,
                range=range_name,
            ).execute()
            
            values = result.get("values", [])
            logger.info("sheet_read", spreadsheet_id=spreadsheet_id, rows=len(values))
            return values
        
        except Exception as e:
            import traceback
            logger.error("sheet_read_failed", error=str(e), traceback=traceback.format_exc(), spreadsheet_id=spreadsheet_id)
            raise RuntimeError(f"Google Sheets error: {type(e).__name__}: {e}")
    
    async def write_sheet(self, spreadsheet_id: str, range_name: str, values: List[List[Any]]) -> Dict:
        """Write data to sheet"""
        
        if not self.is_configured():
            raise ValueError("Google Sheets not configured")
        
        try:
            body = {"values": values}
            result = self.service.spreadsheets().values().update(
                spreadsheetId=spreadsheet_id,
                range=range_name,
                valueInputOption="USER_ENTERED",
                body=body,
            ).execute()
            
            logger.info("sheet_written", spreadsheet_id=spreadsheet_id, updated_cells=result.get("updatedCells"))
            return result
        
        except Exception as e:
            logger.error("sheet_write_failed", error=str(e))
            raise
    
    async def append_row(self, spreadsheet_id: str, range_name: str, values: List[Any]) -> Dict:
        """Append a single new row to the sheet WITHOUT overwriting existing rows."""

        if not self.is_configured():
            raise ValueError("Google Sheets not configured")

        try:
            body = {"values": [values]}
            result = self.service.spreadsheets().values().append(
                spreadsheetId=spreadsheet_id,
                range=range_name,
                valueInputOption="USER_ENTERED",
                insertDataOption="INSERT_ROWS",
                body=body,
            ).execute()

            logger.info(
                "sheet_row_appended",
                spreadsheet_id=spreadsheet_id,
                updates=result.get("updates", {}),
            )
            return result

        except Exception as e:
            logger.error("sheet_append_failed", error=str(e), spreadsheet_id=spreadsheet_id)
            raise RuntimeError(f"Google Sheets append error: {type(e).__name__}: {e}")


    async def append_rows(self, spreadsheet_id: str, range_name: str, values: List[List[Any]]) -> Dict:
        """Append multiple rows in a single Google Sheets API request."""

        if not self.is_configured():
            raise ValueError("Google Sheets not configured")

        try:
            body = {"values": values}
            result = self.service.spreadsheets().values().append(
                spreadsheetId=spreadsheet_id,
                range=range_name,
                valueInputOption="USER_ENTERED",
                insertDataOption="INSERT_ROWS",
                body=body,
            ).execute()

            logger.info(
                "sheet_rows_appended",
                spreadsheet_id=spreadsheet_id,
                rows=len(values),
            )

            return result

        except Exception as e:
            logger.error("sheet_append_rows_failed", error=str(e), spreadsheet_id=spreadsheet_id)
            raise RuntimeError(f"Google Sheets append error: {type(e).__name__}: {e}")


    async def parse_office_import_sheet(self, spreadsheet_id: str) -> List[Dict[str, Any]]:
        """Parse office master import sheet"""
        
        rows = await self.read_sheet(spreadsheet_id, "Offices!A1:Z1000")
        if not rows or len(rows) < 2:
            return []
        
        headers = [h.strip().lower().replace(" ", "_") for h in rows[0]]
        offices = []
        
        for row in rows[1:]:
            # Pad row to headers length
            row_padded = row + [""] * (len(headers) - len(row))
            office = dict(zip(headers, row_padded))
            
            # Validate required
            if not office.get("office_code") or not office.get("office_name"):
                continue
            
            offices.append(office)
        
        return offices
    
    async def parse_achievement_sheet(self, spreadsheet_id: str | None = None) -> List[Dict[str, Any]]:
        """Parse achievement sheet"""

        spreadsheet_id = spreadsheet_id or settings.GOOGLE_SHEETS_SPREADSHEET_ID
        sheet_name = settings.GOOGLE_SHEETS_SHEET_NAME or "Form Responses 1"

        rows = await self.read_sheet(
            spreadsheet_id,
            f"{sheet_name}!A1:Z1000",
        )
        if not rows or len(rows) < 2:
            return []
        
        headers = [h.strip().lower().replace(" ", "_") for h in rows[0]]
        achievements = []
        
        for idx, row in enumerate(rows[1:], start=2):
            row_padded = row + [""] * (len(headers) - len(row))
            ach = dict(zip(headers, row_padded))
            ach["_row_number"] = idx
            
            if not ach.get("office_code") or not ach.get("scheme_code"):
                continue
            
            achievements.append(ach)
        
        return achievements


    async def parse_daily_office_report_sheet(self, spreadsheet_id: str | None = None) -> List[Dict[str, Any]]:
        """Parse daily office report sheet with proper column mapping"""

        spreadsheet_id = spreadsheet_id or settings.GOOGLE_SHEETS_SPREADSHEET_ID
        sheet_name = "Office wise"

        rows = await self.read_sheet(
            spreadsheet_id,
            f"{sheet_name}!A1:ZZ1000",
        )

        if not rows or len(rows) < 3:
            return []

        header_row = rows[1] if len(rows) > 1 else []
        headers = []
        for h in header_row:
            if h:
                h = h.strip().lower()
                h = re.sub(r'[\s./]+', '_', h)
                h = re.sub(r'_+', '_', h)
                if h.endswith('_'):
                    h = h[:-1]
                headers.append(h)
            else:
                headers.append('')

        field_map = {
            'office_name': 'office_name',
            'date': 'report_date',
            'no_of_sb_a_c_opened': 'sb_opened',
            'no_of_sb_a_c_closed': 'sb_closed',
            'net_accounts': 'net_accounts',
            'no_of_new_policy': 'pli_policies',
            'sum_assured': 'sum_assured',
            'total_premium': 'premium',
            'speed_post_documents_revenue': 'speed_post_document',
            'speed_post_parcle_revenue': 'speed_post_parcel',
            'business_post_revenue': 'business_post',
            'internation_letter_revenue': 'international_letter',
            'logistic_revenue': 'logistics',
            'no_of_aadhar_txn': 'aadhaar_transactions',
            'total_amount_of_aadhar': 'aadhaar_amount',
        }

        reports = []
        for idx, row in enumerate(rows[2:], start=3):
            if len(row) < len(headers):
                row = row + [''] * (len(headers) - len(row))
            row_dict = dict(zip(headers, row))
            if not row_dict.get('office_name') or not row_dict.get('date'):
                continue
            report = {}
            for header, value in row_dict.items():
                if header in field_map:
                    model_field = field_map[header]
                    if value == '':
                        value = None
                    if model_field in ['sb_opened','sb_closed','net_accounts','pli_policies','aadhaar_transactions']:
                        try:
                            value = int(value) if value is not None else 0
                        except:
                            value = 0
                    elif model_field in ['sum_assured','premium','speed_post_document','speed_post_parcel','business_post','international_letter','logistics','aadhaar_amount']:
                        try:
                            value = float(value) if value is not None else 0.0
                        except:
                            value = 0.0
                    report[model_field] = value
            report['office_name_original'] = row_dict.get('office_name')
            report['_row_number'] = idx
            reports.append(report)

        return reports
    async def export_dashboard_to_sheet(self, spreadsheet_id: str, dashboard_data: Dict[str, Any]) -> Dict:
        """Export dashboard stats to sheet for sharing"""
        
        # Prepare data
        kpis = dashboard_data.get("kpis", {})
        
        values = [
            ["NagVijay Smart Monitoring System - Dashboard Export", ""],
            ["Generated At", dashboard_data.get("generated_at", "")],
            ["", ""],
            ["KPI", "Value"],
            ["Total Offices", kpis.get("total_offices", 0)],
            ["Total Employees", kpis.get("total_employees", 0)],
            ["Total Targets", kpis.get("total_targets", 0)],
            ["Total Achieved", kpis.get("total_achieved", 0)],
            ["Achievement %", f"{kpis.get('overall_achievement_percentage', 0)}%"],
            ["Active Schemes", kpis.get("active_schemes", 0)],
            ["", ""],
            ["Top Performers", ""],
        ]
        
        for performer in dashboard_data.get("top_performers", [])[:5]:
            values.append([performer.get("office_name", ""), f"{performer.get('percentage', 0)}%"])
        
        return await self.write_sheet(spreadsheet_id, "Dashboard!A1:B50", values)


# Singleton
_sheets_client: Optional[GoogleSheetsIntegration] = None


def get_sheets_client() -> GoogleSheetsIntegration:
    global _sheets_client
    if _sheets_client is None:
        _sheets_client = GoogleSheetsIntegration()
    return _sheets_client
