from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import desc, func
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import KhuVuc, KhachHang, LichSuNo, DonHang, ChiTietDon
from ..schemas.khach_hang import TaoKhuVuc, CapNhatKhuVuc, TaoKhachHang, CapNhatKhachHang, TaoLichSuNo, CapNhatLichSuNo
from ..utils import now_vn, now_vn_ts, parse_duong_dan_anh

router = APIRouter(tags=["Khách hàng"])


def _lay_khu_vuc_mac_dinh(db: Session):
    kv = db.query(KhuVuc).filter(KhuVuc.name == "Chợ hàn").first()
    if kv:
        return kv.id
    kv_dau = db.query(KhuVuc).order_by(KhuVuc.id).first()
    return kv_dau.id if kv_dau else None


# ─── Khu vực ───

khu_vuc_router = APIRouter(prefix="/areas", tags=["Khu vực"])


@khu_vuc_router.get("")
def lay_danh_sach_khu_vuc(db: Session = Depends(get_db)):
    khu_vuc = db.query(KhuVuc).order_by(KhuVuc.id).all()
    ket_qua = []
    for kv in khu_vuc:
        khach = db.query(KhachHang).filter(KhachHang.area_id == kv.id).all()
        ket_qua.append({
            "id": kv.id, "name": kv.name,
            "customer_count": len(khach),
            "total_debt": sum(int(kh.debt or 0) for kh in khach),
        })
    return ket_qua


@khu_vuc_router.post("")
def tao_khu_vuc(data: TaoKhuVuc, db: Session = Depends(get_db)):
    ten = data.name.strip()
    if not ten:
        raise HTTPException(status_code=400, detail="Tên khu vực không hợp lệ")
    if db.query(KhuVuc).filter(func.lower(KhuVuc.name) == func.lower(ten)).first():
        raise HTTPException(status_code=400, detail="Khu vực đã tồn tại")
    kv = KhuVuc(name=ten)
    db.add(kv)
    db.commit()
    db.refresh(kv)
    return {"status": "created", "id": kv.id}


@khu_vuc_router.put("/{kv_id}")
def cap_nhat_khu_vuc(kv_id: int, data: CapNhatKhuVuc, db: Session = Depends(get_db)):
    kv = db.query(KhuVuc).filter(KhuVuc.id == kv_id).first()
    if not kv:
        raise HTTPException(status_code=404, detail="Khu vực không tồn tại")
    ten = data.name.strip()
    if not ten:
        raise HTTPException(status_code=400, detail="Tên khu vực không hợp lệ")
    if db.query(KhuVuc).filter(func.lower(KhuVuc.name) == func.lower(ten), KhuVuc.id != kv_id).first():
        raise HTTPException(status_code=400, detail="Tên khu vực đã tồn tại")
    kv.name = ten
    db.commit()
    return {"status": "updated"}


@khu_vuc_router.delete("/{kv_id}")
def xoa_khu_vuc(kv_id: int, db: Session = Depends(get_db)):
    kv = db.query(KhuVuc).filter(KhuVuc.id == kv_id).first()
    if not kv:
        raise HTTPException(status_code=404, detail="Khu vực không tồn tại")
    kv_dich = _lay_khu_vuc_mac_dinh(db)
    if kv_dich == kv_id:
        du_phong = db.query(KhuVuc).filter(KhuVuc.id != kv_id).order_by(KhuVuc.id).first()
        kv_dich = du_phong.id if du_phong else None
    if kv_dich is None:
        raise HTTPException(status_code=400, detail="Không thể xóa khu vực duy nhất")
    db.query(KhachHang).filter(KhachHang.area_id == kv_id).update({KhachHang.area_id: kv_dich})
    db.delete(kv)
    db.commit()
    return {"status": "deleted", "moved_to_area_id": kv_dich}


# ─── Khách hàng ───

khach_hang_router = APIRouter(prefix="/customers", tags=["Khách hàng"])


@khach_hang_router.get("")
def lay_danh_sach_khach(db: Session = Depends(get_db)):
    khach = db.query(KhachHang).order_by(desc(KhachHang.id)).all()
    return [{
        "id": kh.id, "name": kh.name, "phone": kh.phone, "debt": kh.debt,
        "area_id": kh.area_id, "area_name": (kh.khu_vuc.name if kh.khu_vuc else ""),
    } for kh in khach]


@khach_hang_router.post("")
def tao_khach_hang(data: TaoKhachHang, db: Session = Depends(get_db)):
    try:
        if db.query(KhachHang).filter(KhachHang.name == data.name).first():
            raise HTTPException(status_code=400, detail="Tên đã tồn tại!")
        if not db.query(KhuVuc).filter(KhuVuc.id == data.area_id).first():
            raise HTTPException(status_code=400, detail="Khu vực không tồn tại")
        kh = KhachHang(name=data.name, phone=data.phone, debt=data.debt, area_id=data.area_id)
        db.add(kh)
        db.flush()
        if data.debt != 0:
            db.add(LichSuNo(customer_id=kh.id, change_amount=data.debt, new_balance=data.debt, note="Khởi tạo thủ công", created_ts=now_vn_ts()))
        db.commit()
        db.refresh(kh)
        return {"status": "created", "id": kh.id}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@khach_hang_router.put("/{kh_id}")
def cap_nhat_khach_hang(kh_id: int, data: CapNhatKhachHang, db: Session = Depends(get_db)):
    kh = db.query(KhachHang).filter(KhachHang.id == kh_id).first()
    if not kh:
        raise HTTPException(status_code=404)
    if not db.query(KhuVuc).filter(KhuVuc.id == data.area_id).first():
        raise HTTPException(status_code=400, detail="Khu vực không tồn tại")
    chenh_lech = data.debt - kh.debt
    kh.name, kh.phone, kh.debt, kh.area_id = data.name, data.phone, data.debt, data.area_id
    if chenh_lech != 0:
        db.add(LichSuNo(customer_id=kh.id, change_amount=chenh_lech, new_balance=kh.debt, note="Điều chỉnh thủ công", created_ts=now_vn_ts()))
    db.commit()
    return {"status": "ok"}


@khach_hang_router.delete("/{kh_id}")
def xoa_khach_hang(kh_id: int, db: Session = Depends(get_db)):
    kh = db.query(KhachHang).filter(KhachHang.id == kh_id).first()
    if not kh:
        raise HTTPException(status_code=404, detail="Khách hàng không tồn tại")
    try:
        don_hang_list = db.query(DonHang).filter(DonHang.customer_id == kh_id).all()
        for don in don_hang_list:
            _xoa_don_voi_logic(don, db)
        db.delete(kh)
        db.commit()
        return {"detail": "Đã xóa khách hàng và toàn bộ lịch sử đơn hàng liên quan"}
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


def _xoa_don_voi_logic(don: DonHang, db: Session):
    """Xóa đơn và hoàn tác kho + công nợ tương ứng."""
    from ..models import BienThe
    if don.status in ("completed", "approved", "assigned"):
        for ct in don.chi_tiet:
            if ct.variant_id:
                bt = db.query(BienThe).filter(BienThe.id == ct.variant_id).first()
                if bt:
                    bt.stock = (bt.stock or 0) + (ct.quantity or 0)
        if don.status == "completed" and don.customer_id:
            kh = db.query(KhachHang).filter(KhachHang.id == don.customer_id).first()
            if kh and don.total_amount:
                kh.debt = (kh.debt or 0) - int(don.total_amount or 0)
    db.query(ChiTietDon).filter(ChiTietDon.order_id == don.id).delete()
    db.delete(don)


@khach_hang_router.get("/{kh_id}/history")
def lich_su_khach_hang(kh_id: int, db: Session = Depends(get_db)):
    don_hang = db.query(DonHang).filter(DonHang.customer_id == kh_id).all()
    lich_su = []
    for don in don_hang:
        ts = int(don.created_ts) if (hasattr(don, "created_ts") and don.created_ts) else int(don.created_at.timestamp() * 1000)
        ct_list = [{"product_name": ct.product_name, "variant_id": ct.variant_id, "variant_info": ct.variant_info, "quantity": ct.quantity, "price": ct.price} for ct in don.chi_tiet]
        lich_su.append({
            "type": "ORDER", "date": don.created_at.strftime("%Y-%m-%d %H:%M"), "sort_ts": ts,
            "desc": f"Xuất đơn hàng #{don.id}", "amount": don.total_amount,
            "data": {
                "id": don.id, "customer": don.customer_name, "customer_name": don.customer_name,
                "date": don.created_at.strftime("%d/%m %H:%M"), "total_money": don.total_amount,
                "total_qty": sum(ct.quantity for ct in don.chi_tiet),
                "delivery_photo_path": (don.delivery_photo_path or ""),
                "delivery_photo_paths": parse_duong_dan_anh(don.delivery_photo_path),
                "items": ct_list,
            },
        })
    no_list = db.query(LichSuNo).filter(LichSuNo.customer_id == kh_id).all()
    for log in no_list:
        ts_log = int(log.created_ts) if (hasattr(log, "created_ts") and log.created_ts) else int(log.created_at.timestamp() * 1000)
        lich_su.append({
            "type": "LOG", "date": log.created_at.strftime("%Y-%m-%d %H:%M"), "sort_ts": ts_log,
            "desc": log.note, "amount": log.change_amount, "data": None, "log_id": log.id,
        })
    return sorted(lich_su, key=lambda x: x["sort_ts"], reverse=True)


@khach_hang_router.post("/{kh_id}/history")
def tao_lich_su_no(kh_id: int, data: TaoLichSuNo, db: Session = Depends(get_db)):
    kh = db.query(KhachHang).filter(KhachHang.id == kh_id).first()
    if not kh:
        raise HTTPException(status_code=404, detail="Khách hàng không tồn tại")
    try:
        if data.actor_employee_id is not None:
            from ..models import NhanVien
            if not db.query(NhanVien).filter(NhanVien.id == data.actor_employee_id).first():
                raise HTTPException(status_code=400, detail="Nhân viên thực hiện không tồn tại")
        hien_tai = now_vn()
        ngay_hien_thi = hien_tai
        if data.created_at:
            try:
                ngay_hien_thi = datetime.strptime(data.created_at, "%Y-%m-%d %H:%M")
            except Exception:
                pass
        kh.debt += data.change_amount
        db.add(LichSuNo(
            customer_id=kh.id, actor_employee_id=data.actor_employee_id,
            change_amount=data.change_amount, new_balance=kh.debt, note=data.note,
            created_at=ngay_hien_thi, created_ts=int(hien_tai.timestamp() * 1000),
        ))
        db.commit()
        return {"status": "created"}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@khach_hang_router.put("/{kh_id}/history/{log_id}")
def cap_nhat_lich_su_no(kh_id: int, log_id: int, data: CapNhatLichSuNo, db: Session = Depends(get_db)):
    kh = db.query(KhachHang).filter(KhachHang.id == kh_id).first()
    if not kh:
        raise HTTPException(status_code=404, detail="Khách hàng không tồn tại")
    log = db.query(LichSuNo).filter(LichSuNo.id == log_id, LichSuNo.customer_id == kh_id).first()
    if not log:
        raise HTTPException(status_code=404, detail="Log không tồn tại")
    try:
        chenh_lech = data.change_amount - log.change_amount
        kh.debt += chenh_lech
        log.change_amount, log.note, log.new_balance = data.change_amount, data.note, kh.debt
        if data.created_at:
            ngay_moi = datetime.strptime(data.created_at, "%Y-%m-%d %H:%M")
            log.created_at, log.created_ts = ngay_moi, int(ngay_moi.timestamp() * 1000)
        db.commit()
        return {"status": "updated"}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@khach_hang_router.delete("/{kh_id}/history/{log_id}")
def xoa_lich_su_no(kh_id: int, log_id: int, db: Session = Depends(get_db)):
    kh = db.query(KhachHang).filter(KhachHang.id == kh_id).first()
    if not kh:
        raise HTTPException(status_code=404, detail="Khách hàng không tồn tại")
    log = db.query(LichSuNo).filter(LichSuNo.id == log_id, LichSuNo.customer_id == kh_id).first()
    if not log:
        raise HTTPException(status_code=404, detail="Log không tồn tại")
    try:
        kh.debt -= log.change_amount
        db.delete(log)
        db.commit()
        return {"status": "deleted"}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
