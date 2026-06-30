-- ============================================================
-- Database Schema for Zillow Real Estate Price Analysis
-- Designed for SQL Server
-- ============================================================

USE ZillowRealEstateDB;
GO

DROP VIEW IF EXISTS dbo.view_property_clean;
GO

DROP TABLE IF EXISTS dbo.property_locations;
DROP TABLE IF EXISTS dbo.properties;
DROP TABLE IF EXISTS dbo.risk_profiles;
DROP TABLE IF EXISTS dbo.socioeconomic_profiles;
DROP TABLE IF EXISTS dbo.home_types;
DROP TABLE IF EXISTS dbo.raw_zillow_listings;
GO


-- 1. Bảng staging: lưu dữ liệu thô từ CSV
CREATE TABLE raw_zillow_listings (
    raw_id INT IDENTITY(1,1) PRIMARY KEY,

    price FLOAT,
    bed FLOAT,
    bath FLOAT,
    living FLOAT,
    lot_sqft FLOAT,
    lot_living FLOAT,
    bed_bath FLOAT,

    type_condo INT CHECK (type_condo IN (0, 1)),
    type_manufactured INT CHECK (type_manufactured IN (0, 1)),
    type_multi INT CHECK (type_multi IN (0, 1)),
    type_single INT CHECK (type_single IN (0, 1)),
    type_townhouse INT CHECK (type_townhouse IN (0, 1)),

    lat FLOAT,
    [long] FLOAT,

    income FLOAT,
    poverty FLOAT,
    unemployment FLOAT,
    pop FLOAT,
    bachelor FLOAT,
    rent FLOAT,
    area_home_value FLOAT,
    owner_occ FLOAT,
    pop_density FLOAT,

    risk_overall FLOAT,
    risk_loss FLOAT,
    risk_social FLOAT,
    risk_resilience FLOAT,
    risk_fire FLOAT,
    risk_earthquake FLOAT,
    risk_heat FLOAT,

    dist_city FLOAT,
    dist_airport FLOAT,
    dist_coast FLOAT
);





-- 2. Bảng loại nhà
CREATE TABLE home_types (
    home_type_id INT IDENTITY(1,1) PRIMARY KEY,
    home_type_name NVARCHAR(100) NOT NULL UNIQUE
);




-- 3. Bảng thông tin kinh tế - xã hội
CREATE TABLE socioeconomic_profiles (
    socioeconomic_id INT IDENTITY(1,1) PRIMARY KEY,

    median_income_usd FLOAT NOT NULL,
    poverty_rate FLOAT NOT NULL CHECK (poverty_rate >= 0 AND poverty_rate <= 1),
    unemployment_rate FLOAT NOT NULL CHECK (unemployment_rate >= 0 AND unemployment_rate <= 1),
    population FLOAT NOT NULL CHECK (population >= 0),
    bachelor_rate FLOAT NOT NULL CHECK (bachelor_rate >= 0 AND bachelor_rate <= 1),
    median_rent_usd FLOAT NOT NULL,
    area_home_value FLOAT NOT NULL,
    owner_occupied_rate FLOAT NOT NULL CHECK (owner_occupied_rate >= 0 AND owner_occupied_rate <= 1),
    population_density FLOAT NOT NULL,

    CONSTRAINT uq_socioeconomic_profiles UNIQUE (
        median_income_usd,
        poverty_rate,
        unemployment_rate,
        population,
        bachelor_rate,
        median_rent_usd,
        area_home_value,
        owner_occupied_rate,
        population_density
    )
);




-- 4. Bảng chỉ số rủi ro khu vực
CREATE TABLE risk_profiles (
    risk_profile_id INT IDENTITY(1,1) PRIMARY KEY,

    overall_risk_score FLOAT NOT NULL CHECK (overall_risk_score >= 0 AND overall_risk_score <= 100),
    loss_risk_score FLOAT NOT NULL CHECK (loss_risk_score >= 0 AND loss_risk_score <= 100),
    social_vulnerability_score FLOAT NOT NULL CHECK (social_vulnerability_score >= 0 AND social_vulnerability_score <= 100),
    resilience_score FLOAT NOT NULL CHECK (resilience_score >= 0 AND resilience_score <= 100),
    fire_risk_score FLOAT NOT NULL CHECK (fire_risk_score >= 0 AND fire_risk_score <= 100),
    earthquake_risk_score FLOAT NOT NULL CHECK (earthquake_risk_score >= 0 AND earthquake_risk_score <= 100),
    heat_risk_score FLOAT NOT NULL CHECK (heat_risk_score >= 0 AND heat_risk_score <= 100),

    CONSTRAINT uq_risk_profiles UNIQUE (
        overall_risk_score,
        loss_risk_score,
        social_vulnerability_score,
        resilience_score,
        fire_risk_score,
        earthquake_risk_score,
        heat_risk_score
    )
);



-- 5. Bảng chính: thông tin từng căn nhà
CREATE TABLE properties (
    property_id INT IDENTITY(1,1) PRIMARY KEY,

    raw_id INT NOT NULL UNIQUE,
    home_type_id INT NOT NULL,
    socioeconomic_id INT NOT NULL,
    risk_profile_id INT NOT NULL,

    price_usd FLOAT NOT NULL CHECK (price_usd >= 0),
    bedrooms FLOAT NOT NULL CHECK (bedrooms >= 0),
    bathrooms FLOAT NOT NULL CHECK (bathrooms >= 0),
    living_area_sqft FLOAT NOT NULL CHECK (living_area_sqft >= 0),
    lot_area_sqft FLOAT NOT NULL CHECK (lot_area_sqft >= 0),
    lot_to_living_ratio FLOAT NOT NULL CHECK (lot_to_living_ratio >= 0),
    bed_bath_ratio FLOAT NOT NULL CHECK (bed_bath_ratio >= 0),

    CONSTRAINT fk_properties_raw
        FOREIGN KEY (raw_id)
        REFERENCES raw_zillow_listings(raw_id),

    CONSTRAINT fk_properties_home_type
        FOREIGN KEY (home_type_id)
        REFERENCES home_types(home_type_id),

    CONSTRAINT fk_properties_socioeconomic
        FOREIGN KEY (socioeconomic_id)
        REFERENCES socioeconomic_profiles(socioeconomic_id),

    CONSTRAINT fk_properties_risk
        FOREIGN KEY (risk_profile_id)
        REFERENCES risk_profiles(risk_profile_id)
);





-- 6. Bảng vị trí nhà
-- Quan hệ 1-1 với properties
CREATE TABLE property_locations (
    property_id INT PRIMARY KEY,

    latitude FLOAT NOT NULL,
    longitude FLOAT NOT NULL,
    distance_to_city FLOAT NOT NULL CHECK (distance_to_city >= 0),
    distance_to_airport FLOAT NOT NULL CHECK (distance_to_airport >= 0),
    distance_to_coast FLOAT NOT NULL CHECK (distance_to_coast >= 0),

    CONSTRAINT fk_locations_properties
        FOREIGN KEY (property_id)
        REFERENCES properties(property_id)
        ON DELETE CASCADE
);



-- 7. Index để truy vấn nhanh hơn
CREATE INDEX idx_properties_home_type
ON properties(home_type_id);

CREATE INDEX idx_properties_price
ON properties(price_usd);

CREATE INDEX idx_properties_socioeconomic
ON properties(socioeconomic_id);

CREATE INDEX idx_properties_risk
ON properties(risk_profile_id);

CREATE INDEX idx_locations_distance_city
ON property_locations(distance_to_city);