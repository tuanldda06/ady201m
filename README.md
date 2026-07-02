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

Dataset cuối cùng nằm tại `data_csv/zillow_final.csv`:

| Thông Tin | Giá Trị |
|---|---:|
| Số dòng | 4,251 |
| Số cột | 32 |
| Missing values | 0 |
| Duplicate rows | 0 |
| Target | `price` |

Một số cột quan trọng:

- Đặc trưng nhà: `bed`, `bath`, `living`, `lot_sqft`, `lot_living`, `bed_bath`
- Loại nhà: `type_condo`, `type_manufactured`, `type_multi`, `type_single`, `type_townhouse`
- Vị trí: `lat`, `long`, `dist_city`, `dist_airport`, `dist_coast`
- Kinh tế - xã hội: `income`, `poverty`, `unemployment`, `pop`, `bachelor`, `rent`, `owner_occ`, `pop_density`
- Rủi ro khu vực: `risk_overall`, `risk_loss`, `risk_social`, `risk_resilience`, `risk_fire`, `risk_earthquake`, `risk_heat`

## Quy Trình Xử Lý

1. **Data Collection**
   - Crawl dữ liệu cơ bản từ Zillow.
   - Lọc trùng listing trong quá trình thu thập.
   - Lưu dữ liệu raw vào `zillow_basic_raw.csv`.

2. **Feature Enrichment**
   - Chuyển tọa độ nhà sang Census Tract.
   - Nối thêm dữ liệu ACS và FEMA theo khu vực.
   - Tính các khoảng cách địa lý bằng công thức Haversine.
   - Lưu file đầy đủ vào `zillow_full_raw.csv`.

3. **Data Cleaning**
   - Loại dòng không có giá hoặc giá bằng 0.
   - Loại các dòng đất trống/không có thông tin nhà đầy đủ.
   - Xử lý missing values bằng median cho các biến phù hợp.
   - Tính lại các biến tỷ lệ như `bed_bath` và `lot_living`.
   - Loại 5% giá cao nhất để giảm ảnh hưởng của outliers cực đoan.

4. **EDA**
   - Phân tích thống kê mô tả.
   - Kiểm tra missing values và duplicates.
   - Phân tích phân phối `price`.
   - Phân tích tương quan giữa `price` và các đặc trưng.
   - Trực quan hóa histogram, heatmap, scatter plot, geographic plot và boxplot theo loại nhà.

5. **Modeling**
   - Chia train/test theo tỷ lệ 80/20.
   - Huấn luyện và so sánh Linear Regression, Random Forest và XGBoost.
   - Đánh giá bằng MAE, Median AE, RMSE, R2 Score và MAPE.
   - Bổ sung Feature Engineering không gây target leakage: tổng số phòng, diện tích/phòng, log diện tích, cờ gần biển/gần thành phố, tương tác thu nhập - học vấn và chỉ số rủi ro tổng hợp.
   - Thực hiện 5-fold Cross-validation trên training set.
   - Tuning Random Forest và XGBoost bằng RandomizedSearchCV.
   - Phân tích Permutation Feature Importance, Error Analysis theo phân khúc giá/loại nhà và kiểm định paired t-test trên CV folds.

## Kết Quả Mô Hình Baseline

Kết quả trong `train_model/model.ipynb`:

| Model | MAE | RMSE | R2 |
|---|---:|---:|---:|
| Linear Regression | 570,064 | 940,590 | 0.677 |
| Random Forest | 356,027 | 725,815 | 0.808 |
| XGBoost | 334,230 | 674,904 | 0.834 |

Mô hình XGBoost cho kết quả tốt nhất trong các mô hình đã thử nghiệm. Các biến có mức ảnh hưởng cao gồm `bachelor`, `living`, `bath`, `risk_earthquake`, `dist_coast`, `risk_resilience`, `risk_overall` và `risk_heat`.

## Kết Quả Modeling Nâng Cao

Kết quả trong `train_model/model_advanced.ipynb` sau Feature Engineering, Cross-validation và Hyperparameter Tuning:

| Model | MAE | Median AE | RMSE | R2 | MAPE |
|---|---:|---:|---:|---:|---:|
| XGBoost Tuned | 345,285 | 126,859 | 682,954 | 0.830 | 23.20% |
| Random Forest | 358,699 | 130,588 | 732,212 | 0.804 | 24.18% |
| Random Forest Tuned | 361,441 | 134,201 | 734,174 | 0.803 | 24.79% |
| XGBoost | 366,634 | 147,656 | 707,909 | 0.817 | 25.49% |
| ElasticNet | 571,111 | 368,053 | 934,695 | 0.681 | 61.40% |

Kết quả 5-fold Cross-validation trên training set:

| Model | CV MAE Mean | CV MAE Std | CV RMSE Mean | CV R2 Mean |
|---|---:|---:|---:|---:|
| XGBoost Tuned | 341,311 | 22,336 | 701,963 | 0.833 |
| XGBoost | 361,462 | 23,479 | 729,496 | 0.820 |
| Random Forest Tuned | 361,914 | 24,522 | 737,475 | 0.816 |
| Random Forest | 362,840 | 25,148 | 740,208 | 0.814 |
| ElasticNet | 597,039 | 17,506 | 967,256 | 0.680 |

Kiểm định paired t-test trên 5 CV folds:

| Comparison | MAE Improvement | p-value |
|---|---:|---:|
| XGBoost vs XGBoost Tuned | 20,151 | 0.0061 |
| Random Forest vs Random Forest Tuned | 926 | 0.2298 |

Nhận xét chính:

- `XGBoost Tuned` là mô hình tốt nhất theo MAE trên test set.
- Tuning XGBoost cải thiện rõ rệt so với XGBoost baseline trên CV folds; p-value 0.0061 cho thấy mức cải thiện có ý nghĩa thống kê trong thiết lập 5-fold này.
- Tuning Random Forest không cải thiện đáng kể; điều này được giữ lại trong báo cáo để thể hiện đánh giá khách quan.
- Permutation Importance cho thấy các biến quan trọng nhất gồm `living`, `dist_coast`, `lat`, `income_x_bachelor`, `bath`, `long`, `dist_airport`, `type_single`, `risk_heat` và `bachelor`.
- Error Analysis cho thấy mô hình sai lớn nhất ở nhóm nhà trên 2 triệu USD; MAE nhóm này khoảng 1.04 triệu USD, cao hơn nhiều so với các phân khúc thấp hơn.

## Database

Thư mục `database/` chứa các script SQL Server để thiết kế database quan hệ từ dataset cuối cùng:

- `create_database.sql`: tạo database `ZillowRealEstateDB`
- `schema.sql`: tạo bảng, khóa chính, khóa ngoại và index
- `insert_data.sql`: chèn dữ liệu mẫu/dữ liệu đã xử lý vào database
- `query_data.sql`: tạo view dữ liệu sạch và các truy vấn phân tích theo loại nhà, phân khúc giá, thu nhập, rủi ro, khoảng cách thành phố/biển, diện tích và nhóm kinh tế - xã hội

Database được tách thành các nhóm bảng chính:

- `raw_zillow_listings`: dữ liệu gốc
- `home_types`: danh mục loại nhà
- `socioeconomic_profiles`: thông tin kinh tế - xã hội
- `risk_profiles`: chỉ số rủi ro
- `properties`: thông tin nhà trung tâm
- `property_locations`: thông tin vị trí

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

## Lưu Ý Bảo Mật

Không nên commit API key, username/password hoặc token lên repository public. Nếu cần crawl lại dữ liệu, hãy cấu hình credential bằng biến môi trường hoặc file `.env` không đưa lên Git.

## Hạn Chế Và Hướng Phát Triển

- Dataset chỉ tập trung vào một số ZIP code/khu vực tại California, nên khả năng tổng quát hóa sang toàn bộ thị trường Mỹ còn hạn chế.
- Giá nhà có phân phối lệch phải và nhiều outliers; đã có thử nghiệm log-price ở các notebook mô hình riêng, nhưng có thể so sánh hệ thống hơn trong pipeline nâng cao.
- Cross-validation đã được bổ sung, nhưng vẫn nên thử split theo khu vực địa lý để đánh giá khả năng tổng quát hóa theo không gian.
- Có thể thêm feature engineering theo vùng, cluster tọa độ hoặc zipcode/county nếu có đủ thông tin.
- Hyperparameter tuning đã được thực hiện ở mức cơ bản; có thể mở rộng bằng Bayesian Optimization hoặc grid lớn hơn nếu có nhiều tài nguyên tính toán.
- Nên bổ sung thêm biến chất lượng nhà như năm xây dựng, tình trạng nội thất, trường học, crime rate hoặc tiện ích xung quanh nếu crawl được dữ liệu.

## Tác Giả

Dự án môn ADY201m - Introduction to Data Science.
