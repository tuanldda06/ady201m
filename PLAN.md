# PLAN

# ĐỀ TÀI

# **Xây dựng và Tối ưu hóa Mô hình Machine Learning cho Bài toán Dự đoán Giá Nhà**

* **Môn học:** ADY201m – Introduction to Data Science
* **Lớp:** AI2013
* **Giảng viên hướng dẫn:** ....................................

---

# 1. MỤC TIÊU

Mục tiêu của dự án là xây dựng một mô hình Machine Learning có khả năng dự đoán giá nhà dựa trên các đặc trưng của bất động sản như diện tích, số phòng ngủ, số phòng tắm, loại nhà, vị trí và các thông tin liên quan. Đồng thời, nhóm sẽ đánh giá, so sánh nhiều thuật toán hồi quy và tối ưu hóa mô hình nhằm nâng cao độ chính xác của dự đoán. Kết quả của dự án giúp người dùng có thể ước lượng giá trị bất động sản và hỗ trợ ra quyết định trong lĩnh vực mua bán nhà ở.

---

# 2. BẢNG THÀNH VIÊN VÀ PHÂN CÔNG NHIỆM VỤ

| STT | Họ và tên    | MSSV     | Vai trò                             | Nhiệm vụ chi tiết                                                                                                                                        | Output dự kiến                                            |
| --- | ------------ | -------- | ----------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------- |
| 1   | Thành viên 1 | ........ | Data Collector                      | Cào dữ liệu, thu thập dữ liệu từ nguồn phù hợp, kiểm tra định dạng ban đầu, lưu trữ dataset gốc và quản lý nguồn dữ liệu.                                | Dataset gốc, file dữ liệu ban đầu, mô tả nguồn dữ liệu    |
| 2   | Thành viên 2 | ........ | Data Preprocessing                  | Xử lý dữ liệu thiếu, loại bỏ dữ liệu trùng lặp, phát hiện và xử lý outlier, chuyển đổi kiểu dữ liệu, mã hóa biến phân loại và chuẩn hóa dữ liệu khi cần. | Dataset đã làm sạch, Notebook tiền xử lý                  |
| 3   | Thành viên 3 | ........ | Data Analyst                        | Phân tích thống kê mô tả, thực hiện EDA, trực quan hóa dữ liệu, phân tích tương quan, rút ra insight và hỗ trợ viết phần báo cáo phân tích.              | Biểu đồ, Insight, Báo cáo EDA                             |
| 4   | Thành viên 4 | ........ | Machine Learning Engineer / Modeler | Xây dựng mô hình hồi quy, chia tập train/test, huấn luyện và so sánh các mô hình, tối ưu hyperparameter, đánh giá kết quả bằng các chỉ số phù hợp.       | Notebook mô hình, Bảng so sánh mô hình, Mô hình cuối cùng |

---

# 3. LỘ TRÌNH THỰC HIỆN DỰ ÁN

## Giai đoạn 1: Business Understanding & Data Collection

**Deadline:** ....................................

### Công việc

* Xác định mục tiêu bài toán.
* Xây dựng các Business Questions.
* Cào và thu thập dữ liệu giá nhà.
* Tìm hiểu ý nghĩa của các thuộc tính.
* Kiểm tra số lượng mẫu và chất lượng dữ liệu ban đầu.

**Nhân sự chính**

* Thành viên 1
* Thành viên 3

**Phân công cụ thể**

* **Thành viên 1:** Cào dữ liệu, thu thập dữ liệu từ nguồn phù hợp, kiểm tra định dạng và lưu trữ dataset gốc.
* **Thành viên 3:** Xây dựng Business Questions, xác định các vấn đề cần phân tích từ dữ liệu.

**Output**

* Dataset ban đầu.
* Danh sách Business Questions.
* Báo cáo mô tả dữ liệu.

---

## Giai đoạn 2: Data Preprocessing

**Deadline:** ....................................

### Công việc

* Kiểm tra Missing Values.
* Kiểm tra Duplicate.
* Phát hiện và xử lý Outlier.
* Chuyển đổi kiểu dữ liệu.
* Feature Encoding (One-Hot Encoding).
* Chuẩn hóa dữ liệu khi cần.
* Phân tích phân phối của biến Price.
* Áp dụng Log Transformation nếu phù hợp.

**Nhân sự chính**

* Thành viên 2
* Thành viên 4

**Phân công cụ thể**

* **Thành viên 2:** Làm sạch dữ liệu, xử lý missing values, duplicate, outlier và chuẩn hóa dữ liệu đầu vào.
* **Thành viên 4:** Kiểm tra ảnh hưởng của các bước tiền xử lý đến dữ liệu, hỗ trợ feature engineering và chuẩn bị dữ liệu cho mô hình.

**Output**

* Dataset đã làm sạch.
* Notebook tiền xử lý dữ liệu.

---

## Giai đoạn 3: Exploratory Data Analysis (EDA)

**Deadline:** ....................................

### Công việc

* Phân tích thống kê mô tả.

* Phân tích phân phối dữ liệu.

* Phân tích tương quan giữa các biến.

* Trực quan hóa dữ liệu bằng:

  * Histogram
  * Boxplot
  * Scatter Plot
  * Heatmap Correlation
  * Pairplot (nếu cần)

* Đưa ra các Insight từ dữ liệu.

**Nhân sự chính**

* Thành viên 3
* Thành viên 1

**Phân công cụ thể**

* **Thành viên 3:** Thực hiện EDA, trực quan hóa dữ liệu và rút ra insight chính.
* **Thành viên 1:** Hỗ trợ kiểm tra lại dữ liệu gốc, đối chiếu nguồn dữ liệu và bổ sung thông tin mô tả dữ liệu nếu cần.

**Output**

* Các biểu đồ trực quan.
* Báo cáo EDA.
* Insight của dữ liệu.

---

## Giai đoạn 4: Modeling & Evaluation

**Deadline:** ....................................

### Công việc

* Chia dữ liệu Train/Test.

* Huấn luyện các mô hình:

  * Linear Regression
  * Decision Tree Regressor
  * Random Forest Regressor

* So sánh hiệu năng giữa các mô hình.

* Tối ưu Random Forest bằng RandomizedSearchCV.

* Đánh giá mô hình bằng:

  * MAE
  * RMSE
  * R² Score

* Phân tích Feature Importance.

* Chọn mô hình cuối cùng.

**Nhân sự chính**

* Thành viên 4
* Thành viên 2

**Phân công cụ thể**

* **Thành viên 4:** Xây dựng, huấn luyện và đánh giá các mô hình hồi quy, thực hiện tối ưu hyperparameter.
* **Thành viên 2:** Hỗ trợ kiểm tra dữ liệu đầu vào cho mô hình, tổng hợp kết quả đánh giá và đối chiếu hiệu quả giữa các mô hình.

**Output**

* Notebook Modeling.
* Bảng so sánh các mô hình.
* Mô hình tốt nhất.

---

## Giai đoạn 5: Reporting & Presentation

**Deadline:** ....................................

### Công việc

* Tổng hợp toàn bộ kết quả.
* Phân tích ưu điểm và hạn chế của mô hình.
* Hoàn thiện báo cáo.
* Thiết kế Slide.
* Chuẩn bị thuyết trình.

**Nhân sự chính**

* Toàn bộ nhóm

**Phân công cụ thể**

* **Thành viên 1:** Trình bày phần thu thập dữ liệu và mô tả nguồn dữ liệu.
* **Thành viên 2:** Trình bày phần tiền xử lý và làm sạch dữ liệu.
* **Thành viên 3:** Trình bày phần EDA, biểu đồ thống kê và insight.
* **Thành viên 4:** Trình bày phần xây dựng mô hình, đánh giá và tối ưu mô hình.

**Output**

* Báo cáo hoàn chỉnh.
* Slide thuyết trình.
* Source Code.
* Dataset.
* Notebook cuối cùng.

---

# Deliverables

* Dataset gốc.
* Dataset sau tiền xử lý.
* Notebook EDA.
* Notebook Modeling.
* Notebook Hyperparameter Tuning.
* Báo cáo phân tích.
* Slide thuyết trình.
* Source Code.
* Mô hình Machine Learning cuối cùng.

---

# Công nghệ sử dụng

* Python
* Pandas
* NumPy
* Matplotlib
* Seaborn
* Scikit-learn
* Jupyter Notebook

---

# Kết quả mong đợi

* Xây dựng thành công mô hình dự đoán giá nhà.
* So sánh nhiều thuật toán hồi quy để lựa chọn mô hình phù hợp.
* Đạt mô hình có độ chính xác cao (đánh giá bằng MAE, RMSE và R²).
* Phân tích các yếu tố ảnh hưởng lớn nhất đến giá nhà thông qua Feature Importance.
* Hoàn thiện quy trình Data Science từ thu thập dữ liệu, tiền xử lý, trực quan hóa, xây dựng mô hình đến đánh giá kết quả.
