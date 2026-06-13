from pydantic import BaseModel
from typing import List, Optional


class MatHangGio(BaseModel):
    variant_id: int
    quantity: int
    price: int
    product_name: str
    color: str
    size: str

    def to_json(self):
        return {
            "variant_id": self.variant_id,
            "quantity": self.quantity,
            "price": self.price,
            "product_name": self.product_name,
            "color": self.color,
            "size": self.size,
        }


class YeuCauThanhToan(BaseModel):
    customer_name: str
    customer_phone: str = ""
    employee_id: Optional[int] = None
    cart: List[MatHangGio]


class CapNhatNgayDon(BaseModel):
    created_at: str  # YYYY-MM-DD HH:MM


class XacNhanGiaoItem(BaseModel):
    order_item_id: Optional[int] = None
    variant_id: Optional[int] = None
    picked_qty: int = 0


class YeuCauXacNhanGiao(BaseModel):
    items: List[XacNhanGiaoItem] = []


class YeuCauNhanDon(BaseModel):
    picker_id: int


class YeuCauGiaoHang(BaseModel):
    picker_id: int
    photo_path: str
    items: List[XacNhanGiaoItem] = []
    picker_note: str = ""


class XacNhanLocalAnh(BaseModel):
    order_id: int
    local_file_names: List[str] = []
