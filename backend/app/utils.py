import json
import os
from datetime import datetime, timezone, timedelta
from typing import Optional

VN_TZ = timezone(timedelta(hours=7))


def now_vn() -> datetime:
    return datetime.now(VN_TZ).replace(tzinfo=None)


def now_vn_ts() -> int:
    return int(datetime.now(VN_TZ).timestamp() * 1000)


def period_start_vn(so_ngay: int) -> Optional[datetime]:
    """Trả về thời điểm bắt đầu của khoảng `so_ngay` ngày gần nhất (theo múi giờ VN)."""
    if so_ngay <= 0:
        return None
    hien_tai = now_vn()
    dau_ngay = hien_tai.replace(hour=0, minute=0, second=0, microsecond=0)
    return dau_ngay - timedelta(days=max(0, so_ngay - 1))


def parse_duong_dan_anh(raw) -> list:
    """Chuẩn hóa trường delivery_photo_path thành list đường dẫn."""
    if raw is None:
        return []
    if isinstance(raw, list):
        return [str(x).strip() for x in raw if str(x).strip()]
    if isinstance(raw, str):
        t = raw.strip()
        if not t:
            return []
        if t.startswith("["):
            try:
                data = json.loads(t)
                if isinstance(data, list):
                    return [str(x).strip() for x in data if str(x).strip()]
            except Exception:
                pass
        if "|" in t:
            return [p.strip() for p in t.split("|") if p.strip()]
        return [t]
    return [str(raw).strip()]


def trang_thai_don_vi(trang_thai: str) -> str:
    s = (trang_thai or "").strip().lower()
    mapping = {
        "pending": "Đợi duyệt",
        "approved": "Đã duyệt",
        "assigned": "Đã nhận",
        "accepted": "Đã nhận",
        "completed": "Hoàn thành",
    }
    return mapping.get(s, (trang_thai or "").upper())


def safe_basename(ten_file: str) -> str:
    """Trả về os.path.basename và kiểm tra path traversal."""
    safe = os.path.basename(ten_file)
    if safe != ten_file:
        raise ValueError("Tên file không hợp lệ")
    return safe
