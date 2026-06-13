# FISD — Hệ thống quản lý bán hàng & kho

## Tổng quan dự án

Ứng dụng quản lý bán hàng kho hàng bằng tiếng Việt, bao gồm:
- **Backend:** FastAPI + SQLAlchemy + PostgreSQL (Railway), hỗ trợ SQLite khi chạy local
- **Frontend:** Flutter (Windows desktop + mobile Android/iOS + web PWA)
- **Deploy:** Railway (backend), GitHub Releases (Windows `.exe` và Android `.apk`)

```
FISD-r/
├── backend/        FastAPI API server
│   ├── app/        Codebase module mới (phân tầng rõ ràng)
│   ├── api.py      Entry point cũ (legacy — sẽ dần chuyển vào app/)
│   └── database.py SQLAlchemy models
├── frontend/       Flutter app
│   ├── lib/
│   │   ├── screens/    Các màn hình chính
│   │   ├── services/   API client (api_service.dart)
│   │   ├── models/     Data classes
│   │   ├── dialogs/    Dialog widgets
│   │   └── widgets/    Reusable widgets
│   └── pubspec.yaml
├── cronjob/        Backup PostgreSQL → Telegram
└── CLAUDE.md
```

---

## Chạy local

### Backend (SQLite tự động, không cần Postgres)
```bash
cd backend
pip install -r requirements.txt
uvicorn api:app --reload --port 8000
```

### Backend với PostgreSQL local
```bash
cd backend
DATABASE_URL=postgresql://user:pass@localhost:5432/fisd uvicorn api:app --reload
```

### Frontend (Windows)
```bash
cd frontend
flutter pub get
flutter run -d windows
```

### Frontend (Chrome/Web)
```bash
cd frontend
flutter run -d chrome
```

---

## Biến môi trường (backend)

| Biến | Mô tả | Bắt buộc |
|------|-------|----------|
| `DATABASE_URL` | PostgreSQL URL (Railway tự inject) | Không (SQLite làm fallback) |
| `CORS_ALLOWED_ORIGINS` | Danh sách origin, cách nhau dấu phẩy | Không (`*` là default) |
| `TELEGRAM_DB_BOT_TOKEN` | Token bot Telegram để backup ảnh | Không |
| `TELEGRAM_DB_CHAT_ID` | Chat ID nhận backup | Không |
| `DELIVERY_UPLOAD_DIR` | Thư mục lưu ảnh giao hàng | Không (`/tmp/delivery_proofs`) |
| `MAX_DELIVERY_PHOTO_MB` | Giới hạn kích thước ảnh (MB) | Không (8MB) |

---

## Cấu trúc dữ liệu (domain models)

```
Product (sản phẩm)
  └── Variant (biến thể: màu + size + giá + tồn kho)

Area (khu vực)
  └── Customer (khách hàng: tên, sđt, công nợ)
        └── DebtLog (lịch sử thay đổi công nợ)
        └── Order (đơn hàng)
              └── OrderItem (dòng đơn: sản phẩm + variant + số lượng + giá)

Employee (nhân viên)
  roles: orderer | picker | manager
  └── tạo đơn (created_by_employee_id)
  └── nhận đơn / giao hàng (assigned_picker_id, delivered_by_id)
```

### Luồng trạng thái đơn hàng

```
[Orderer tạo đơn]
      ↓
  pending  ─── reject ──→ (xóa)
      ↓
   approved  (staff tiếp nhận, stock trừ ngay)
      ↓
   assigned  (picker nhận đơn)
      ↓
  completed  (picker xác nhận giao, công nợ cộng)
```

Ngoài ra còn có luồng **desktop-dispatch**:
- Desktop tạo đơn → thẳng `approved` (bỏ bước pending/approve)

---

## API endpoints (backend)

### Auth & Nhân viên
| Method | Path | Mô tả |
|--------|------|-------|
| POST | `/auth/pin-login` | Đăng nhập bằng PIN (4-8 số) |
| GET | `/employees` | Danh sách nhân viên |
| POST | `/employees` | Tạo nhân viên (auto-gen PIN) |
| PUT | `/employees/{id}` | Cập nhật nhân viên |
| DELETE | `/employees/{id}` | Xóa nhân viên |
| GET | `/employees/{id}/deliveries` | Lịch sử giao hàng |
| GET | `/employees/{id}/activities` | Lịch sử hoạt động (đơn + công nợ) |

### Sản phẩm
| Method | Path | Mô tả |
|--------|------|-------|
| GET | `/products?search=` | Danh sách sản phẩm |
| POST | `/products` | Thêm sản phẩm |
| PUT | `/products/{id}` | Sửa sản phẩm + variants |
| DELETE | `/products/{id}` | Xóa sản phẩm |
| POST | `/product-images/upload` | Upload ảnh sản phẩm |
| GET | `/product-images/{name}` | Lấy file ảnh |

### Khu vực & Khách hàng
| Method | Path | Mô tả |
|--------|------|-------|
| GET/POST | `/areas` | Danh sách / tạo khu vực |
| PUT/DELETE | `/areas/{id}` | Sửa / xóa khu vực |
| GET/POST | `/customers` | Danh sách / tạo khách hàng |
| PUT/DELETE | `/customers/{id}` | Sửa / xóa khách hàng |
| GET/POST | `/customers/{id}/history` | Lịch sử công nợ |
| PUT/DELETE | `/customers/{id}/history/{log_id}` | Sửa / xóa log công nợ |

### Đơn hàng
| Method | Path | Mô tả |
|--------|------|-------|
| GET | `/orders?page=&limit=` | Đơn đã hoàn thành (phân trang) |
| POST | `/checkout` | Tạo đơn trực tiếp (completed) |
| POST | `/checkout/draft` | Tạo đơn nháp (pending) |
| POST | `/checkout/desktop-dispatch` | Tạo đơn desktop → picker (approved) |
| PUT | `/orders/{id}` | Sửa đơn đã hoàn thành |
| DELETE | `/orders/{id}` | Xóa đơn (hoàn kho + công nợ) |
| PUT | `/orders/{id}/date` | Sửa ngày đơn |
| GET | `/orders/pending` | Đơn chờ duyệt |
| PUT | `/orders/{id}/approve` | Duyệt đơn (pending→approved) |
| DELETE | `/orders/{id}/reject` | Từ chối đơn (xóa) |
| DELETE | `/orders/{id}/cancel` | Hủy đơn (pending/approved/assigned) |
| GET | `/orders/approved` | Đơn đã duyệt chờ picker |
| GET | `/orders/accepted` | Alias cho /orders/approved |
| PUT | `/orders/{id}/receive` | Picker nhận đơn (approved→assigned) |
| GET | `/orders/assigned?picker_id=` | Đơn đã nhận của picker |
| PUT | `/orders/{id}/deliver` | Giao hàng (JSON photo path) |
| PUT | `/orders/{id}/deliver-with-photo` | Giao hàng (multipart upload ảnh) |
| PUT | `/orders/{id}/confirm` | Picker xác nhận (assigned→completed) |
| GET | `/orders/management` | Tất cả đơn cho manager |
| GET | `/orders/{id}/status` | Kiểm tra trạng thái nhẹ |

### Ảnh giao hàng
| Method | Path | Mô tả |
|--------|------|-------|
| GET | `/delivery-proofs/pending` | Đơn chưa sync ảnh về desktop |
| POST | `/delivery-proofs/ack-local` | Desktop xác nhận đã lưu local |
| GET | `/delivery-proofs/{name}` | Lấy file ảnh |

---

## Quy ước code

### Tên biến & cột DB
- **Tên biến và cột cơ sở dữ liệu dùng tiếng Việt** khi thêm mới
- Ví dụ: `tong_tien`, `ngay_tao`, `ten_khach`, `trang_thai`, `so_luong`
- Các cột hiện tại (English) giữ nguyên để tương thích production

### Python (backend)
- Business logic thuộc về `app/services/` — **không viết logic trong routers**
- Router chỉ: validate input → gọi service → trả response
- Không trả trực tiếp ORM object — luôn serialize thành dict hoặc Pydantic schema
- Dùng Vietnamese cho tên biến local khi xử lý domain objects (đơn hàng, khách hàng...)
- Tất cả đơn vị tiền tệ: **VND (integer, không dùng float)**

### Dart/Flutter (frontend)
- `ApiService` (`lib/services/api_service.dart`) là điểm duy nhất gọi HTTP
- Model classes ở `lib/models/` — thêm `.fromJson()` và `.toJson()`
- State management: `StatefulWidget + setState` cho local state; sẽ chuyển Riverpod khi refactor
- Vietnamese cho tên biến domain, English cho technical (controller, state, index...)

---

## Git workflow

```
main          ← protected, CI chạy khi push
  └── feature/ten-tinh-nang    (tính năng mới)
  └── fix/mo-ta-bug             (bug fix)
  └── chore/ten-cong-viec       (cấu hình, deps...)
```

### Commit message format
```
<type>(<scope>): <mô tả>

Types: feat | fix | chore | docs | test | refactor
Scope: backend | frontend | deploy | db

Ví dụ:
  feat(backend): thêm endpoint tìm kiếm sản phẩm theo khu vực
  fix(frontend): sửa lỗi hiển thị công nợ âm
  chore(deploy): cập nhật flutter version lên 3.41.4
```

### PR checklist
- [ ] Mô tả thay đổi và lý do
- [ ] Kiểm tra trên cả SQLite local và PostgreSQL
- [ ] Không commit file `.env`, `*.db`, `__pycache__`
- [ ] Test thủ công các luồng chính bị ảnh hưởng

---

## Deploy (Railway)

### Backend
- Build: Nixpacks (tự detect Python)
- Start: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- Config: `backend/railway.toml`
- Database: Railway PostgreSQL addon (auto-inject `DATABASE_URL`)

### Frontend
- Web: build → Docker + Nginx → Railway
- Windows: GitHub Actions build → artifact
- Android: GitHub Actions build → artifact
- iOS: GitHub Actions build (unsigned) → artifact

---

## Chạy tests

```bash
# Backend (khi có pytest setup)
cd backend && pytest

# Frontend
cd frontend && flutter test
```

---

## Kiến trúc backend mới (app/)

Đang chuyển dần từ monolith `api.py` → package `app/`:

```
backend/app/
├── main.py          FastAPI factory + middleware
├── database.py      Engine + Session + Base
├── config.py        Settings từ env vars
├── models/          SQLAlchemy ORM models
├── schemas/         Pydantic request/response
├── routers/         Route handlers (1 file = 1 domain)
│   ├── auth.py
│   ├── san_pham.py   (products)
│   ├── khu_vuc.py    (areas)
│   ├── khach_hang.py (customers)
│   ├── don_hang.py   (orders)
│   └── giao_hang.py  (delivery proofs)
├── services/        Business logic
└── utils.py         Helpers (_now_vn, _parse_paths...)
```

**Nguyên tắc kiến trúc:**
1. Router → nhận request, validate, gọi service
2. Service → business logic, không biết về HTTP
3. Model → ORM, không dùng trực tiếp trong response
4. Schema → Pydantic, định nghĩa interface input/output
