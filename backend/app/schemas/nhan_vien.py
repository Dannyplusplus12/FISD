from pydantic import BaseModel
from typing import Optional


class TaoNhanVien(BaseModel):
    name: str
    phone: str = ""
    email: str = ""
    address: str = ""
    notes: str = ""
    role: str


class CapNhatNhanVien(BaseModel):
    name: str
    phone: str = ""
    email: str = ""
    address: str = ""
    notes: str = ""
    role: str
    pin: Optional[str] = None
    is_active: int = 1


class DangNhapPin(BaseModel):
    pin: str
    requested_role: str
