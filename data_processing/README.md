# Data Processing

Thư mục này chứa hai notebook xử lý dữ liệu theo thứ tự pipeline rõ ràng.

```text
data_processing/
├── clean_raw.ipynb
├── prepare_final.ipynb
└── README.md
```

## Clean Raw

`clean_raw.ipynb`

- Input: `data_csv/zillow_full_raw.csv`
- Output: `data_csv/zillow_clean.csv`
- Vai trò: chọn các cột cần thiết từ dữ liệu raw/enriched, chuẩn hóa đơn vị diện tích đất, tính tỷ lệ cơ bản và đổi tên cột về dạng ngắn gọn.

## Prepare Final

`prepare_final.ipynb`

- Input: `data_csv/zillow_clean.csv`
- Output: `data_csv/zillow_final.csv`
- Vai trò: lọc dòng không hợp lệ, xử lý missing values bằng median, bỏ loại nhà đất trống, tính lại `bed_bath` và `lot_living`, loại 5% giá cao nhất để giảm ảnh hưởng outlier cực đoan.

## Ghi Chú

Tên notebook được đặt ngắn gọn nhưng vẫn nói rõ vai trò: một file làm sạch dữ liệu raw, một file chuẩn bị dataset cuối.
