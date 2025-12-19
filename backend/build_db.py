from pathlib import Path
import pandas as pd
import sqlite3
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score

# ---------- 1. 讀資料 ----------
use_columns = [
    "rps28",
    "district","rps02","rps09","rps10_quantity",
    "rps14_yyymmddroc",   # ← 修正欄位名
    "rps15_area","rps16_quantity","rps17_quantity",
    "rps18_quantity","rps21",
    "rps22_amountsunitdollars","rps23_amountsunitdollars",
    "rps30","rps32"
]
BASE_DIR = Path(__file__).resolve().parent
CSV_PATH = BASE_DIR / "不動產實價登錄資訊-租賃案件.csv"
df = pd.read_csv(
    CSV_PATH,
    encoding="utf-8",
    usecols=use_columns
)

df = df.rename(columns={
    "rps28":"id",
    "district": "district",
    "rps02": "address",
    "rps09": "floor",
    "rps10_quantity": "total_floors",
    "rps14_yyymmddroc": "building_completion_date",
    "rps15_area": "building_area_sqm",
    "rps16_quantity": "num_rooms",
    "rps17_quantity": "num_living_rooms",
    "rps18_quantity": "num_bathrooms",
    "rps21": "has_furniture",
    "rps22_amountsunitdollars": "total_rent",
    "rps23_amountsunitdollars": "rent_per_sqm",
    "rps30": "has_manager",
    "rps32": "has_elevator"
})
# ---------- 2. 屋齡計算（民國 → 西元） ----------
df["build_year_roc"] = (
    df["building_completion_date"]
    .astype(str)
    .str[:3]
)

df["build_year"] = pd.to_numeric(df["build_year_roc"], errors="coerce") + 1911

CURRENT_YEAR = 2025
df["house_age"] = CURRENT_YEAR - df["build_year"]

# 清理不合理屋齡
df = df[(df["house_age"] >= 0) & (df["house_age"] <= 100)]

# ---------- 3. 數值欄位清理 ----------
num_cols = ["total_rent", "rent_per_sqm", "building_area_sqm"]
for c in num_cols:
    df[c] = pd.to_numeric(df[c], errors="coerce")

df = df.dropna(subset=num_cols + ["house_age"])

# 加一個「坪數」欄位（超加分）
df["area_ping"] = round(df["building_area_sqm"] / 3.3058,3)
df = df[df["area_ping"] <= 200]
# ---------- 5. Clustering ----------
features = df[["total_rent", "area_ping", "house_age"]]

scaler = StandardScaler()
X_scaled = scaler.fit_transform(features)

kmeans = KMeans(n_clusters=4, random_state=42, n_init=10)
df["cluster"] = kmeans.fit_predict(X_scaled)

score = silhouette_score(X_scaled, df["cluster"])
print("Silhouette Score:", score)

print(
    df.groupby("cluster")[["total_rent", "area_ping", "house_age"]].mean()
)

# ---------- 4. 存進 SQLite ----------
conn = sqlite3.connect("rent.db")
df.to_sql("rent_records", conn, if_exists="replace", index=False)

print(df.head())

# 🔵 Cluster 0
# 單坪租金：中偏高
# 坪數：中小
# 屋齡：非常新（2.4 年）
# 👉 合理解釋：
# 「新成屋、小家庭 / 單身族、高品質住宅」
# ✔ 新 → 租金高
# ✔ 坪數不大 → 單坪合理偏高
# 這一群非常合理
# 🟢 Cluster 1
# 單坪租金：最低
# 坪數：最大（66 坪）
# 屋齡：偏舊
# 👉 合理解釋：
# 「郊區或家庭型大坪數住宅」
# ✔ 坪數大 → 單坪自然低
# ✔ 屋齡高 → 租金下降
# 這是 textbook 等級的合理群
# 🟡 Cluster 2
# 單坪租金：中
# 坪數：中小
# 屋齡：偏舊
# 👉 合理解釋：
# 「舊公寓 / 一般市場主流房型」
# ✔ 跟 Cluster 0 差別在「屋齡」
# ✔ 跟 Cluster 1 差別在「坪數」
# 📌 這一群的存在很重要
# 代表模型不是只分「貴 vs 便宜」
# 🔴 Cluster 3（最關鍵）
# 單坪租金：極高（521）
# 坪數：最小
# 屋齡：偏舊（但不影響）
# 👉 合理解釋：
# 「市中心核心區小宅（蛋黃區）」
# 或「豪宅單位切割」
# ✔ 地段價值 > 屋齡
# ✔ 小坪數 → 單坪爆高
# 📌 這群非常「像真實市場」ㄋ