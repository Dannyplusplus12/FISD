from pydantic import BaseModel
from typing import List, Optional


class BienTheInput(BaseModel):
    id: Optional[int] = None
    color: str
    size: str
    price: int
    stock: int


class TaoSanPham(BaseModel):
    code: str = ""
    name: str
    description: str = ""
    image_path: str
    variants: List[BienTheInput]


class CapNhatSanPham(BaseModel):
    code: str = ""
    name: str
    image_path: str
    variants: List[BienTheInput]
