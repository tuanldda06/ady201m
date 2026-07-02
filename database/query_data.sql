-- ============================================================
-- SQL DATA WRANGLING & ANALYSIS QUERIES
-- Dataset: Zillow Real Estate Price Analysis
-- Designed for SQL Server
-- ============================================================

USE ZillowRealEstateDB;
GO


-- ============================================================
-- PHẦN 1: KIỂM TRA THỐNG KÊ TỔNG QUAN
-- ============================================================

-- 1.1. Kiểm tra số lượng dòng trong các bảng
SELECT 'raw_zillow_listings' AS table_name, COUNT(*) AS total_rows FROM dbo.raw_zillow_listings
UNION ALL
SELECT 'home_types' AS table_name, COUNT(*) AS total_rows FROM dbo.home_types
UNION ALL
SELECT 'socioeconomic_profiles' AS table_name, COUNT(*) AS total_rows FROM dbo.socioeconomic_profiles
UNION ALL
SELECT 'risk_profiles' AS table_name, COUNT(*) AS total_rows FROM dbo.risk_profiles
UNION ALL
SELECT 'properties' AS table_name, COUNT(*) AS total_rows FROM dbo.properties
UNION ALL
SELECT 'property_locations' AS table_name, COUNT(*) AS total_rows FROM dbo.property_locations;
GO


-- 1.2. Kiểm tra phân bổ loại nhà
SELECT
    h.home_type_name,
    COUNT(*) AS property_count,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM dbo.properties), 2) AS percentage
FROM dbo.properties p
JOIN dbo.home_types h
    ON p.home_type_id = h.home_type_id
GROUP BY h.home_type_name
ORDER BY property_count DESC;
GO


-- 1.3. Kiểm tra khoảng giá nhà
SELECT
    COUNT(*) AS total_properties,
    ROUND(MIN(price_usd), 2) AS min_price,
    ROUND(AVG(price_usd), 2) AS avg_price,
    ROUND(MAX(price_usd), 2) AS max_price
FROM dbo.properties;
GO


-- ============================================================
-- PHẦN 2: DATA WRANGLING & DATA CLEANING VIA SQL VIEW
-- ============================================================

-- Tạo view dữ liệu sạch để phục vụ phân tích
-- View này join các bảng đã chuẩn hóa lại với nhau
DROP VIEW IF EXISTS dbo.view_property_clean;
GO

CREATE VIEW dbo.view_property_clean AS
SELECT
    p.property_id,
    h.home_type_name,

    p.price_usd,

    -- Phân nhóm giá nhà
    CASE
        WHEN p.price_usd < 500000 THEN 'Low price'
        WHEN p.price_usd < 1000000 THEN 'Medium price'
        WHEN p.price_usd < 2000000 THEN 'High price'
        ELSE 'Luxury price'
    END AS price_segment,

    p.bedrooms,
    p.bathrooms,
    p.living_area_sqft,
    p.lot_area_sqft,
    p.lot_to_living_ratio,
    p.bed_bath_ratio,

    l.latitude,
    l.longitude,
    l.distance_to_city,
    l.distance_to_airport,
    l.distance_to_coast,

    s.median_income_usd,
    s.poverty_rate,
    s.unemployment_rate,
    s.population,
    s.bachelor_rate,
    s.median_rent_usd,
    s.owner_occupied_rate,
    s.population_density,

    r.overall_risk_score,
    r.loss_risk_score,
    r.social_vulnerability_score,
    r.resilience_score,
    r.fire_risk_score,
    r.earthquake_risk_score,
    r.heat_risk_score

FROM dbo.properties p
JOIN dbo.home_types h
    ON p.home_type_id = h.home_type_id
JOIN dbo.property_locations l
    ON p.property_id = l.property_id
JOIN dbo.socioeconomic_profiles s
    ON p.socioeconomic_id = s.socioeconomic_id
JOIN dbo.risk_profiles r
    ON p.risk_profile_id = r.risk_profile_id;
GO


-- 2.1. Xem thử dữ liệu sạch sau khi join
SELECT TOP 10 *
FROM dbo.view_property_clean;
GO


-- ============================================================
-- PHẦN 3: CÁC CÂU HỎI PHÂN TÍCH QUAN TRỌNG
-- ============================================================

-- Câu hỏi 1: Loại nhà nào có giá trung bình và trung vị cao nhất?
SELECT
    home_type_name,
    COUNT(*) AS total_properties,
    ROUND(AVG(price_usd), 2) AS avg_price,
    ROUND(MAX(median_price), 2) AS median_price,
    ROUND(MIN(price_usd), 2) AS min_price,
    ROUND(MAX(price_usd), 2) AS max_price,
    ROUND(AVG(price_usd / NULLIF(living_area_sqft, 0)), 2) AS avg_price_per_sqft
FROM (
    SELECT
        home_type_name,
        price_usd,
        living_area_sqft,
        PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY price_usd)
            OVER (PARTITION BY home_type_name) AS median_price
    FROM dbo.view_property_clean
) AS x
GROUP BY home_type_name
ORDER BY avg_price DESC;
GO


-- Câu hỏi 2: Dataset có nhiều nhà thuộc phân khúc giá nào?
SELECT
    price_segment,
    COUNT(*) AS total_properties,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM dbo.view_property_clean), 2) AS percentage,
    ROUND(AVG(price_usd), 2) AS avg_price
FROM dbo.view_property_clean
GROUP BY price_segment
ORDER BY avg_price;
GO


-- Câu hỏi 3: Khu vực thu nhập cao có giá nhà cao hơn không?
SELECT
    CASE
        WHEN median_income_usd < 60000 THEN 'Low income area'
        WHEN median_income_usd < 100000 THEN 'Middle income area'
        ELSE 'High income area'
    END AS income_group,

    COUNT(*) AS total_properties,
    ROUND(AVG(median_income_usd), 2) AS avg_income,
    ROUND(AVG(price_usd), 2) AS avg_price
FROM dbo.view_property_clean
GROUP BY
    CASE
        WHEN median_income_usd < 60000 THEN 'Low income area'
        WHEN median_income_usd < 100000 THEN 'Middle income area'
        ELSE 'High income area'
    END
ORDER BY avg_income;
GO


-- Câu hỏi 4: Rủi ro khu vực ảnh hưởng thế nào đến giá nhà?
SELECT
    CASE
        WHEN overall_risk_score < 25 THEN 'Low risk'
        WHEN overall_risk_score < 50 THEN 'Medium risk'
        WHEN overall_risk_score < 75 THEN 'High risk'
        ELSE 'Very high risk'
    END AS risk_group,

    COUNT(*) AS total_properties,
    ROUND(AVG(overall_risk_score), 2) AS avg_risk_score,
    ROUND(AVG(price_usd), 2) AS avg_price,
    ROUND(AVG(fire_risk_score), 2) AS avg_fire_risk,
    ROUND(AVG(earthquake_risk_score), 2) AS avg_earthquake_risk,
    ROUND(AVG(heat_risk_score), 2) AS avg_heat_risk
FROM dbo.view_property_clean
GROUP BY
    CASE
        WHEN overall_risk_score < 25 THEN 'Low risk'
        WHEN overall_risk_score < 50 THEN 'Medium risk'
        WHEN overall_risk_score < 75 THEN 'High risk'
        ELSE 'Very high risk'
    END
ORDER BY avg_risk_score;
GO


-- Câu hỏi 5: Nhà gần thành phố có giá cao hơn không?
SELECT
    CASE
        WHEN distance_to_city < 10 THEN 'Near city'
        WHEN distance_to_city < 25 THEN 'Medium distance'
        WHEN distance_to_city < 50 THEN 'Far from city'
        ELSE 'Very far from city'
    END AS city_distance_group,

    COUNT(*) AS total_properties,
    ROUND(AVG(distance_to_city), 2) AS avg_distance_to_city,
    ROUND(AVG(price_usd), 2) AS avg_price,
    ROUND(AVG(living_area_sqft), 2) AS avg_living_area_sqft
FROM dbo.view_property_clean
GROUP BY
    CASE
        WHEN distance_to_city < 10 THEN 'Near city'
        WHEN distance_to_city < 25 THEN 'Medium distance'
        WHEN distance_to_city < 50 THEN 'Far from city'
        ELSE 'Very far from city'
    END
ORDER BY avg_distance_to_city;
GO


-- Câu hỏi 6: Nhà gần biển có giá cao hơn không?
SELECT
    CASE
        WHEN distance_to_coast < 10 THEN 'Near coast'
        WHEN distance_to_coast < 25 THEN 'Medium distance'
        WHEN distance_to_coast < 75 THEN 'Far from coast'
        ELSE 'Very far from coast'
    END AS coast_distance_group,

    COUNT(*) AS total_properties,
    ROUND(AVG(distance_to_coast), 2) AS avg_distance_to_coast,
    ROUND(AVG(price_usd), 2) AS avg_price,
    ROUND(MAX(median_price), 2) AS median_price
FROM (
    SELECT
        price_usd,
        distance_to_coast,
        PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY price_usd)
            OVER (
                PARTITION BY
                    CASE
                        WHEN distance_to_coast < 10 THEN 'Near coast'
                        WHEN distance_to_coast < 25 THEN 'Medium distance'
                        WHEN distance_to_coast < 75 THEN 'Far from coast'
                        ELSE 'Very far from coast'
                    END
            ) AS median_price
    FROM dbo.view_property_clean
) AS x
GROUP BY
    CASE
        WHEN distance_to_coast < 10 THEN 'Near coast'
        WHEN distance_to_coast < 25 THEN 'Medium distance'
        WHEN distance_to_coast < 75 THEN 'Far from coast'
        ELSE 'Very far from coast'
    END
ORDER BY avg_distance_to_coast;
GO


-- Câu hỏi 7: Giá trên mỗi sqft thay đổi như thế nào theo loại nhà?
SELECT
    home_type_name,
    COUNT(*) AS total_properties,
    ROUND(AVG(living_area_sqft), 2) AS avg_living_area_sqft,
    ROUND(AVG(price_usd / NULLIF(living_area_sqft, 0)), 2) AS avg_price_per_sqft,
    ROUND(MIN(price_usd / NULLIF(living_area_sqft, 0)), 2) AS min_price_per_sqft,
    ROUND(MAX(price_usd / NULLIF(living_area_sqft, 0)), 2) AS max_price_per_sqft
FROM dbo.view_property_clean
GROUP BY home_type_name
ORDER BY avg_price_per_sqft DESC;
GO


-- Câu hỏi 8: Các biến kinh tế - xã hội khác nhau thế nào theo phân khúc giá?
SELECT
    price_segment,
    COUNT(*) AS total_properties,
    ROUND(AVG(price_usd), 2) AS avg_price,
    ROUND(AVG(median_income_usd), 2) AS avg_income,
    ROUND(AVG(bachelor_rate), 4) AS avg_bachelor_rate,
    ROUND(AVG(poverty_rate), 4) AS avg_poverty_rate,
    ROUND(AVG(median_rent_usd), 2) AS avg_rent
FROM dbo.view_property_clean
GROUP BY price_segment
ORDER BY avg_price;
GO
