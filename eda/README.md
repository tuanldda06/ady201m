# EDA - Zillow Real Estate Dataset

Thư mục này chứa phần phân tích khám phá dữ liệu cho dataset cuối cùng tại `data_csv/zillow_final.csv`.

## File Chính

```text
eda/
├── data_analyze.ipynb
├── eda_visualization.ipynb
└── README.md
```

## Nội Dung

- `data_analyze.ipynb`: kiểm tra cấu trúc dữ liệu, missing values, duplicate rows, thống kê mô tả, phân phối `price`, tương quan và nhận xét chính.
- `eda_visualization.ipynb`: trực quan hóa phân phối giá, heatmap tương quan, scatter plot, boxplot theo loại nhà và biểu đồ địa lý theo tọa độ.

## Tóm Tắt Dữ Liệu

| Thông Tin | Giá Trị |
|---|---:|
| Số dòng | 4,251 |
| Số cột | 32 |
| Missing values | 0 |
| Duplicate rows | 0 |
| Target | `price` |

## Nhận Xét Chính

- `price` có phân phối lệch phải, vì vậy các mô hình cần được đánh giá thêm bằng MAE, Median AE và MAPE thay vì chỉ dùng R2.
- `living`, `bath`, `bachelor`, `dist_coast` và các biến vị trí/rủi ro là nhóm biến đáng chú ý khi phân tích giá.
- Các biểu đồ EDA được dùng để hỗ trợ Feature Engineering và Error Analysis trong `train_model/model_advanced.ipynb`.
