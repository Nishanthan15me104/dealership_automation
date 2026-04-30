-- database.sql

-- Drop tables if they exist to ensure a fresh start
DROP TABLE IF EXISTS dealerships;
DROP TABLE IF EXISTS brands;

CREATE TABLE brands (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL
);

CREATE TABLE dealerships (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    brand_id INTEGER,
    name VARCHAR(100) NOT NULL,
    panel_image_path VARCHAR(255),
    logo_image_path VARCHAR(255),
    FOREIGN KEY (brand_id) REFERENCES brands(id)
);

-- Insert Brand Data
INSERT INTO brands (id, name) VALUES (1, 'Tata');
INSERT INTO brands (id, name) VALUES (2, 'Volkswagen');

-- Insert Dealership Data (Matching your VS Code screenshot paths)
-- Brand 1 is Tata, Brand 2 is Volkswagen
INSERT INTO dealerships (brand_id, name, panel_image_path, logo_image_path) VALUES 
(1, 'Bellad Tata', 'assets/Dealership-panels/Tata-dealers/Bellad-tata/template.png', 'assets/Dealership-panels/Tata-dealers/Bellad-tata/logo-dark.png'),
(2, 'VW Autobhan', 'assets/Dealership-panels/VW-dealers/VW-Autobhan/template.png', 'assets/Dealership-panels/VW-dealers/VW-Autobhan/logo-dark.png'),
(2, 'VW Hubli', 'assets/Dealership-panels/VW-dealers/VW-Hubli/template.png', 'assets/Dealership-panels/VW-dealers/VW-Hubli/logo-dark.png');