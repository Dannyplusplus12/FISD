# 2026-04-18 - Railway service split prep
- Tách mã cronjob backup PostgreSQL ra thư mục riêng `cronjob/` để triển khai thành service độc lập.
- Chuẩn hóa file chạy dịch vụ theo từng service bằng `Procfile`:
  - `backend/Procfile` cho API.
  - `frontend/Procfile` cho PWA.
  - `cronjob/Procfile` cho tác vụ backup Telegram.
- Giữ `backend/` là service API riêng, không để lẫn script cronjob backup DB.

# 2026-04-18 - Root cleanup
- Dọn file ngoài 3 thư mục chính (`backend/`, `cronjob/`, `frontend/`) để repo gọn hơn.
- Chuyển script tiện ích DB từ root vào `backend/scripts/`:
  - `backend/scripts/migrate_to_cloud.py`
  - `backend/scripts/download_from_cloud.py`
- Xóa các file root cũ/không còn dùng: `BackendFrontendOnly.sln`, `railway.cron.toml`, `requirements.txt`, `run_app.py`, `README_DEV.md`, `GITIGNORE_CHECKLIST.md`, `config.json`.
- Xóa metadata Git cũ trong `backend/.git` và thư mục `backend/cronjob` dư thừa.

# 2026-04-18 - Git/Railway strategy
- Chốt chiến lược dùng **1 GitHub repo duy nhất** cho toàn bộ FISD (monorepo), không tách 3 repo.
- Trên Railway sẽ tạo nhiều service từ cùng 1 repo và cấu hình `Root Directory` theo từng service:
  - `backend/` cho API
  - `cronjob/` cho backup job
  - `frontend/` cho PWA
