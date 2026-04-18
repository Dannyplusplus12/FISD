# StuffStorageManager

Monorepo gồm 3 service để deploy Railway:

- `backend/` — FastAPI backend.
- `cronjob/` — cron backup PostgreSQL gửi Telegram.
- `frontend/` — Flutter PWA frontend.

Scripts migration/phụ trợ DB được gom trong `backend/scripts/`.

Quick start (backend)

1. Create a virtual environment and install backend dependencies:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r backend/requirements.txt
```

2. Run the FastAPI app (development):

```powershell
cd backend
uvicorn api:app --reload --port 8000
```

3. DB utility scripts

- `backend/scripts/migrate_to_cloud.py`
- `backend/scripts/download_from_cloud.py`

Quick start (Flutter frontend)

1. Install Flutter SDK and tools.
2. From `frontend/` run:

```bash
flutter pub get
flutter run
```

Cronjob

Chạy local:

```powershell
cd cronjob
pip install -r requirements.txt
python backup_postgres_to_telegram.py --label railway
```




