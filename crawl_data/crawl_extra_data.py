
# MỤC ĐÍCH:
#   File này dùng để "làm giàu dữ liệu" cho dataset nhà đất lấy từ Zillow.
#   Nghĩa là: dữ liệu gốc từ Zillow chỉ có thông tin cơ bản như giá, diện tích,
#   số phòng ngủ, số phòng tắm, tọa độ... Sau đó code này gọi thêm các nguồn dữ liệu công khai để bổ sung đặc trưng phục vụ mô hình dự đoán giá nhà.
#
# CÁC NHÓM FEATURE TRONG 5 BƯỚC CHẠY:
#   [1/5] Basic Zillow features:
#      - KHÔNG cào thêm API mới.
#      - Chỉ tính toán lại từ file Zillow raw đã có sẵn, ví dụ:
#        price_per_sqft, lot_to_living_ratio, beds_per_bath, log_price...
#
#   [2/5] Census + ACS:
#      - CÓ gọi API ngoài.
#      - Dùng Census Geocoder để đổi lat/lon -> Census Tract.
#      - Sau đó gọi ACS 5-year để lấy income, poverty, unemployment...
#
#   [3/5] OSM amenities:
#      - CÓ gọi API ngoài.
#      - Dùng OpenStreetMap / Overpass API để đếm tiện ích xung quanh nhà.
#
#   [4/5] FEMA NRI:
#      - CÓ gọi API ngoài.
#      - Dùng mã Census Tract để lấy điểm rủi ro thiên tai từ FEMA.
#
#   [5/5] Geo distance:
#      - KHÔNG cào thêm API mới.
#      - Tự tính khoảng cách bằng công thức Haversine dựa trên tọa độ nhà
#        và danh sách tọa độ thành phố/sân bay/bờ biển đã khai báo trong code.
#
#
# CÁC NGUỒN DỮ LIỆU ĐƯỢC DÙNG:
#   1. Zillow raw data:
#      - Là file CSV đầu vào đã cào từ Zillow.
#      - Dùng để lấy price, living area, bedrooms, bathrooms, home type, lat/lon...
#
#   2. U.S. Census Geocoder:
#      - Dùng tọa độ latitude/longitude của từng căn nhà để tìm Census Tract.
#      - Census Tract giống như một vùng thống kê nhỏ tại Mỹ.
#      - Việc map tọa độ -> tract giúp chứng minh mỗi căn nhà được nối đúng
#        với khu vực dân cư tương ứng.
#
#   3. ACS 5-year data của U.S. Census:
#      - Sau khi có tract, code gọi ACS để lấy income, poverty, unemployment,
#        population, bachelor rate...
#      - Đây là dữ liệu kinh tế - xã hội chính thức của U.S. Census.
#
#   4. OpenStreetMap / Overpass API:
#      - Dùng tọa độ căn nhà để đếm tiện ích xung quanh như trường học, bệnh viện,
#        siêu thị, công viên, trạm giao thông công cộng.
#      - Code dùng bán kính rõ ràng: grocery/park/transit 1km, school 2km,
#        hospital 3km.
#
#   5. FEMA National Risk Index:
#      - Dùng tract_geoid để lấy điểm rủi ro thiên tai như wildfire, earthquake,
#        flood.
#      - Dữ liệu này giúp mô hình có thêm thông tin về rủi ro khu vực.
#
#   6. Khoảng cách địa lý tự tính:
#      - Code dùng công thức Haversine để tính khoảng cách từ căn nhà đến
#        thành phố lớn, sân bay lớn và bờ biển California.
#
# CÁCH CÀO :
#   - Không ghép dữ liệu theo tên mơ hồ, mà ghép theo tọa độ thật của căn nhà.
#   - Tọa độ được chuyển sang Census Tract bằng Census Geocoder.
#   - ACS và FEMA được lấy theo tract_geoid, tức mã vùng thống kê chính thức.
#   - OSM đếm tiện ích theo khoảng cách thực tế từ tọa độ căn nhà.
#   - Cuối chương trình có phần "Feature check" để kiểm tra từng feature có được
#     tạo ra hay không và có bao nhiêu dòng không bị thiếu dữ liệu.
#   - Có cache để tránh gọi API lặp lại, giúp kết quả ổn định hơn khi chạy lại.
#


import argparse, json, math, os, time, random
from pathlib import Path

import numpy as np
import pandas as pd
import requests

CACHE = Path.home() / ".cache" / "zillow_feature_cache_short"
CACHE.mkdir(parents=True, exist_ok=True)


S = requests.Session()
S.headers.update({"User-Agent": "zillow-feature-enrichment-student-project/1.0"})

# API chính thức của U.S. Census để đổi tọa độ nhà -> Census Tract.
CENSUS_GEOCODER = "https://geocoding.geo.census.gov/geocoder/geographies/coordinates"
# API dữ liệu FEMA National Risk Index theo Census Tract.
NRI_URL = "https://services.arcgis.com/XG15cJAlne2vxtgt/arcgis/rest/services/National_Risk_Index_Census_Tracts/FeatureServer/0"
# Các endpoint Overpass để truy vấn OpenStreetMap.
# Có nhiều endpoint dự phòng: nếu một endpoint lỗi/quá tải thì thử endpoint khác.
OVERPASS = [
    "https://overpass-api.de/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter",
    "https://overpass.openstreetmap.ru/api/interpreter",
]

OSM_SLEEP = 10
GRID = 2

def load_cache(name):
    p = CACHE / name
    if p.exists():
        try:
            return json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}


def save_cache(name, obj):
    (CACHE / name).write_text(json.dumps(obj, ensure_ascii=False), encoding="utf-8")



def req_json(url, params=None, data=None, post=False, retries=3, timeout=40):
    last = None
    for i in range(retries):
        try:
            r = S.post(url, params=params, data=data, timeout=timeout) if post else S.get(url, params=params, timeout=timeout)
            if r.status_code == 429:
                time.sleep(60)
            r.raise_for_status()
            return r.json()
        except Exception as e:
            last = e
            time.sleep(1 + i * 2 + random.random())
    raise RuntimeError(last)


def num(x):
    try:
        x = float(x)
        return np.nan if x <= -9999 else x
    except Exception:
        return np.nan

def div(a, b):
    a, b = num(a), num(b)
    return np.nan if pd.isna(a) or pd.isna(b) or b == 0 else a / b


def col(df, names):
    return next((c for c in names if c in df.columns), None)


def latlon(df):
    la = col(df, ["latLong.latitude", "hdpData.homeInfo.latitude", "latitude", "lat"])
    lo = col(df, ["latLong.longitude", "hdpData.homeInfo.longitude", "longitude", "lon", "lng"])
    if not la or not lo:
        raise ValueError("Không tìm thấy cột latitude/longitude.")
    return la, lo

def hav(lat1, lon1, lat2, lon2):
    R = 6371.0088
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp, dl = math.radians(lat2 - lat1), math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * R * math.asin(math.sqrt(a))


# ================================================================
# [1/5] ADD BASIC ZILLOW FEATURES
# Tạo feature trực tiếp từ dữ liệu Zillow gốc.
# Đây không phải dữ liệu cào thêm mà là biến đổi từ các cột có sẵn:
#   - target_price, log_price
#   - living_area_sqft, bedrooms, bathrooms
#   - price_per_sqft
#   - lot_area_sqft, lot_to_living_ratio
#   - beds_per_bath
#   - home_type one-hot encoding
# ================================================================
def add_basic(df):
    # Nó chỉ lấy các cột có sẵn trong file Zillow raw rồi tạo feature mới.
    # Ví dụ: price_per_sqft = price / living area.
    # Vì vậy khi trình bày, nên gọi đây là bước "xử lý / biến đổi feature từ Zillow",
    # không nên gọi là bước "cào dữ liệu ngoài".
    print("\n[1/5] Basic Zillow features - derived from Zillow raw, not external crawling")
    df = df.copy()
    p = col(df, ["hdpData.homeInfo.price", "price"])
    a = col(df, ["hdpData.homeInfo.livingArea", "area"])
    b = col(df, ["hdpData.homeInfo.bedrooms", "beds"])
    ba = col(df, ["hdpData.homeInfo.bathrooms", "baths"])
    rent = col(df, ["hdpData.homeInfo.rentZestimate", "rentZestimate"])
    zest = col(df, ["hdpData.homeInfo.zestimate", "zestimate"])
    tax = col(df, ["hdpData.homeInfo.taxAssessedValue", "taxAssessedValue"])
    lot = col(df, ["hdpData.homeInfo.lotAreaValue", "lotAreaValue"])
    unit = col(df, ["hdpData.homeInfo.lotAreaUnit", "lotAreaUnit"])
    days = col(df, ["hdpData.homeInfo.daysOnZillow", "daysOnZillow"])
    typ = col(df, ["hdpData.homeInfo.homeType", "homeType"])

    if p:
        df["target_price"] = pd.to_numeric(df[p], errors="coerce")
        df["log_price"] = np.log1p(df["target_price"])
    if a:
        df["living_area_sqft"] = pd.to_numeric(df[a], errors="coerce")
    if b:
        df["bedrooms"] = pd.to_numeric(df[b], errors="coerce")
    if ba:
        df["bathrooms"] = pd.to_numeric(df[ba], errors="coerce")
    if p and a:
        df["price_per_sqft"] = pd.to_numeric(df[p], errors="coerce") / pd.to_numeric(df[a], errors="coerce").replace(0, np.nan)
    if p and rent:
        df["annual_rent_to_price_ratio"] = pd.to_numeric(df[rent], errors="coerce") * 12 / pd.to_numeric(df[p], errors="coerce").replace(0, np.nan)
    if p and zest:
        df["zestimate_to_price_ratio"] = pd.to_numeric(df[zest], errors="coerce") / pd.to_numeric(df[p], errors="coerce").replace(0, np.nan)
    if p and tax:
        df["tax_assessment_to_price_ratio"] = pd.to_numeric(df[tax], errors="coerce") / pd.to_numeric(df[p], errors="coerce").replace(0, np.nan)
    if lot:
        x = pd.to_numeric(df[lot], errors="coerce")
        df["lot_area_sqft"] = np.where(df[unit].astype(str).str.lower().str.contains("acre", na=False), x * 43560, x) if unit else x
    if lot and a:
        df["lot_to_living_ratio"] = df["lot_area_sqft"] / pd.to_numeric(df[a], errors="coerce").replace(0, np.nan)
    if b and ba:
        df["beds_per_bath"] = pd.to_numeric(df[b], errors="coerce") / pd.to_numeric(df[ba], errors="coerce").replace(0, np.nan)
    if days:
        d = pd.to_numeric(df[days], errors="coerce")
        df["is_fresh_listing_7d"] = (d <= 7).astype("Int64")
        df["is_stale_listing_90d"] = (d >= 90).astype("Int64")
    if typ:
        df = pd.concat([df, pd.get_dummies(df[typ].astype(str), prefix="home_type", dummy_na=True)], axis=1)
    return df


# ================================================================
# [2/5] ADD CENSUS + ACS FEATURES
# Quy trình :
#   Bước 1: lấy lat/lon của từng căn nhà.
#   Bước 2: gọi U.S. Census Geocoder để tìm state_fips, county_fips, tract_fips.
#   Bước 3: tạo tract_geoid = state + county + tract.
#   Bước 4: dùng tract_geoid đó gọi ACS để lấy dữ liệu kinh tế - xã hội.
# Vì ghép theo Census Tract chính thức nên có cơ sở địa lý rõ ràng.
# ================================================================
def add_census(df, key):
    # Bước [2/5] CÓ gọi API ngoài.
    # Logic kiểm chứng:
    #   lat/lon của nhà -> Census Geocoder -> tract_geoid chính thức
    #   tract_geoid -> ACS -> income, poverty, unemployment, population...
    # Đây là bước cào/ghép dữ liệu kinh tế - xã hội theo đúng vị trí địa lý.
    print("\n[2/5] Census + ACS - external API crawling")
    df = df.copy()
    la, lo = latlon(df)
    coord_cache = load_cache("coord_to_tract.json")
    acs_cache = load_cache("acs.json")

    rows = []
    coords = df[[la, lo]].dropna().drop_duplicates()
    print(f"    Coordinates: {len(coords)}")

    for i, r in enumerate(coords.itertuples(index=False), 1):
        y, x = float(r[0]), float(r[1])
        ck = f"{y:.6f},{x:.6f}"

        if ck not in coord_cache:
            out = {"state_fips": np.nan, "county_fips": np.nan, "tract_fips": np.nan, "tract_geoid": np.nan, "tract_arealand_km2": np.nan}
            try:
                js = req_json(CENSUS_GEOCODER, {
                    "x": x, "y": y, "benchmark": "Public_AR_Current",
                    "vintage": "Current_Current", "format": "json"
                })
                t = js["result"]["geographies"]["Census Tracts"][0]
                st, co, tr = str(t["STATE"]).zfill(2), str(t["COUNTY"]).zfill(3), str(t["TRACT"]).zfill(6)
                area = num(t.get("AREALAND"))
                out = {"state_fips": st, "county_fips": co, "tract_fips": tr, "tract_geoid": st + co + tr,
                       "tract_arealand_km2": area / 1_000_000 if not pd.isna(area) else np.nan}
            except Exception as e:
                print(f"    Geocoder error {ck}: {e}")
            coord_cache[ck] = out

        item = dict(coord_cache[ck])
        item[la], item[lo] = y, x
        rows.append(item)

        if i % 100 == 0:
            print(f"    Geocoder: {i}/{len(coords)}")
            save_cache("coord_to_tract.json", coord_cache)
        time.sleep(0.15)

    save_cache("coord_to_tract.json", coord_cache)
    tract_df = pd.DataFrame(rows)

    vars_ = ["NAME","B19013_001E","B17001_001E","B17001_002E","B23025_003E","B23025_005E",
             "B01003_001E","B15003_001E","B15003_022E","B15003_023E","B15003_024E","B15003_025E"]
    acs_rows = []
    tracts = tract_df.dropna(subset=["tract_geoid"]).drop_duplicates(["state_fips", "county_fips", "tract_fips"])
    print(f"    Unique tracts: {len(tracts)}")

    for i, t in enumerate(tracts.itertuples(), 1):
        st, co, tr, geoid = t.state_fips, t.county_fips, t.tract_fips, t.tract_geoid

        if geoid not in acs_cache:
            blank = {"median_household_income": np.nan, "poverty_rate": np.nan,
                     "unemployment_rate": np.nan, "population": np.nan, "bachelor_or_higher_rate": np.nan}
            try:
                res = None
                for year in [2024, 2023]:
                    try:
                        rows = req_json(f"https://api.census.gov/data/{year}/acs/acs5", {
                            "get": ",".join(vars_), "for": f"tract:{tr}",
                            "in": f"state:{st} county:{co}", "key": key
                        }, retries=2)
                        if isinstance(rows, list) and len(rows) > 1:
                            res = dict(zip(rows[0], rows[1]))
                            break
                    except Exception:
                        pass
                if not res:
                    raise RuntimeError("No ACS data")

                bachelor_plus = sum(num(res.get(v)) for v in ["B15003_022E","B15003_023E","B15003_024E","B15003_025E"])
                acs_cache[geoid] = {
                    "median_household_income": num(res.get("B19013_001E")),
                    "poverty_rate": div(res.get("B17001_002E"), res.get("B17001_001E")),
                    "unemployment_rate": div(res.get("B23025_005E"), res.get("B23025_003E")),
                    "population": num(res.get("B01003_001E")),
                    "bachelor_or_higher_rate": div(bachelor_plus, res.get("B15003_001E")),
                }
            except Exception as e:
                print(f"    ACS error {geoid}: {e}")
                acs_cache[geoid] = blank

        row = dict(acs_cache[geoid])
        row.update({"state_fips": st, "county_fips": co, "tract_fips": tr, "tract_geoid": geoid})
        acs_rows.append(row)

        if i % 50 == 0:
            print(f"    ACS: {i}/{len(tracts)}")
            save_cache("acs.json", acs_cache)
        time.sleep(0.15)

    save_cache("acs.json", acs_cache)
    acs_df = pd.DataFrame(acs_rows)
    tract_df = tract_df.merge(acs_df, on=["state_fips", "county_fips", "tract_fips", "tract_geoid"], how="left")
    tract_df["population_density_per_km2"] = tract_df["population"] / tract_df["tract_arealand_km2"].replace(0, np.nan)
    return df.merge(tract_df, on=[la, lo], how="left")


# Tạo câu truy vấn Overpass QL cho OpenStreetMap.
# Query này tìm các node/way/relation trong bán kính 3km quanh tọa độ nhà.
# Sau đó code sẽ tự lọc lại theo từng bán kính nhỏ hơn cho từng loại tiện ích.
def osm_query(lat, lon):
    tags = [('amenity','school'),('amenity','college'),('amenity','university'),('amenity','kindergarten'),
            ('amenity','hospital'),('amenity','clinic'),('amenity','doctors'),('shop','supermarket'),
            ('shop','convenience'),('leisure','park'),('leisure','garden'),('leisure','recreation_ground'),
            ('highway','bus_stop'),('public_transport','platform'),('railway','station'),('railway','tram_stop'),
            ('railway','subway_entrance')]
    lines = ["[out:json][timeout:30];", "("]
    for k, v in tags:
        for typ in ["node", "way", "relation"]:
            lines.append(f'{typ}["{k}"="{v}"](around:3000,{lat},{lon});')
    lines += [");", "out center tags;"]
    return "\n".join(lines)


# Phân loại object OSM thành nhóm feature dùng cho bài toán giá nhà.
# Ví dụ: amenity=school -> school, shop=supermarket -> grocery.
def osm_cat(tags):
    a, s, l = tags.get("amenity"), tags.get("shop"), tags.get("leisure")
    h, p, r = tags.get("highway"), tags.get("public_transport"), tags.get("railway")
    out = []
    if a in {"school","college","university","kindergarten"}: out.append("school")
    if a in {"hospital","clinic","doctors"}: out.append("hospital")
    if s in {"supermarket","convenience"}: out.append("grocery")
    if l in {"park","garden","recreation_ground"}: out.append("park")
    if h == "bus_stop" or p == "platform" or r in {"station","tram_stop","subway_entrance"}: out.append("transit")
    return out


# Trả về bộ feature OSM rỗng khi API lỗi hoặc không có dữ liệu.
# Dùng NaN để phân biệt "không lấy được" với số lượng thật sự bằng 0.
def empty_osm():
    return {c: np.nan for c in ["school_count_2km","hospital_count_3km","grocery_count_1km","park_count_1km","transit_count_1km"]}


# ================================================================
# [3/5] ADD OPENSTREETMAP AMENITY FEATURES
# Dùng lat/lon để đếm tiện ích xung quanh căn nhà:
#   - school_count_2km: số trường học trong 2km
#   - hospital_count_3km: số bệnh viện/phòng khám trong 3km
#   - grocery_count_1km: số siêu thị/cửa hàng tiện lợi trong 1km
#   - park_count_1km: số công viên trong 1km
#   - transit_count_1km: số điểm giao thông công cộng trong 1km
# Cách này hợp lý vì giá nhà thường bị ảnh hưởng bởi tiện ích xung quanh.
# ================================================================
def add_osm(df, max_points=None):
    # Bước [3/5] CÓ gọi API ngoài.
    # Code gọi OpenStreetMap thông qua Overpass API để đếm tiện ích quanh tọa độ nhà.
    # Các bán kính được ghi rõ:
    #   grocery/park/transit: 1km
    #   school: 2km
    #   hospital: 3km
    print("\n[3/5] OSM amenities - external API crawling")
    df = df.copy()
    la, lo = latlon(df)
    df["osm_lat_grid"] = pd.to_numeric(df[la], errors="coerce").round(GRID)
    df["osm_lon_grid"] = pd.to_numeric(df[lo], errors="coerce").round(GRID)

    pts = df[["osm_lat_grid", "osm_lon_grid"]].dropna().drop_duplicates()
    if max_points:
        pts = pts.head(max_points)
        print(f"    Test mode: {max_points} grid points")
    print(f"    Grid points: {len(pts)}")

    cache = load_cache(f"osm_{GRID}.json")
    rows = []
    for i, r in enumerate(pts.itertuples(index=False), 1):
        y, x = float(r[0]), float(r[1])
        ck = f"{y:.{GRID}f},{x:.{GRID}f}"

        if ck not in cache:
            features = empty_osm()
            counts = {"school":0, "hospital":0, "grocery":0, "park":0, "transit":0}
            radii = {"school":2, "hospital":3, "grocery":1, "park":1, "transit":1}
            try:
                data = None
                for url in OVERPASS:
                    try:
                        resp = S.post(url, data={"data": osm_query(y, x)}, timeout=90)
                        if resp.status_code == 429:
                            time.sleep(60)
                            continue
                        resp.raise_for_status()
                        data = resp.json()
                        break
                    except Exception:
                        time.sleep(5)
                if data is None:
                    raise RuntimeError("Overpass failed")

                for el in data.get("elements", []):
                    cats = osm_cat(el.get("tags", {}) or {})
                    if not cats:
                        continue
                    ey, ex = el.get("lat"), el.get("lon")
                    if ey is None or ex is None:
                        center = el.get("center", {})
                        ey, ex = center.get("lat"), center.get("lon")
                    if ey is None or ex is None:
                        continue
                    d = hav(y, x, float(ey), float(ex))
                    for c in cats:
                        if d <= radii[c]:
                            counts[c] += 1
                features = {
                    "school_count_2km": counts["school"],
                    "hospital_count_3km": counts["hospital"],
                    "grocery_count_1km": counts["grocery"],
                    "park_count_1km": counts["park"],
                    "transit_count_1km": counts["transit"],
                }
                cache[ck] = features
            except Exception as e:
                print(f"    OSM error {ck}: {e}")
                features = empty_osm()
        else:
            features = cache[ck]

        rows.append({"osm_lat_grid": y, "osm_lon_grid": x, **features})

        if i % 25 == 0:
            print(f"    OSM: {i}/{len(pts)}")
            save_cache(f"osm_{GRID}.json", cache)
        time.sleep(OSM_SLEEP)

    save_cache(f"osm_{GRID}.json", cache)
    osm_df = pd.DataFrame(rows)
    return df.merge(osm_df, on=["osm_lat_grid", "osm_lon_grid"], how="left") if not osm_df.empty else df


# ================================================================
# [4/5] ADD FEMA NATIONAL RISK INDEX FEATURES
# Dùng tract_geoid đã lấy từ Census để gọi FEMA NRI.
# Các điểm rủi ro được lấy theo cùng Census Tract với căn nhà,
# nên không phải ghép ngẫu nhiên.
# ================================================================
def add_nri(df):
    # Bước [4/5] CÓ gọi API ngoài.
    # Code dùng tract_geoid đã lấy từ Census để gọi FEMA National Risk Index.
    # Nhờ vậy rủi ro wildfire/earthquake/flood được ghép theo mã vùng thống kê,
    # không phải ghép thủ công theo tên địa điểm.
    print("\n[4/5] FEMA NRI - external API crawling")
    if "tract_geoid" not in df.columns:
        print("    Missing tract_geoid, skip NRI")
        return df

    df = df.copy()
    fields = ["TRACTFIPS","WFIR_RISKS","ERQK_RISKS","RFLD_RISKS","CFLD_RISKS"]
    cache = load_cache("nri.json")
    rows = []
    tracts = df["tract_geoid"].dropna().astype(str).str.split(".").str[0].str.zfill(11).drop_duplicates()
    print(f"    Tracts: {len(tracts)}")

    for i, geoid in enumerate(tracts, 1):
        if geoid not in cache:
            try:
                js = req_json(f"{NRI_URL}/query", {
                    "f": "json", "where": f"TRACTFIPS='{geoid}'",
                    "outFields": ",".join(fields), "returnGeometry": "false",
                    "resultRecordCount": 1
                })
                cache[geoid] = js.get("features", [{}])[0].get("attributes", {}) if js.get("features") else {}
            except Exception as e:
                print(f"    NRI error {geoid}: {e}")
                cache[geoid] = {}

        a = cache[geoid]
        rows.append({
            "tract_geoid": geoid,
            "wildfire_risk_score": a.get("WFIR_RISKS", np.nan),
            "earthquake_risk_score": a.get("ERQK_RISKS", np.nan),
            "flood_risk_score": np.nanmax([num(a.get("RFLD_RISKS")), num(a.get("CFLD_RISKS"))]),
        })

        if i % 50 == 0:
            print(f"    NRI: {i}/{len(tracts)}")
            save_cache("nri.json", cache)
        time.sleep(0.1)

    save_cache("nri.json", cache)
    nri = pd.DataFrame(rows)
    df["tract_geoid"] = df["tract_geoid"].astype(str).str.split(".").str[0].str.zfill(11)
    return df.merge(nri, on="tract_geoid", how="left")


# ================================================================
# [5/5] ADD GEO DISTANCE FEATURES
# Tính khoảng cách từ căn nhà đến:
#   - thành phố lớn gần nhất ở California,
#   - sân bay lớn gần nhất,
#   - bờ biển California gần nhất.
# Khoảng cách được tính bằng Haversine nên có ý nghĩa địa lý thực tế.
# ================================================================
def add_geo(df):
    # GHI CHÚ QUAN TRỌNG:
    # Bước [5/5] KHÔNG gọi API và KHÔNG cào thêm nguồn mới.
    # Nó tự tính khoảng cách bằng công thức Haversine từ tọa độ căn nhà đến:
    #   - thành phố lớn gần nhất ở California,
    #   - sân bay lớn gần nhất,
    #   - một số điểm đại diện trên bờ biển California.
    # Vì vậy đây là feature engineering địa lý, không phải crawling.
    print("\n[5/5] Geo distance - calculated locally, not external crawling")
    df = df.copy()
    la, lo = latlon(df)
    cities = {"los_angeles":(34.0522,-118.2437), "san_francisco":(37.7749,-122.4194),
              "san_diego":(32.7157,-117.1611), "san_jose":(37.3382,-121.8863),
              "sacramento":(38.5816,-121.4944), "fresno":(36.7378,-119.7871)}
    airports = {"LAX":(33.9416,-118.4085), "SFO":(37.6213,-122.3790), "SAN":(32.7338,-117.1933),
                "SJC":(37.3639,-121.9289), "SMF":(38.6951,-121.5908), "OAK":(37.7126,-122.2197)}
    coast = [(32.5343,-117.1236),(33.6189,-117.9298),(34.0195,-118.4912),(35.2828,-120.6596),
             (36.6002,-121.8947),(37.7749,-122.4194),(39.4457,-123.8053),(41.7558,-124.2026)]

    city, cd, air, ad, coastd = [], [], [], [], []
    for y, x in zip(pd.to_numeric(df[la], errors="coerce"), pd.to_numeric(df[lo], errors="coerce")):
        if pd.isna(y) or pd.isna(x):
            city.append(np.nan); cd.append(np.nan); air.append(np.nan); ad.append(np.nan); coastd.append(np.nan); continue
        cdist = {k: hav(y, x, *v) for k, v in cities.items()}
        adist = {k: hav(y, x, *v) for k, v in airports.items()}
        cn, an = min(cdist, key=cdist.get), min(adist, key=adist.get)
        city.append(cn); cd.append(cdist[cn]); air.append(an); ad.append(adist[an])
        coastd.append(min(hav(y, x, *v) for v in coast))

    df["nearest_major_ca_city"] = city
    df["distance_to_nearest_major_ca_city_km"] = cd
    df["nearest_major_ca_airport"] = air
    df["distance_to_nearest_major_ca_airport_km"] = ad
    df["distance_to_ca_coast_approx_km"] = coastd
    return pd.concat([df, pd.get_dummies(df["nearest_major_ca_city"], prefix="nearest_city"),
                      pd.get_dummies(df["nearest_major_ca_airport"], prefix="nearest_airport")], axis=1)


# ================================================================
# MAIN PIPELINE
# Chạy lần lượt 5 nhóm feature:
#   1) Zillow basic features
#   2) Census + ACS socioeconomic features
#   3) OSM amenities features
#   4) FEMA NRI risk features
#   5) Geographic distance features
# Cuối cùng xuất ra CSV đã được làm giàu dữ liệu.
# ================================================================
def main():
    p = argparse.ArgumentParser()
    # File CSV đầu vào: dữ liệu nhà đất thô đã crawl từ Zillow.
    p.add_argument(
    "--input",
    default="/Users/leducanhtuan/Downloads/california_final_raw.csv"
)

    # File CSV đầu ra: dữ liệu sau khi thêm feature.
    # Lưu ý: hiện đang để giống input, nghĩa là có thể ghi đè file gốc.
    # Khi nộp bài nên đổi thành tên khác, ví dụ california_final_enriched.csv.
    p.add_argument(
    "--output",
    default="/Users/leducanhtuan/Downloads/california_final_raw.csv"
)
    # Census API key có thể truyền bằng tham số --census-key hoặc biến môi trường CENSUS_API_KEY.
    p.add_argument("--census-key", default=os.getenv("CENSUS_API_KEY"))
    # Các cờ skip dùng khi muốn test nhanh hoặc API bị lỗi.
    # Ví dụ: --skip-osm để bỏ phần OSM vì OSM thường chạy lâu nhất.
    p.add_argument("--skip-census", action="store_true")
    p.add_argument("--skip-osm", action="store_true")
    p.add_argument("--skip-nri", action="store_true")
    p.add_argument("--skip-geo", action="store_true")
    p.add_argument("--max-osm-points", type=int)
    a = p.parse_args()

    if not a.skip_census and not a.census_key:
        raise SystemExit("Thiếu Census key. Dùng --census-key KEY hoặc --skip-census.")

    print("=" * 60)
    print("ZILLOW SHORT FEATURE ENRICHMENT")
    print(f"Input : {a.input}")
    print(f"Output: {a.output}")
    print("=" * 60)

    # Đọc file Zillow raw/enriched ban đầu.
    df = pd.read_csv(a.input)
    print("Loaded:", df.shape)

    # Bắt đầu pipeline thêm feature. Mỗi hàm trả về DataFrame mới có thêm cột.
    df = add_basic(df)
    if not a.skip_census: df = add_census(df, a.census_key)
    else: print("\n[2/5] Skip Census")
    if not a.skip_osm: df = add_osm(df, a.max_osm_points)
    else: print("\n[3/5] Skip OSM")
    if not a.skip_nri: df = add_nri(df)
    else: print("\n[4/5] Skip NRI")
    if not a.skip_geo: df = add_geo(df)
    else: print("\n[5/5] Skip Geo")

    # Danh sách feature quan trọng cần kiểm tra sau khi crawl.
    # Khi trình bày với thầy, phần này dùng để chứng minh các cột đã được tạo ra
    # và có bao nhiêu dòng lấy được dữ liệu thật, không bị thiếu.
    wanted = ["median_household_income","poverty_rate","unemployment_rate","bachelor_or_higher_rate",
              "school_count_2km","hospital_count_3km","grocery_count_1km","park_count_1km","transit_count_1km",
              "wildfire_risk_score","earthquake_risk_score","flood_risk_score"]
    print("\nFeature check:")
    for c in wanted:
        print(("OK  " if c in df.columns else "MISS") + f" {c}" + (f": {df[c].notna().sum()}/{len(df)}" if c in df.columns else ""))

    # Tạo thư mục output nếu chưa tồn tại, rồi lưu CSV bằng utf-8-sig để Excel đọc tiếng Việt tốt hơn.
    Path(a.output).parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(a.output, index=False, encoding="utf-8-sig")
    print("\nDONE:", df.shape, "->", a.output)


if __name__ == "__main__":
    main()
