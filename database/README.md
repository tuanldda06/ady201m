# Zillow Real Estate Database

Thư mục này chứa các script SQL Server để thiết kế database quan hệ từ dataset cuối cùng `data_csv/zillow_final.csv`.

## Cấu Trúc File

```text
database/
├── create_database.sql
├── schema.sql
├── insert_data.sql
├── query_data.sql
└── README.md
```

| File | Chức năng |
|---|---|
| `create_database.sql` | Tạo database `ZillowRealEstateDB` nếu chưa tồn tại |
| `schema.sql` | Tạo bảng, khóa chính, khóa ngoại và index |
| `insert_data.sql` | Insert dữ liệu từ `zillow_final.csv` đã làm sạch |
| `query_data.sql` | Tạo view sạch và chạy các truy vấn phân tích |

## Dataset Được Insert

`insert_data.sql` được regenerate từ `data_csv/zillow_final.csv` và khớp với 32 cột của dataset cuối cùng.

| Bảng | Số dòng |
|---|---:|
| `raw_zillow_listings` | 4,251 |
| `properties` | 4,251 |
| `property_locations` | 4,251 |
| `home_types` | 6 |
| `socioeconomic_profiles` | 713 |
| `risk_profiles` | 1,002 |

## Thiết Kế Database

Database được tách từ một bảng phẳng thành các nhóm bảng theo ý nghĩa dữ liệu:

- `raw_zillow_listings`: lưu dataset cuối cùng ở dạng staging để đối chiếu.
- `home_types`: danh mục loại nhà từ các biến one-hot.
- `socioeconomic_profiles`: thông tin kinh tế - xã hội của khu vực.
- `risk_profiles`: các chỉ số rủi ro tự nhiên/khu vực.
- `properties`: bảng trung tâm chứa thông tin từng căn nhà và khóa ngoại đến các bảng dimension.
- `property_locations`: thông tin tọa độ và khoảng cách địa lý của từng căn nhà.

## ERD

```mermaid
erDiagram
    RAW_ZILLOW_LISTINGS ||--|| PROPERTIES : "source row"
    HOME_TYPES ||--o{ PROPERTIES : "classifies"
    SOCIOECONOMIC_PROFILES ||--o{ PROPERTIES : "describes area"
    RISK_PROFILES ||--o{ PROPERTIES : "scores risk"
    PROPERTIES ||--|| PROPERTY_LOCATIONS : "has location"

    RAW_ZILLOW_LISTINGS {
        INT raw_id PK
        FLOAT price
        FLOAT bed
        FLOAT bath
        FLOAT living
        FLOAT lot_sqft
        FLOAT lot_living
        FLOAT bed_bath
        INT type_condo
        INT type_manufactured
        INT type_multi
        INT type_single
        INT type_townhouse
        FLOAT lat
        FLOAT long
        FLOAT income
        FLOAT poverty
        FLOAT unemployment
        FLOAT pop
        FLOAT bachelor
        FLOAT rent
        FLOAT owner_occ
        FLOAT pop_density
        FLOAT risk_overall
        FLOAT risk_loss
        FLOAT risk_social
        FLOAT risk_resilience
        FLOAT risk_fire
        FLOAT risk_earthquake
        FLOAT risk_heat
        FLOAT dist_city
        FLOAT dist_airport
        FLOAT dist_coast
    }

    HOME_TYPES {
        INT home_type_id PK
        NVARCHAR home_type_name UK
    }

    SOCIOECONOMIC_PROFILES {
        INT socioeconomic_id PK
        FLOAT median_income_usd
        FLOAT poverty_rate
        FLOAT unemployment_rate
        FLOAT population
        FLOAT bachelor_rate
        FLOAT median_rent_usd
        FLOAT owner_occupied_rate
        FLOAT population_density
    }

    RISK_PROFILES {
        INT risk_profile_id PK
        FLOAT overall_risk_score
        FLOAT loss_risk_score
        FLOAT social_vulnerability_score
        FLOAT resilience_score
        FLOAT fire_risk_score
        FLOAT earthquake_risk_score
        FLOAT heat_risk_score
    }

    PROPERTIES {
        INT property_id PK
        INT raw_id FK
        INT home_type_id FK
        INT socioeconomic_id FK
        INT risk_profile_id FK
        FLOAT price_usd
        FLOAT bedrooms
        FLOAT bathrooms
        FLOAT living_area_sqft
        FLOAT lot_area_sqft
        FLOAT lot_to_living_ratio
        FLOAT bed_bath_ratio
    }

    PROPERTY_LOCATIONS {
        INT property_id PK, FK
        FLOAT latitude
        FLOAT longitude
        FLOAT distance_to_city
        FLOAT distance_to_airport
        FLOAT distance_to_coast
    }
```

## Cách Chạy

Chạy các script theo thứ tự trong SQL Server:

```text
create_database.sql
schema.sql
insert_data.sql
query_data.sql
```

`query_data.sql` tạo `dbo.view_property_clean`, sau đó trả lời các câu hỏi phân tích như loại nhà có giá cao nhất, phân khúc giá phổ biến, ảnh hưởng của thu nhập/rủi ro/khoảng cách đến giá nhà và giá trên mỗi sqft.
