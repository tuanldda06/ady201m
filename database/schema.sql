-- ============================================================
-- Database Schema for Zillow Real Estate Price Analysis
-- Designed for SQL Server
-- Generated from data_csv/zillow_final.csv
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

-- 1. Staging table: final cleaned Zillow dataset
CREATE TABLE dbo.raw_zillow_listings (
    raw_id INT IDENTITY(1,1) PRIMARY KEY,

    price FLOAT NULL,
    bed FLOAT NULL,
    bath FLOAT NULL,
    living FLOAT NULL,
    lot_sqft FLOAT NULL,
    lot_living FLOAT NULL,
    bed_bath FLOAT NULL,

    type_condo INT NULL CHECK (type_condo IN (0, 1)),
    type_manufactured INT NULL CHECK (type_manufactured IN (0, 1)),
    type_multi INT NULL CHECK (type_multi IN (0, 1)),
    type_single INT NULL CHECK (type_single IN (0, 1)),
    type_townhouse INT NULL CHECK (type_townhouse IN (0, 1)),

    lat FLOAT NULL,
    [long] FLOAT NULL,

    income FLOAT NULL,
    poverty FLOAT NULL,
    unemployment FLOAT NULL,
    [pop] FLOAT NULL,
    bachelor FLOAT NULL,
    rent FLOAT NULL,
    owner_occ FLOAT NULL,
    pop_density FLOAT NULL,

    risk_overall FLOAT NULL,
    risk_loss FLOAT NULL,
    risk_social FLOAT NULL,
    risk_resilience FLOAT NULL,
    risk_fire FLOAT NULL,
    risk_earthquake FLOAT NULL,
    risk_heat FLOAT NULL,

    dist_city FLOAT NULL,
    dist_airport FLOAT NULL,
    dist_coast FLOAT NULL
);
GO

-- 2. Home type dimension
CREATE TABLE dbo.home_types (
    home_type_id INT IDENTITY(1,1) PRIMARY KEY,
    home_type_name NVARCHAR(50) NOT NULL UNIQUE
);
GO

-- 3. Socioeconomic profile dimension
CREATE TABLE dbo.socioeconomic_profiles (
    socioeconomic_id INT IDENTITY(1,1) PRIMARY KEY,

    median_income_usd FLOAT NOT NULL,
    poverty_rate FLOAT NOT NULL CHECK (poverty_rate >= 0 AND poverty_rate <= 1),
    unemployment_rate FLOAT NOT NULL CHECK (unemployment_rate >= 0 AND unemployment_rate <= 1),
    population FLOAT NOT NULL CHECK (population >= 0),
    bachelor_rate FLOAT NOT NULL CHECK (bachelor_rate >= 0 AND bachelor_rate <= 1),
    median_rent_usd FLOAT NOT NULL,
    owner_occupied_rate FLOAT NOT NULL CHECK (owner_occupied_rate >= 0 AND owner_occupied_rate <= 1),
    population_density FLOAT NOT NULL,

    CONSTRAINT uq_socioeconomic_profiles UNIQUE (
        median_income_usd,
        poverty_rate,
        unemployment_rate,
        population,
        bachelor_rate,
        median_rent_usd,
        owner_occupied_rate,
        population_density
    )
);
GO

-- 4. Natural risk profile dimension
CREATE TABLE dbo.risk_profiles (
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
GO

-- 5. Central property fact table
CREATE TABLE dbo.properties (
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
        FOREIGN KEY (raw_id) REFERENCES dbo.raw_zillow_listings(raw_id),

    CONSTRAINT fk_properties_home_type
        FOREIGN KEY (home_type_id) REFERENCES dbo.home_types(home_type_id),

    CONSTRAINT fk_properties_socioeconomic
        FOREIGN KEY (socioeconomic_id) REFERENCES dbo.socioeconomic_profiles(socioeconomic_id),

    CONSTRAINT fk_properties_risk
        FOREIGN KEY (risk_profile_id) REFERENCES dbo.risk_profiles(risk_profile_id)
);
GO

-- 6. Property location table, one row per property
CREATE TABLE dbo.property_locations (
    property_id INT PRIMARY KEY,

    latitude FLOAT NOT NULL,
    longitude FLOAT NOT NULL,
    distance_to_city FLOAT NOT NULL CHECK (distance_to_city >= 0),
    distance_to_airport FLOAT NOT NULL CHECK (distance_to_airport >= 0),
    distance_to_coast FLOAT NOT NULL CHECK (distance_to_coast >= 0),

    CONSTRAINT fk_locations_properties
        FOREIGN KEY (property_id)
        REFERENCES dbo.properties(property_id)
        ON DELETE CASCADE
);
GO

-- 7. Indexes for common analytical queries
CREATE INDEX idx_properties_home_type ON dbo.properties(home_type_id);
CREATE INDEX idx_properties_price ON dbo.properties(price_usd);
CREATE INDEX idx_properties_socioeconomic ON dbo.properties(socioeconomic_id);
CREATE INDEX idx_properties_risk ON dbo.properties(risk_profile_id);
CREATE INDEX idx_locations_distance_city ON dbo.property_locations(distance_to_city);
CREATE INDEX idx_locations_distance_coast ON dbo.property_locations(distance_to_coast);
GO
