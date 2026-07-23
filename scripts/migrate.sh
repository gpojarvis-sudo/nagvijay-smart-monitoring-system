#!/bin/bash
set -e
echo "Running DB migrations - creates tables via SQLAlchemy if not exists"
cd backend
source venv/bin/activate || true
python -c "
import asyncio
from app.core.database import init_db
async def main():
    await init_db()
    print('DB initialized')
asyncio.run(main())
"
echo "Migration done"
