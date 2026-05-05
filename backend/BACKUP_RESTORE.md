# Backup/Restore PostgreSQL (Railway)

## Backup (tạo file `.dump`)
> Thực hiện từ thư mục root repo (nơi có folder `backend/`).

```bash
# Backup DB Railway về file .dump trong backend/
docker run --rm -v "${PWD}:/backup" postgres:17 \
  pg_dump --format=custom \
  --dbname "postgresql://postgres:<PASSWORD>@roundhouse.proxy.rlwy.net:31220/railway" \
  --file "/backup/backend/railway_backup_YYYYMMDD_HHMMSS.dump"
```

## Restore (khôi phục từ file `.dump`)
> **Cảnh báo:** lệnh này sẽ xóa toàn bộ dữ liệu hiện tại (DROP SCHEMA public CASCADE) trước khi restore.

```bash
# 1) Xóa schema hiện tại
docker run --rm -v "${PWD}:/backup" postgres:17 \
  psql "postgresql://postgres:<PASSWORD>@roundhouse.proxy.rlwy.net:31220/railway" \
  -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;"

# 2) Restore file dump
docker run --rm -v "${PWD}:/backup" postgres:17 \
  pg_restore --no-owner --no-privileges \
  --dbname "postgresql://postgres:<PASSWORD>@roundhouse.proxy.rlwy.net:31220/railway" \
  "/backup/backend/railway_backup_YYYYMMDD_HHMMSS.dump"
```

## Ghi chú
- Sử dụng Docker giúp không cần cài PostgreSQL client trên máy.
- Nếu `pg_restore` báo lỗi `unsupported version`, cần dùng image Postgres đúng phiên bản (dump hiện tại dùng Postgres 17).
- Khi đổi database/host, thay URL trong lệnh ở trên.
