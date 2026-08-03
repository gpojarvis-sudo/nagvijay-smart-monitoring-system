from io import BytesIO
from pathlib import Path
from datetime import datetime

from openpyxl import load_workbook

TEMPLATE = (
    Path(__file__).resolve().parent.parent
    / "templates"
    / "Daily_Monitoring_Template.xlsx"
)

class ExcelExportService:

    def generate(self, reports, report_date):

        wb = load_workbook(TEMPLATE)

        response_sheet = wb["Form Responses 1"]

        if response_sheet.max_row > 1:
            response_sheet.delete_rows(2, response_sheet.max_row - 1)

        for r in reports:
            response_sheet.append([
                datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
                r.office_name,
                str(report_date),
                "",
                r.sb_opened,
                r.sb_closed,
                r.net_accounts,
                r.pli_policies,
                float(r.sum_assured),
                float(r.premium),
                r.speed_post_document,
                r.speed_post_parcel,
                r.business_post,
                r.international_letter,
                r.logistics,
                r.aadhaar_transactions,
                float(r.aadhaar_amount),
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
            ])

        output = BytesIO()
        wb.save(output)
        output.seek(0)
        return output
