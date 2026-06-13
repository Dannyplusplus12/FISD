"""
Entry point cho Railway deployment.
Khởi tạo FastAPI app, cấu hình middleware, register routers, tạo bảng khi cần.
"""
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from .config import settings
from .database import engine, IS_SQLITE, Base

# Import models để Base.metadata biết về tất cả các bảng
from .models import SanPham, BienThe, KhuVuc, KhachHang, LichSuNo, NhanVien, DonHang, ChiTietDon  # noqa: F401

from .routers.nhan_vien import router as router_nhan_vien, auth_router as router_auth
from .routers.san_pham import router as router_san_pham, anh_router as router_anh_sp
from .routers.khach_hang import khu_vuc_router, khach_hang_router
from .routers.don_hang import router as router_don_hang, anh_router as router_anh_giao_hang


def _khoi_tao_db():
    """Tạo bảng và seed dữ liệu mặc định nếu chưa có."""
    Base.metadata.create_all(bind=engine)
    _migrate_them_cot(engine, IS_SQLITE)
    _seed_khu_vuc_va_nhan_vien(engine, IS_SQLITE)


def _migrate_them_cot(eng, is_sqlite: bool):
    """Thêm cột mới vào bảng hiện có nếu chưa tồn tại (tương thích dữ liệu cũ)."""
    try:
        with eng.connect() as conn:
            if is_sqlite:
                _sqlite_ensure_columns(conn)
            else:
                _postgres_ensure_columns(conn)
            conn.commit()
    except Exception as e:
        print(f"Warning: migration thêm cột thất bại — {e}")


def _sqlite_ensure_columns(conn):
    for table, col, col_type in [
        ("orders", "created_ts", "INTEGER"),
        ("debt_logs", "created_ts", "INTEGER"),
        ("orders", "is_draft", "INTEGER DEFAULT 0"),
        ("orders", "status", "VARCHAR DEFAULT 'completed'"),
        ("orders", "picker_note", "VARCHAR DEFAULT ''"),
        ("orders", "telegram_file_id", "VARCHAR DEFAULT ''"),
        ("orders", "telegram_message_id", "VARCHAR DEFAULT ''"),
        ("orders", "created_by_employee_id", "INTEGER"),
        ("orders", "assigned_picker_id", "INTEGER"),
        ("orders", "assigned_at", "TIMESTAMP"),
        ("orders", "delivered_by_id", "INTEGER"),
        ("orders", "delivered_at", "TIMESTAMP"),
        ("orders", "delivery_photo_path", "VARCHAR"),
        ("customers", "area_id", "INTEGER"),
        ("debt_logs", "actor_employee_id", "INTEGER"),
    ]:
        info = conn.execute(text(f"PRAGMA table_info('{table}')")).fetchall()
        cols = [r[1] for r in info]
        if col not in cols:
            conn.execute(text(f"ALTER TABLE {table} ADD COLUMN {col} {col_type}"))
    conn.execute(text("UPDATE orders SET status = 'pending' WHERE is_draft = 1 AND (status IS NULL OR status = 'completed')"))
    conn.execute(text("UPDATE orders SET status = 'completed' WHERE (is_draft = 0 OR is_draft IS NULL) AND status IS NULL"))
    conn.execute(text("UPDATE orders SET status = 'approved' WHERE status = 'accepted'"))


def _postgres_ensure_columns(conn):
    for table, col, col_type in [
        ("orders", "created_ts", "INTEGER"),
        ("debt_logs", "created_ts", "INTEGER"),
        ("orders", "is_draft", "INTEGER DEFAULT 0"),
        ("orders", "status", "VARCHAR DEFAULT 'completed'"),
        ("orders", "picker_note", "VARCHAR DEFAULT ''"),
        ("orders", "telegram_file_id", "VARCHAR DEFAULT ''"),
        ("orders", "telegram_message_id", "VARCHAR DEFAULT ''"),
        ("orders", "created_by_employee_id", "INTEGER"),
        ("orders", "assigned_picker_id", "INTEGER"),
        ("orders", "assigned_at", "TIMESTAMP"),
        ("orders", "delivered_by_id", "INTEGER"),
        ("orders", "delivered_at", "TIMESTAMP"),
        ("orders", "delivery_photo_path", "VARCHAR"),
        ("customers", "area_id", "INTEGER"),
        ("debt_logs", "actor_employee_id", "INTEGER"),
    ]:
        try:
            conn.execute(text(f"ALTER TABLE {table} ADD COLUMN IF NOT EXISTS {col} {col_type}"))
        except Exception:
            pass
    try:
        conn.execute(text("UPDATE orders SET status = 'pending' WHERE is_draft = 1 AND (status IS NULL OR status = 'completed')"))
        conn.execute(text("UPDATE orders SET status = 'approved' WHERE status = 'accepted'"))
    except Exception:
        pass


def _seed_khu_vuc_va_nhan_vien(eng, is_sqlite: bool):
    """Seed khu vực mặc định và nhân viên demo nếu bảng rỗng."""
    khu_vuc_mac_dinh = ["Chợ đêm", "Chợ hàn", "Hội An", "Nha Trang"]
    try:
        with eng.connect() as conn:
            if is_sqlite:
                conn.execute(text("CREATE TABLE IF NOT EXISTS areas (id INTEGER PRIMARY KEY, name VARCHAR UNIQUE)"))
                for ten in khu_vuc_mac_dinh:
                    conn.execute(text("INSERT OR IGNORE INTO areas (name) VALUES (:ten)"), {"ten": ten})
                conn.execute(text("INSERT OR IGNORE INTO employees (name, phone, role, pin, created_at) VALUES ('Orderer mặc định', '', 'orderer', '0000', CURRENT_TIMESTAMP)"))
                conn.execute(text("INSERT OR IGNORE INTO employees (name, phone, role, pin, created_at) VALUES ('Picker mặc định', '', 'picker', '1111', CURRENT_TIMESTAMP)"))
            else:
                conn.execute(text("CREATE TABLE IF NOT EXISTS areas (id SERIAL PRIMARY KEY, name VARCHAR UNIQUE)"))
                for ten in khu_vuc_mac_dinh:
                    conn.execute(text("INSERT INTO areas (name) VALUES (:ten) ON CONFLICT (name) DO NOTHING"), {"ten": ten})
                conn.execute(text("INSERT INTO employees (name, phone, role, pin) VALUES ('Orderer mặc định', '', 'orderer', '0000') ON CONFLICT (pin) DO NOTHING"))
                conn.execute(text("INSERT INTO employees (name, phone, role, pin) VALUES ('Picker mặc định', '', 'picker', '1111') ON CONFLICT (pin) DO NOTHING"))
            conn.commit()
    except Exception as e:
        print(f"Warning: seed thất bại — {e}")


def create_app() -> FastAPI:
    app = FastAPI(
        title="FISD API",
        version="2.0.0",
        description="Hệ thống quản lý bán hàng & kho FISD",
    )

    # CORS
    cors_raw = settings.CORS_ALLOWED_ORIGINS.strip()
    cors_origins = [x.strip() for x in cors_raw.split(",") if x.strip()]
    allow_all = not cors_origins or "*" in cors_origins
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"] if allow_all else cors_origins,
        allow_credentials=False if allow_all else True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Health check
    @app.get("/", tags=["System"])
    def root():
        return {"status": "ok", "app": "FISD API", "version": "2.0.0"}

    @app.get("/health", tags=["System"])
    def health():
        return {"status": "healthy"}

    # Routers
    app.include_router(router_auth)
    app.include_router(router_nhan_vien)
    app.include_router(router_san_pham)
    app.include_router(router_anh_sp)
    app.include_router(khu_vuc_router)
    app.include_router(khach_hang_router)
    app.include_router(router_don_hang)
    app.include_router(router_anh_giao_hang)

    # Khởi tạo DB khi app start
    try:
        _khoi_tao_db()
    except Exception as e:
        print(f"Warning: DB init thất bại — {e}")

    return app


app = create_app()
