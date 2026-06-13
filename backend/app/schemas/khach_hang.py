from pydantic import BaseModel
from typing import Optional


class TaoKhuVuc(BaseModel):
    name: str


class CapNhatKhuVuc(BaseModel):
    name: str


class TaoKhachHang(BaseModel):
    name: str
    phone: str = ""
    debt: int = 0
    area_id: int


class CapNhatKhachHang(BaseModel):
    name: str
    phone: str
    debt: int
    area_id: int


class TaoLichSuNo(BaseModel):
    change_amount: int
    note: str = ""
    created_at: Optional[str] = None  # định dạng: YYYY-MM-DD HH:MM
    actor_employee_id: Optional[int] = None


class CapNhatLichSuNo(BaseModel):
    change_amount: int
    note: str = ""
    created_at: Optional[str] = None
