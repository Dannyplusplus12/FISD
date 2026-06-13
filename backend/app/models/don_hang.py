from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from ..database import Base
from ..utils import now_vn, now_vn_ts


class DonHang(Base):
    """Đơn hàng."""
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    customer_name = Column(String)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=True)
    created_at = Column(DateTime, default=now_vn)
    created_ts = Column(Integer, default=now_vn_ts)
    total_amount = Column(Integer)
    is_draft = Column(Integer, default=0)
    # trang_thai: 'pending' | 'approved' | 'assigned' | 'completed'
    status = Column(String, default="completed")
    picker_note = Column(String, default="")
    created_by_employee_id = Column(Integer, ForeignKey("employees.id"), nullable=True)
    assigned_picker_id = Column(Integer, ForeignKey("employees.id"), nullable=True)
    assigned_at = Column(DateTime, nullable=True)
    delivered_by_id = Column(Integer, ForeignKey("employees.id"), nullable=True)
    delivered_at = Column(DateTime, nullable=True)
    delivery_photo_path = Column(String, default="")
    telegram_file_id = Column(String, default="")
    telegram_message_id = Column(String, default="")

    chi_tiet = relationship("ChiTietDon", back_populates="don_hang")
    khach_hang = relationship("KhachHang", back_populates="don_hang")
    nguoi_tao = relationship(
        "NhanVien",
        foreign_keys=[created_by_employee_id],
        back_populates="don_hang_tao",
    )
    picker = relationship(
        "NhanVien",
        foreign_keys=[assigned_picker_id],
        back_populates="don_hang_nhan",
    )
    nguoi_giao = relationship(
        "NhanVien",
        foreign_keys=[delivered_by_id],
        back_populates="don_hang_giao",
    )


class ChiTietDon(Base):
    """Chi tiết dòng đơn hàng."""
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"))
    product_name = Column(String)
    variant_id = Column(Integer, ForeignKey("variants.id"), nullable=True)
    variant_info = Column(String)
    quantity = Column(Integer)
    price = Column(Integer)

    don_hang = relationship("DonHang", back_populates="chi_tiet")
