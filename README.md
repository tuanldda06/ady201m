# Zillow Real Estate Price Prediction

Dự án xây dựng quy trình Data Science cho bài toán dự đoán giá nhà từ dữ liệu Zillow. Dữ liệu được thu thập theo nhiều khu vực tại California, làm giàu bằng thông tin kinh tế - xã hội, rủi ro tự nhiên và khoảng cách địa lý, sau đó dùng để phân tích EDA và huấn luyện các mô hình hồi quy.

## Mục Tiêu

- Thu thập và làm sạch dữ liệu bất động sản từ Zillow.
- Phân tích các yếu tố liên quan đến giá nhà: diện tích, số phòng, loại nhà, vị trí, thu nhập khu vực, rủi ro tự nhiên và khoảng cách đến biển/thành phố/sân bay.
- Xây dựng và so sánh nhiều mô hình Machine Learning cho bài toán hồi quy giá nhà.
- Chọn mô hình tốt nhất dựa trên MAE, RMSE, R2 Score và MAPE.
- Bổ sung Cross-validation, Hyperparameter Tuning, Feature Importance, Error Analysis và kiểm định thống kê để tăng độ tin cậy của kết quả.
- Trình bày quy trình hoàn chỉnh từ Data Collection, Data Cleaning, EDA, Database Design đến Modeling.

## Cấu Trúc Dự Án

```text
ady201m/
├── PLAN.md
├── README.md
├── crawl_data/
│   ├── crawl_basic_data.py
│   └── crawl_extra_data.py
├── data_csv/
│   ├── zillow_basic_raw.csv
│   ├── zillow_full_raw.csv
│   ├── zillow_clean.csv
│   └── zillow_final.csv
├── data_processing/
│   ├── clean_raw.ipynb
│   ├── prepare_final.ipynb
│   └── README.md
├── eda/
│   ├── data_analyze.ipynb
│   └── eda_visualization.ipynb
├── database/
│   ├── create_database.sql
│   ├── schema.sql
│   ├── insert_data.sql
│   └── query_data.sql
└── train_model/
    ├── model.ipynb
    ├── model_advanced.ipynb
    ├── linear_regression.ipynb
    ├── random_forest.ipynb
    └── xgboost.ipynb
```

## Dữ Liệu

Dữ liệu gốc được crawl từ Zillow theo các ZIP code ở California, sau đó được bổ sung thêm thông tin từ các nguồn dữ liệu công khai:

- Zillow raw listing: giá, diện tích, số phòng ngủ, số phòng tắm, loại nhà, tọa độ.
- U.S. Census / ACS: thu nhập trung vị, tỷ lệ nghèo, thất nghiệp, dân số, tỷ lệ có bằng đại học, giá thuê trung vị.
- FEMA National Risk Index: điểm rủi ro tổng thể, thiệt hại, dễ tổn thương xã hội, phục hồi, cháy rừng, động đất, nắng nóng.
- Geo distance: khoảng cách đến thành phố lớn, sân bay lớn và bờ biển California.

Dataset cuối cùng nằm tại `data_csv/zillow_final.csv`



## Quy Trình Xử Lý

1. **Data Collection**

2. **Feature Enrichment**

3. **Data Cleaning**

4. **EDA**

5. **Modeling**


## Cách Chạy Project

### 1. Cài môi trường Python

Nên dùng Anaconda hoặc virtual environment riêng:

```bash
pip install pandas numpy matplotlib seaborn scikit-learn xgboost requests
```

### 2. Chạy xử lý dữ liệu

Mở và chạy các notebook theo thứ tự:

```text
data_processing/clean_raw.ipynb
data_processing/prepare_final.ipynb
eda/data_analyze.ipynb
eda/eda_visualization.ipynb
train_model/model.ipynb
train_model/model_advanced.ipynb
```

### 3. Chạy database

Dùng SQL Server và chạy các script theo thứ tự:

```text
database/create_database.sql
database/schema.sql
database/insert_data.sql
database/query_data.sql
```


