from pathlib import Path

p = Path("app/api/v1/daily_reports.py")
text = p.read_text()

if "DailyReportCreate" not in text:
    text = text.replace(
        "from app.schemas.daily_report import DailyReportResponse, DailyReportSummary",
        "from app.schemas.daily_report import DailyReportCreate, DailyReportResponse, DailyReportSummary"
    )

if "@router.post(" not in text:
    endpoint = '''

@router.post("/", response_model=DailyReportResponse)
async def create_daily_report(
    payload: DailyReportCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    service = DailyOfficeReportService(db)
    report = await service.upsert(payload.model_dump())
    return report

'''
    text = text.replace("@router.get(\"/summary\"", endpoint + "\n@router.get(\"/summary\"")

p.write_text(text)
print("POST endpoint added successfully.")
