from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from ..database import Base
from ..utils import now_vn


class NhanVien(Base):
    """Nhân viên (orderer / picker / manager)."""
    __tablename__ = "employees"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    phone = Column(String, default="")
    email = Column(String, default="")
    address = Column(String, default="")
    notes = Column(String, default="")
    role = Column(String, index=True)
    pin = Column(String, unique=True, index=True)
    is_active = Column(Integer, default=1)
    created_at = Column(DateTime, default=now_vn)

    don_hang_tao = relationship(
        "DonHang",
        foreign_keys="DonHang.created_by_employee_id",
        back_populates="nguoi_tao",
    )
    don_hang_nhan = relationship(
        "DonHang",
        foreign_keys="DonHang.assigned_picker_id",
        back_populates="picker",
    )
    don_hang_giao = relationship(
        "DonHang",
        foreign_keys="DonHang.delivered_by_id",
        back_populates="nguoi_giao",
    )
