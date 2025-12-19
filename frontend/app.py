import math
import os
import sqlite3
from flask import Flask, abort, render_template, request, jsonify

app = Flask(__name__)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "..", "rent.db")

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

@app.route("/api/districts")
def get_districts():
    conn = get_db_connection()
    rows = conn.execute("""
        SELECT DISTINCT district
        FROM rent_records
        WHERE district IS NOT NULL
        ORDER BY district
    """).fetchall()
    conn.close()
    return jsonify([r["district"] for r in rows])

# ===== 首頁 =====
@app.route("/")
def index():
    return render_template("index.html",page="home")


# ===== 結果頁（只回 HTML，不帶資料）=====
@app.route("/result")
def result_page():
    return render_template("result.html", page="result")

# # ===== dashbroad頁=====
# @app.route("/analysis")
# def analysis_home():
#     return render_template("analysis_home.html", page="analysis")


# ===== 租屋市場族群分佈（圓餅圖）=====
@app.route("/analysis/distribution")
def analysis_distribution():
    return render_template("analysis_distribution.html", page="analysis_distribution")


# ===== 各租屋族群特徵比較（長條圖）=====
@app.route("/analysis/compare")
def analysis_compare():
    return render_template("analysis_compare.html", page="analysis_compare")

@app.route("/house/<house_id>")
def house_detail(house_id):
    conn = get_db_connection()
    house = conn.execute(
        "SELECT * FROM rent_records WHERE id = ?",
        (house_id,)
    ).fetchone()
    conn.close()

    if not house:
        abort(404)
    return render_template("house_detail.html", house=house)

# ===== API：租屋資料（給 JS fetch 用）=====
@app.route("/api/rent/by-cluster")
def rent_api():
    cluster = request.args.get("cluster", type=int)
    rent_min = request.args.get("rent_min", type=int, default=0)
    rent_max = request.args.get("rent_max", type=int, default=999999)
    district = request.args.get("district")
    page = request.args.get("p", type=int, default=1)
    page_size = 6


    conn = get_db_connection()

    # ===== 共用 WHERE 條件 =====
    where_clauses = ["cluster = ?", "total_rent BETWEEN ? AND ?"]
    params = [cluster, rent_min, rent_max]

    if district:
        where_clauses.append("district = ?")
        params.append(district)

    where_sql = " AND ".join(where_clauses)

    # ===== 1️⃣ 正確的總筆數（含所有篩選）=====
    count_query = f"""
        SELECT COUNT(*)
        FROM rent_records
        WHERE {where_sql}
    """
    total = conn.execute(count_query, params).fetchone()[0]
    total_pages = math.ceil(total / page_size) if total > 0 else 1

    # ===== 2️⃣ 分頁資料 =====
    offset = (page - 1) * page_size
    data_query = f"""
        SELECT district, area_ping, total_rent,id
        FROM rent_records
        WHERE {where_sql}
        LIMIT ? OFFSET ?
    """
    data_params = params + [page_size, offset]

    rows = conn.execute(data_query, data_params).fetchall()
    conn.close()

    return jsonify({
        "houses": [dict(r) for r in rows],
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
        "total": total
    })

#cluster_distribution
@app.route("/api/cluster_distribution")
def cluster_distribution():
    conn = get_db_connection()
    query = """
        SELECT cluster, COUNT(*) AS count
        FROM rent_records
        GROUP BY cluster
        ORDER BY cluster
    """

    rows = conn.execute(query).fetchall()
    conn.close()

    labels = [f"Cluster {row['cluster']}" for row in rows]
    data = [row["count"] for row in rows]

    return jsonify({
        "labels": labels,
        "data": data
    })

#特徵比較
@app.route("/api/cluster/summary")
def cluster_summary():
    conn = get_db_connection()
    rows = conn.execute("""
        SELECT
            cluster,
            AVG(total_rent) AS avg_rent,
            AVG(area_ping) AS avg_size,
            AVG(house_age) AS avg_age
        FROM rent_records
        GROUP BY cluster
        ORDER BY cluster
    """).fetchall()

    return jsonify([
        {
            "cluster": r["cluster"],
            "avg_rent": round(r["avg_rent"], 1),
            "avg_size": round(r["avg_size"], 1),
            "avg_age": round(r["avg_age"], 1)
        }
        for r in rows
    ])

if __name__ == "__main__":
    app.run(debug=True, port=5001)
