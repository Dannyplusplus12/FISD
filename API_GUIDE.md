# FISD API Guide — Hướng dẫn sử dụng API

> Dành cho frontend developer. Tất cả request/response đều là JSON.
> Base URL production: *(xem config.json trong frontend)*
> Base URL local: `http://localhost:8000`

---

## Quy ước chung

- **Content-Type:** `application/json` cho tất cả request có body
- **Tiền tố URL:** Không có `/api/v1` — endpoint trực tiếp từ root, ví dụ: `GET /products`
- **Mã lỗi:**
  - `400` — Dữ liệu không hợp lệ (thiếu trường, sai định dạng)
  - `401` — Chưa xác thực (PIN sai)
  - `403` — Không có quyền
  - `404` — Không tìm thấy
  - `500` — Lỗi server
- **Body lỗi:** `{ "detail": "Mô tả lỗi bằng tiếng Việt" }`
- **Tiền tệ:** Tất cả số tiền là **VND (integer)**, không dùng float
- **Thời gian:** Định dạng `"YYYY-MM-DD HH:MM"` (VD: `"2026-06-13 14:30"`)

---

## 1. Auth — Đăng nhập

### POST `/auth/pin-login`
Đăng nhập bằng PIN số. Mỗi nhân viên có 1 PIN 4-8 chữ số và 1 vai trò cố định.

**Request body:**
```json
{
  "pin": "1234",
  "requested_role": "orderer"
}
```

| Trường | Kiểu | Mô tả |
|--------|------|-------|
| `pin` | string | Mã PIN 4-8 chữ số |
| `requested_role` | string | Vai trò muốn đăng nhập: `"orderer"` \| `"picker"` \| `"manager"` |

**Response thành công (200):**
```json
{
  "id": 1,
  "name": "Nguyễn Văn A",
  "phone": "0909123456",
  "role": "orderer"
}
```

**Lưu ý:** Lưu `id` vào local storage để dùng cho các request tiếp theo (tạo đơn, nhận đơn...).

---

## 2. Nhân viên

### GET `/employees`
Lấy danh sách toàn bộ nhân viên.

**Response:** Array of employee objects:
```json
[
  {
    "id": 1,
    "name": "Nguyễn Văn A",
    "phone": "0909123456",
    "email": "",
    "address": "",
    "notes": "",
    "role": "orderer",
    "pin": "1234",
    "is_active": 1,
    "created_at": "2026-01-01 08:00",
    "delivered_count": 0,
    "last_delivered_at": ""
  }
]
```

### POST `/employees`
Tạo nhân viên mới (PIN được tự động tạo ngẫu nhiên).

**Request body:**
```json
{
  "name": "Trần Thị B",
  "phone": "0901234567",
  "email": "",
  "address": "",
  "notes": "",
  "role": "picker"
}
```

**Response:** `{ "status": "created", "id": 2, "pin": "5678", "employee": {...} }`

### PUT `/employees/{id}`
Cập nhật thông tin nhân viên.

**Request body:** Tương tự tạo mới, thêm trường `pin` (optional) và `is_active` (0 hoặc 1).

### DELETE `/employees/{id}`
Xóa nhân viên.

### GET `/employees/{id}/deliveries?q=&days=0&limit=200`
Lịch sử đơn đã giao của nhân viên.

| Query param | Mô tả |
|-------------|-------|
| `q` | Tìm theo tên khách hoặc mã đơn |
| `days` | Số ngày gần nhất (0 = tất cả) |
| `limit` | Số kết quả tối đa (max 500) |

### GET `/employees/{id}/activities?q=&days=0&limit=300`
Lịch sử tất cả hoạt động: đơn hàng tạo + log công nợ.

**Response:** `{ "employee": {...}, "data": [...], "count": N }`

Mỗi item trong `data` có `"type": "ORDER"` hoặc `"type": "DEBT_LOG"`.

---

## 3. Sản phẩm

### GET `/products?search=`
Lấy danh sách sản phẩm. Tìm theo tên hoặc mã sản phẩm.

**Response:**
```json
[
  {
    "id": 1,
    "code": "SP001",
    "name": "Áo thun trắng",
    "image": "/product-images/product_xxx.jpg",
    "price_range": "150,000 - 200,000",
    "variants": [
      { "id": 10, "color": "Trắng", "size": "M", "price": 150000, "stock": 20 },
      { "id": 11, "color": "Trắng", "size": "L", "price": 200000, "stock": 15 }
    ]
  }
]
```

### POST `/products`
Tạo sản phẩm mới.

**Request body:**
```json
{
  "code": "SP001",
  "name": "Áo thun trắng",
  "description": "",
  "image_path": "/product-images/product_xxx.jpg",
  "variants": [
    { "color": "Trắng", "size": "M", "price": 150000, "stock": 20 }
  ]
}
```

### PUT `/products/{id}`
Cập nhật sản phẩm và danh sách biến thể.

**Request body:**
```json
{
  "code": "SP001",
  "name": "Áo thun trắng (mới)",
  "image_path": "/product-images/product_yyy.jpg",
  "variants": [
    { "id": 10, "color": "Trắng", "size": "M", "price": 160000, "stock": 18 },
    { "color": "Đen", "size": "M", "price": 160000, "stock": 10 }
  ]
}
```

> Biến thể có `id` → cập nhật. Biến thể không có `id` → tạo mới. Biến thể cũ không có trong list → bị xóa.

### DELETE `/products/{id}`
Xóa sản phẩm và tất cả biến thể.

### POST `/product-images/upload`
Upload ảnh sản phẩm (multipart form, field tên là `file`).

**Response:** `{ "path": "/product-images/product_xxx.jpg" }`

### GET `/product-images/{filename}`
Lấy file ảnh sản phẩm.

---

## 4. Khu vực

### GET `/areas`
Danh sách khu vực kèm số khách hàng và tổng nợ.

**Response:**
```json
[
  { "id": 1, "name": "Chợ hàn", "customer_count": 15, "total_debt": 5000000 }
]
```

### POST `/areas`
Tạo khu vực: `{ "name": "Tên khu vực" }`

### PUT `/areas/{id}`
Đổi tên khu vực: `{ "name": "Tên mới" }`

### DELETE `/areas/{id}`
Xóa khu vực. Khách hàng trong khu vực bị chuyển sang khu vực khác.

---

## 5. Khách hàng

### GET `/customers`
Danh sách khách hàng kèm công nợ và khu vực.

**Response:**
```json
[
  {
    "id": 1,
    "name": "Nguyễn Thị C",
    "phone": "0911222333",
    "debt": 1500000,
    "area_id": 2,
    "area_name": "Chợ đêm"
  }
]
```

`debt` > 0 = khách đang nợ. `debt` < 0 = khách trả dư.

### POST `/customers`
Tạo khách hàng mới.

**Request body:**
```json
{
  "name": "Nguyễn Thị C",
  "phone": "0911222333",
  "debt": 0,
  "area_id": 2
}
```

### PUT `/customers/{id}`
Cập nhật thông tin khách hàng (name, phone, debt, area_id).

### DELETE `/customers/{id}`
Xóa khách hàng và toàn bộ lịch sử đơn hàng liên quan.

### GET `/customers/{id}/history`
Lịch sử giao dịch của khách (đơn hàng + log công nợ), sắp xếp mới nhất lên đầu.

**Response item loại ORDER:**
```json
{
  "type": "ORDER",
  "date": "2026-06-10 14:30",
  "sort_ts": 1749524200000,
  "desc": "Xuất đơn hàng #42",
  "amount": 350000,
  "data": {
    "id": 42, "customer": "Nguyễn Thị C",
    "total_money": 350000, "total_qty": 3,
    "items": [...]
  }
}
```

**Response item loại LOG:**
```json
{
  "type": "LOG",
  "date": "2026-06-11 09:00",
  "sort_ts": 1749610200000,
  "desc": "Trả nợ",
  "amount": -200000,
  "data": null,
  "log_id": 15
}
```

### POST `/customers/{id}/history`
Thêm log thủ công vào công nợ (thu tiền / điều chỉnh).

**Request body:**
```json
{
  "change_amount": -200000,
  "note": "Trả tiền mặt",
  "created_at": "2026-06-11 09:00",
  "actor_employee_id": 3
}
```

> `change_amount` âm = thu tiền (giảm nợ). Dương = tăng nợ (ít dùng thủ công).

### PUT `/customers/{id}/history/{log_id}`
Sửa log công nợ: `{ "change_amount": -250000, "note": "Sửa lại", "created_at": "2026-06-11 09:00" }`

### DELETE `/customers/{id}/history/{log_id}`
Xóa log công nợ (tự động điều chỉnh lại tổng nợ).

---

## 6. Đơn hàng

### Trạng thái đơn hàng

```
pending → approved → assigned → completed
            ↑ (desktop dispatch bỏ qua pending)
```

| Trạng thái | Ý nghĩa |
|-----------|---------|
| `pending` | Orderer tạo, chờ staff duyệt |
| `approved` | Staff đã duyệt, picker có thể nhận |
| `assigned` | Picker đã nhận, đang chuẩn bị giao |
| `completed` | Đã giao xong, công nợ đã cộng |

---

### GET `/orders?page=1&limit=20`
Đơn hàng đã hoàn thành, phân trang.

**Response:**
```json
{
  "data": [...],
  "total": 150,
  "page": 1,
  "limit": 20
}
```

### POST `/checkout`
Tạo đơn hàng trực tiếp (completed ngay, trừ kho và cộng nợ ngay).

**Request body:**
```json
{
  "customer_name": "Nguyễn Thị C",
  "customer_phone": "",
  "employee_id": 1,
  "cart": [
    {
      "variant_id": 10,
      "quantity": 2,
      "price": 150000,
      "product_name": "Áo thun trắng",
      "color": "Trắng",
      "size": "M"
    }
  ]
}
```

### POST `/checkout/draft`
Tạo đơn nháp (pending) từ app mobile orderer. Chưa trừ kho, chưa cộng nợ.

**Request body:** Giống `/checkout`

**Response:** `{ "status": "success", "order_id": 43, "message": "..." }`

### POST `/checkout/desktop-dispatch`
Tạo đơn từ desktop, gửi thẳng picker (approved). Trừ kho ngay, chưa cộng nợ.

**Request body:** Giống `/checkout`

### PUT `/orders/{id}`
Sửa đơn đã hoàn thành (chỉ được sửa đơn `completed`).

**Request body:** Giống `/checkout`

### DELETE `/orders/{id}`
Xóa đơn đã hoàn thành (hoàn kho + trừ nợ).

### PUT `/orders/{id}/date`
Sửa ngày giờ đơn hàng.

**Request body:** `{ "created_at": "2026-06-10 14:00" }`

---

### Luồng Orderer → Staff

### GET `/orders/pending`
Danh sách đơn chờ duyệt (cho màn hình manager/staff).

**Response item:**
```json
{
  "id": 43,
  "created_at": "2026-06-13 10:30",
  "customer_name": "Nguyễn Thị C",
  "total_amount": 300000,
  "total_qty": 2,
  "status": "pending",
  "created_by_employee_name": "Nguyễn Văn A",
  "has_stock_conflict": false,
  "items": [
    {
      "order_item_id": 55,
      "product_name": "Áo thun",
      "variant_id": 10,
      "variant_info": "Trắng-M",
      "quantity": 2,
      "price": 150000,
      "current_stock": 18,
      "enough_stock": true
    }
  ]
}
```

### PUT `/orders/{id}/approve`
Staff duyệt đơn (pending → approved). Trừ kho ngay lúc duyệt.

### DELETE `/orders/{id}/reject`
Staff từ chối đơn (xóa hẳn, không hoàn tác gì vì kho chưa trừ).

### DELETE `/orders/{id}/cancel`
Hủy đơn ở bất kỳ trạng thái nào (ngoài completed). Hoàn kho nếu đã trừ.

---

### Luồng Picker

### GET `/orders/approved`
Đơn đã duyệt, picker có thể nhận.

### PUT `/orders/{id}/receive`
Picker nhận đơn (approved → assigned).

**Request body:** `{ "picker_id": 2 }`

### GET `/orders/assigned?picker_id=2`
Đơn picker đang giữ.

### PUT `/orders/{id}/deliver-with-photo`
Picker xác nhận giao hàng kèm ảnh chụp (multipart form).

| Form field | Kiểu | Mô tả |
|-----------|------|-------|
| `picker_id` | integer | ID của picker |
| `photo` / `photos` | file | 1 hoặc nhiều ảnh giao hàng |
| `items_json` | string | JSON array xác nhận số lượng thực giao (optional) |
| `picker_note` | string | Ghi chú nếu thiếu hàng (optional) |

**`items_json` format:**
```json
[
  { "order_item_id": 55, "picked_qty": 2 }
]
```

Nếu không gửi `items_json`, hệ thống tự đánh dấu full quantity.

### PUT `/orders/{id}/confirm`
Picker xác nhận giao (không cần ảnh, dùng cho desktop). Body optional:

```json
{
  "items": [
    { "order_item_id": 55, "picked_qty": 2 }
  ]
}
```

### GET `/orders/management?limit=200`
Tất cả đơn hàng cho màn hình manager.

### GET `/orders/{id}/status`
Kiểm tra nhanh trạng thái đơn. Trả về `404` nếu đơn bị xóa/từ chối.

---

## 7. Ảnh giao hàng (Desktop sync)

### GET `/delivery-proofs/pending?since_order_id=0&limit=200`
Danh sách đơn có ảnh giao hàng chưa được tải về desktop.

### POST `/delivery-proofs/ack-local`
Desktop xác nhận đã lưu ảnh local (server sẽ xóa file tạm).

**Request body:**
```json
{
  "order_id": 43,
  "local_file_names": ["order_43_20260613143000_abc12345.jpg"]
}
```

### GET `/delivery-proofs/{filename}`
Tải file ảnh giao hàng từ server.

---

## Ví dụ code Flutter

```dart
// Đăng nhập
final response = await http.post(
  Uri.parse('$baseUrl/auth/pin-login'),
  headers: {'Content-Type': 'application/json'},
  body: jsonEncode({'pin': '1234', 'requested_role': 'orderer'}),
);
final employee = jsonDecode(response.body);
final employeeId = employee['id'];

// Lấy sản phẩm
final productsRes = await http.get(Uri.parse('$baseUrl/products'));
final products = jsonDecode(utf8.decode(productsRes.bodyBytes)) as List;

// Tạo đơn nháp (mobile orderer)
final checkoutRes = await http.post(
  Uri.parse('$baseUrl/checkout/draft'),
  headers: {'Content-Type': 'application/json'},
  body: jsonEncode({
    'customer_name': 'Nguyễn Thị C',
    'customer_phone': '',
    'employee_id': employeeId,
    'cart': [
      {
        'variant_id': 10,
        'quantity': 2,
        'price': 150000,
        'product_name': 'Áo thun',
        'color': 'Trắng',
        'size': 'M',
      }
    ],
  }),
);

// Upload ảnh giao hàng (picker)
final request = http.MultipartRequest(
  'PUT',
  Uri.parse('$baseUrl/orders/43/deliver-with-photo'),
);
request.fields['picker_id'] = '2';
request.fields['picker_note'] = '';
request.fields['items_json'] = '[]';
request.files.add(await http.MultipartFile.fromPath('photo', '/path/to/photo.jpg'));
final streamedResponse = await request.send();
```
