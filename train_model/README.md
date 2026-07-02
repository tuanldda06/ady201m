# Model Training

Thư mục này chứa các notebook huấn luyện mô hình hồi quy để dự đoán giá nhà (`price`) từ dataset cuối cùng `data_csv/zillow_final.csv`.

```text
train_model/
├── model.ipynb
├── model_advanced.ipynb
├── linear_regression.ipynb
├── random_forest.ipynb
├── xgboost.ipynb
└── README.md
```

## Dữ Liệu Và Target

- Input: `../data_csv/zillow_final.csv`
- Target: `price`
- Baseline features: 31 cột sau khi bỏ `price`
- Train/test split: 80/20 với `random_state=42`
- Trong `model_advanced.ipynb`, feature engineering tăng số biến lên 39 cột.

## File Chính

| Notebook | Vai trò |
|---|---|
| `model.ipynb` | So sánh baseline giữa Linear Regression, Random Forest và XGBoost trên cùng train/test split. |
| `linear_regression.ipynb` | Huấn luyện ElasticNet Linear Regression với `log(price)` và phân tích coefficient. |
| `random_forest.ipynb` | Huấn luyện Random Forest với `log(price)` và trực quan hóa feature importance. |
| `xgboost.ipynb` | Huấn luyện XGBoost với `log(price)`, regularization và feature importance. |
| `model_advanced.ipynb` | Notebook tổng hợp nâng cao: Feature Engineering, 5-fold Cross-validation, Hyperparameter Tuning, Feature Importance, Error Analysis và paired t-test. |

## Chỉ Số Đánh Giá

Các notebook đánh giá mô hình bằng các metric chính:

- `MAE`: sai số tuyệt đối trung bình, đơn vị USD.
- `Median AE`: sai số tuyệt đối trung vị, giúp giảm ảnh hưởng của outlier.
- `RMSE`: phạt mạnh các lỗi dự đoán lớn.
- `R2`: mức độ giải thích phương sai của mô hình.
- `MAPE (%)`: sai số phần trăm trung bình.

Với MAE, Median AE, RMSE và MAPE thì giá trị càng thấp càng tốt. Với R2 thì giá trị càng cao càng tốt.

## Kết Quả Chính

- Trong `model.ipynb`, XGBoost cho kết quả tốt nhất trong nhóm baseline với MAE khoảng `334,230`, RMSE khoảng `674,904` và R2 khoảng `0.834`.
- Trong `xgboost.ipynb`, XGBoost train trên `log(price)` đạt MAE khoảng `331,149`, RMSE khoảng `695,350`, R2 khoảng `0.823` và MAPE khoảng `20.05%`.
- Trong `model_advanced.ipynb`, mô hình tốt nhất theo MAE trên test set là `XGBoost Tuned` với MAE khoảng `345,285`, RMSE khoảng `682,954`, R2 khoảng `0.830` và MAPE khoảng `23.20%`.

Các kết quả có thể chênh lệch nhẹ nếu phiên bản thư viện hoặc random seed thay đổi.

## Thứ Tự Chạy Gợi Ý

1. Chạy notebook xử lý dữ liệu để tạo `data_csv/zillow_final.csv`.
2. Chạy `linear_regression.ipynb`, `random_forest.ipynb` và `xgboost.ipynb` nếu muốn xem riêng từng mô hình.
3. Chạy `model.ipynb` để xem bảng so sánh baseline.
4. Chạy `model_advanced.ipynb` cho phần báo cáo cuối vì file này có cross-validation, tuning và error analysis.

`model_advanced.ipynb` dùng `RandomizedSearchCV`, nên thời gian chạy sẽ lâu hơn các notebook đơn lẻ.
