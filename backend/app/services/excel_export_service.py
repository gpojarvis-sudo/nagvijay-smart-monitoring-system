from io import BytesIO
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment


class ExcelExportService:

    def generate(self, reports, report_date):

        wb = Workbook()

        ws = wb.active
        ws.title = "Office Wise"

        headers = [
            "Sr No",
            "Office Name",
            "Office Code",
            "Report Date",
            "SB Opened",
            "SB Closed",
            "Net Accounts",
            "PLI Policies",
            "Sum Assured",
            "Premium",
            "Speed Post Document",
            "Speed Post Parcel",
            "Business Post",
            "Logistics",
            "International",
            "Aadhaar Txn",
            "Aadhaar Amount",
        ]

        fill = PatternFill(fill_type="solid",
                           start_color="C00000",
                           end_color="C00000")

        for col, h in enumerate(headers, start=1):
            c = ws.cell(row=1, column=col)
            c.value = h
            c.font = Font(bold=True, color="FFFFFF")
            c.fill = fill
            c.alignment = Alignment(horizontal="center")

        row = 2

        for i, r in enumerate(reports, start=1):

            ws.cell(row,1).value=i
            ws.cell(row,2).value=r.office_name
            ws.cell(row,3).value=r.office_code
            ws.cell(row,4).value=str(report_date)
            ws.cell(row,5).value=r.sb_opened
            ws.cell(row,6).value=r.sb_closed
            ws.cell(row,7).value=r.net_accounts
            ws.cell(row,8).value=r.pli_policies
            ws.cell(row,9).value=float(r.sum_assured)
            ws.cell(row,10).value=float(r.premium)
            ws.cell(row,11).value=r.speed_post_document
            ws.cell(row,12).value=r.speed_post_parcel
            ws.cell(row,13).value=r.business_post
            ws.cell(row,14).value=r.logistics
            ws.cell(row,15).value=r.international_letter
            ws.cell(row,16).value=r.aadhaar_transactions
            ws.cell(row,17).value=float(r.aadhaar_amount)

            row += 1

        for col in ws.columns:
            length=max(len(str(c.value or "")) for c in col)
            ws.column_dimensions[col[0].column_letter].width=min(length+3,35)

        output=BytesIO()
        wb.save(output)
        output.seek(0)

        return output
