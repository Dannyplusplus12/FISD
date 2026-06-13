from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from ..database import Base
from ..utils import now_vn, now_vn_ts


class KhuVuc(Base):
    """Khu vực địa lý của khách hàng."""
    __tablename__ = "areas"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)

    khach_hang = relationship("KhachHang", back_populates="khu_vuc")


class KhachHang(Base):
    """Khách hàng."""
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, unique=True)
    phone = Column(String, default="")
    debt = Column(Integer, default=0)
    area_id = Column(Integer, ForeignKey("areas.id"), nullable=True)

    khu_vuc = relationship("KhuVuc", back_populates="khach_hang")
    lich_su_no = relationship("LichSuNo", back_populates="khach_hang", cascade="all, delete-orphan")
    don_hang = relationship("DonHang", back_populates="khach_hang")


class LichSuNo(Base):
    """Lịch sử thay đổi công nợ của khách hàng."""
    __tablename__ = "debt_logs"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"))
    actor_employee_id = Column(Integer, ForeignKey("employees.id"), nullable=True)
    change_amount = Column(Integer)
    new_balance = Column(Integer)
    note = Column(String)
    created_at = Column(DateTime, default=now_vn)
    created_ts = Column(Integer, default=now_vn_ts)

    khach_hang = relationship("KhachHang", back_populates="lich_su_no")
