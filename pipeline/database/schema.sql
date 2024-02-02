USE plants;
GO

IF OBJECT_ID(N's_delta.recording', N'U') IS NOT NULL
DROP TABLE s_delta.recording;
GO

IF OBJECT_ID(N's_delta.plant', N'U') IS NOT NULL
DROP TABLE s_delta.plant;
GO

IF OBJECT_ID(N's_delta.location', N'U') IS NOT NULL
DROP TABLE s_delta.location;
GO

IF OBJECT_ID(N's_delta.botanist', N'U') IS NOT NULL
DROP TABLE s_delta.botanist;
GO

CREATE TABLE s_delta.location (
    location_id INT NOT NULL IDENTITY(1, 1) PRIMARY KEY,
    region VARCHAR(100) UNIQUE,
    country VARCHAR(50),
    continent VARCHAR(20)
);
GO

CREATE TABLE s_delta.botanist(
    botanist_id INT NOT NULL IDENTITY(1, 1) PRIMARY KEY,
    name VARCHAR(100),
    email VARCHAR(100) UNIQUE,
    telephone_number VARCHAR(20)
);
GO

CREATE TABLE s_delta.plant(
    plant_id INT NOT NULL PRIMARY KEY,
    name VARCHAR(100) UNIQUE,
    location_id INT,
    botanist_id INT,
    FOREIGN KEY (location_id) REFERENCES s_delta.location (location_id) ON DELETE CASCADE,
    FOREIGN KEY (botanist_id) REFERENCES s_delta.botanist (botanist_id) ON DELETE CASCADE
);
GO

CREATE TABLE s_delta.recording(
    recording_id INT NOT NULL IDENTITY(1, 1) PRIMARY KEY,
    plant_id INT NOT NULL,
    soil_moisture FLOAT NOT NULL,
    temperature FLOAT,
    recording_taken DATETIME NOT NULL,
    last_watered DATETIME NOT NULL,
    FOREIGN KEY (plant_id) REFERENCES s_delta.plant (plant_id) ON DELETE CASCADE
);
GO
