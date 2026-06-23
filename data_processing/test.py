import pandas as pd
import numpy as np

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score,
    median_absolute_error,
    mean_absolute_percentage_error
)

# =========================
# 1. Đọc dữ liệu
# =========================

df = pd.read_csv("zillow_final.csv")

print("Shape:", df.shape)
print(df.head())

# =========================
# 2. Xử lý dữ liệu
# =========================

# Đổi True/False thành 1/0 nếu có
for col in df.select_dtypes(include=["bool"]).columns:
    df[col] = df[col].astype(int)

# Bỏ dòng bị thiếu price
df = df.dropna(subset=["price"])

# Tách X và y
X = df.drop(columns=["price"])
y = df["price"]

# Chỉ lấy cột số
X = X.select_dtypes(include=["int64", "float64"])

# Điền missing value bằng median
X = X.fillna(X.median())

# =========================
# 3. Chia train/test
# =========================

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42
)

# =========================
# 4. Hàm đánh giá
# =========================

def evaluate_model(name, y_true, y_pred):
    mae = mean_absolute_error(y_true, y_pred)
    median_ae = median_absolute_error(y_true, y_pred)
    rmse = mean_squared_error(y_true, y_pred) ** 0.5
    r2 = r2_score(y_true, y_pred)
    mape = mean_absolute_percentage_error(y_true, y_pred) * 100

    print("\n" + "=" * 50)
    print(name)
    print("=" * 50)
    print(f"MAE       : {mae:,.0f}")
    print(f"Median AE : {median_ae:,.0f}")
    print(f"RMSE      : {rmse:,.0f}")
    print(f"R2        : {r2:.4f}")
    print(f"MAPE      : {mape:.2f}%")

# =========================
# 5. Random Forest thường
# =========================

rf_raw = RandomForestRegressor(
    n_estimators=300,
    max_depth=None,
    min_samples_split=2,
    min_samples_leaf=1,
    max_features="sqrt",
    random_state=42,
    n_jobs=-1
)

rf_raw.fit(X_train, y_train)

pred_raw = rf_raw.predict(X_test)

evaluate_model(
    "Random Forest - Raw Price",
    y_test,
    pred_raw
)

# =========================
# 6. Random Forest với log(price)
# =========================

rf_log = RandomForestRegressor(
    n_estimators=300,
    max_depth=None,
    min_samples_split=2,
    min_samples_leaf=1,
    max_features="sqrt",
    random_state=42,
    n_jobs=-1
)

# Log target
y_train_log = np.log1p(y_train)

rf_log.fit(X_train, y_train_log)

# Dự đoán log rồi đổi ngược về price
pred_log = rf_log.predict(X_test)
pred_log_price = np.expm1(pred_log)

evaluate_model(
    "Random Forest - Log Price",
    y_test,
    pred_log_price
)

# =========================
# 7. Feature importance
# =========================

importance_df = pd.DataFrame({
    "feature": X_train.columns,
    "importance": rf_log.feature_importances_
})

importance_df = importance_df.sort_values(
    by="importance",
    ascending=False
)

print("\nTop 15 important features:")
print(importance_df.head(15))