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

# 2026-04-18 - PWA device layout detection fix
- Sửa logic chọn UI ở `frontend/lib/main.dart` để dùng `DeviceDetector.isMobileLayout(context)`.
- Bổ sung fallback nhận diện cho web trong `frontend/lib/utils/device_detector.dart`: nếu chạy PWA thì phân loại mobile/desktop theo độ rộng màn hình (`MediaQuery`), giúp hiển thị đúng UI trên điện thoại và desktop browser.

# 2026-04-18 - iPhone web/PWA detection hardening
- Cập nhật `frontend/lib/main.dart`: chọn màn hình bằng `Builder` bên trong `MaterialApp` để đảm bảo có `MediaQuery` hợp lệ khi quyết định mobile/desktop UI.
- Cập nhật `frontend/lib/utils/device_detector.dart`: trên web ưu tiên nhận diện `defaultTargetPlatform` (iOS/Android => mobile), sau đó fallback theo chiều rộng logical viewport.
- Cập nhật `frontend/web/index.html`: thêm meta `viewport` và `apple-mobile-web-app-capable` để Safari iPhone dùng đúng viewport mobile và cải thiện hành vi Add to Home Screen.

# 2026-04-18 - Safari delivery photo upload fix
- Sửa luồng ảnh giao hàng ở `frontend/lib/screens/mobile_home_screen.dart` để dùng `XFile` + `readAsBytes()` cho preview/thao tác chọn ảnh, tránh dùng `dart:io File` trong web Safari.
- Sửa API upload ở `frontend/lib/services/api_service.dart`: đổi `deliverOrder` sang nhận `List<XFile>` và gửi multipart bằng `MultipartFile.fromBytes` để tương thích web/iOS Safari.
- Kết quả mong đợi: không còn lỗi `Unsupported operation: _Namespace` khi chụp/chọn ảnh và gửi xác nhận giao đơn trên Safari.

# 2026-04-18 - iPhone install banner + branding
- Thêm banner hướng dẫn cài PWA trên mobile web trong `frontend/lib/main.dart`:
  - Nội dung: hướng dẫn Safari `Chia sẻ (□↑) -> Thêm vào Màn hình chính`.
  - Có 2 nút: `Đã hiểu` (ẩn tạm) và `Không nhắc lại` (lưu bằng `SharedPreferences`).
- Đồng bộ tên hiển thị web/PWA từ `fisd` thành `Fisd`:
  - `frontend/web/index.html` (`title`, `apple-mobile-web-app-title`, `description`)
  - `frontend/web/manifest.json` (`name`, `short_name`, `description`)
- Thay icon web/PWA từ `frontend/logo.png` cho các file:
  - `frontend/web/icons/Icon-192.png`
  - `frontend/web/icons/Icon-512.png`
  - `frontend/web/icons/Icon-maskable-192.png`
  - `frontend/web/icons/Icon-maskable-512.png`
  - `frontend/web/favicon.png`
