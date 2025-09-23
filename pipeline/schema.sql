IF OBJECT_ID('beta.Reading', 'U') IS NOT NULL
    DROP TABLE beta.Reading

IF OBJECT_ID('beta.Botanist', 'U') IS NOT NULL
    DROP TABLE beta.Botanist

IF OBJECT_ID('beta.Plant', 'U') IS NOT NULL
    DROP TABLE beta.Plant

IF OBJECT_ID('beta.City', 'U') IS NOT NULL
    DROP TABLE beta.City

IF OBJECT_ID('beta.Country', 'U') IS NOT NULL
    DROP TABLE beta.Country

CREATE TABLE beta.Country (
    country_id INT IDENTITY(1,1) PRIMARY KEY,
    country_name VARCHAR NOT NULL
);

CREATE TABLE beta.City (
    city_id INT IDENTITY(1,1) PRIMARY KEY,
    city_name VARCHAR NOT NULL,
    lat FLOAT NOT NULL,
    long FLOAT NOT NULL,
    country_id INT NOT NULL,
    CONSTRAINT FK_City_Country FOREIGN KEY (country_id)
        REFERENCES beta.Country(country_id)
);

CREATE TABLE beta.Plant (
    plant_id INT IDENTITY(1,1) PRIMARY KEY,
    plant_name VARCHAR NOT NULL,
    scientific_name VARCHAR NOT NULL,
    last_watered DATETIME NOT NULL,
    city_id INT NOT NULL,
    CONSTRAINT FK_Plant_City FOREIGN KEY (city_id)
        REFERENCES beta.City(city_id)
);

CREATE TABLE beta.Botanist (
    botanist_id INT IDENTITY(1,1) PRIMARY KEY,
    first_name VARCHAR NOT NULL,
    last_name VARCHAR NOT NULL,
    email VARCHAR NOT NULL,
    phone_number VARCHAR NOT NULL
);

CREATE TABLE beta.Reading (
    reading_id INT IDENTITY(1,1) PRIMARY KEY,
    temperature FLOAT NOT NULL,
    soil_moisture FLOAT NOT NULL,
    recording_taken DATETIME NOT NULL,
    plant_id INT NOT NULL,
    botanist_id INT NOT NULL,
    CONSTRAINT FK_Reading_Plant FOREIGN KEY (plant_id)
        REFERENCES beta.Plant(plant_id),
    CONSTRAINT FK_Reading_Botanist FOREIGN KEY (botanist_id)
        REFERENCES beta.Botanist(botanist_id)
);