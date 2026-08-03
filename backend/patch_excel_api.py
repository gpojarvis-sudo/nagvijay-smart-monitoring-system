from pathlib import Path

p = Path("app/api/v1/daily_reports.py")
text = p.read_text()

import_line = "from app.services.excel_export_service import ExcelExportService\n"

if import_line not in text:
    text = text.replace(
        "from app.services.daily_office_report_service import DailyOfficeReportService\n",
        "from app.services.daily_office_report_service import DailyOfficeReportService\n"
        + import_line,
    )

old = """    elif format == "excel":
        wb = Workbook()
        ws = wb.active
        ws.title = "Daily Report"
        if reports:
            headers = list(reports[0].__dict__.keys())
            headers = [h for h in headers if not h.startswith('_')]
            ws.append(headers)
            for r in reports:
                row = [getattr(r, h) for h in headers]
                ws.append(row)
        output = io.BytesIO()
        wb.save(output)
        output.seek(0)
        return Response(
            content=output.getvalue(),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename=daily_report_{report_date.isoformat()}.xlsx"}
        )
"""

new = """    elif format == "excel":
        output = ExcelExportService().generate(
            reports=reports,
            report_date=report_date,
        )

        return Response(
            content=output.getvalue(),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={
                "Content-Disposition":
                f'attachment; filename="Daily_Monitoring_{report_date.isoformat()}.xlsx"'
            },
        )
"""

if old not in text:
    raise SystemExit("Excel block not found. No changes made.")

text = text.replace(old, new)

p.write_text(text)

print("SUCCESS")
