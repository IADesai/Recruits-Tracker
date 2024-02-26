DROP DATABASE IF EXISTS thermomix;
CREATE DATABASE thermomix;
--\c thermomix;

DROP TABLE IF EXISTS roles;
DROP TABLE IF EXISTS members;
DROP TABLE IF EXISTS calendar_dates CASCADE;
DROP TABLE IF EXISTS member_details CASCADE;
DROP TABLE IF EXISTS member_sales CASCADE;
DROP TABLE IF EXISTS member_relationships CASCADE;

CREATE TABLE calendar_dates (
  training_date_id SERIAL PRIMARY KEY,
  training_date TEXT,
  start_date DATE,
  thirty_days DATE,
  ninety_days DATE,
  one_eighty_days DATE
);

CREATE TABLE roles (
  role_id SERIAL PRIMARY KEY,
  role_name TEXT
);

CREATE TABLE members (
  member_id SERIAL PRIMARY KEY,
  name TEXT,
  role_id_fk INTEGER REFERENCES roles(role_id)
);

CREATE TABLE member_details (
  member_id_details_fk INTEGER REFERENCES members(member_id) ON DELETE CASCADE,
  purchase TEXT,
  training_date_id_fk INTEGER REFERENCES calendar_dates(training_date_id)
);

CREATE TABLE member_sales (
  member_id_fk INTEGER REFERENCES members(member_id) ON DELETE CASCADE,
  newcomer_demo DATE,
  first_sale VARCHAR(20) CHECK (first_sale IS NULL OR first_sale = 'DNQ' OR TO_DATE(first_sale, 'YYYY-MM-DD HH24:MI:SS') IS NOT NULL),
  second_sale VARCHAR(20) CHECK (second_sale IS NULL OR second_sale = 'DNQ' OR TO_DATE(second_sale, 'YYYY-MM-DD HH24:MI:SS') IS NOT NULL),
  third_sale VARCHAR(20) CHECK (third_sale IS NULL OR third_sale = 'DNQ' OR TO_DATE(third_sale, 'YYYY-MM-DD HH24:MI:SS') IS NOT NULL),
  fourth_sale VARCHAR(20) CHECK (fourth_sale IS NULL OR fourth_sale = 'DNQ' OR TO_DATE(fourth_sale, 'YYYY-MM-DD HH24:MI:SS') IS NOT NULL),
  fifth_sale VARCHAR(20) CHECK (fifth_sale IS NULL OR fifth_sale = 'DNQ' OR TO_DATE(fifth_sale, 'YYYY-MM-DD HH24:MI:SS') IS NOT NULL),
  sixth_sale VARCHAR(20) CHECK (sixth_sale IS NULL OR sixth_sale = 'DNQ' OR TO_DATE(sixth_sale, 'YYYY-MM-DD HH24:MI:SS') IS NOT NULL),
  seventh_sale VARCHAR(20) CHECK (seventh_sale IS NULL OR seventh_sale = 'DNQ' OR TO_DATE(seventh_sale, 'YYYY-MM-DD HH24:MI:SS') IS NOT NULL),
  eighth_sale VARCHAR(20) CHECK (eighth_sale IS NULL OR eighth_sale = 'DNQ' OR TO_DATE(eighth_sale, 'YYYY-MM-DD HH24:MI:SS') IS NOT NULL)
);

CREATE TABLE member_relationships (
  member_relationship_id_fk INTEGER REFERENCES members(member_id) ON DELETE CASCADE,
  team_leader_id INTEGER,
  recruiting_advisor_id INTEGER
);

-- Index creation for faster lookups
CREATE INDEX idx_member_details_training_date_id_fk ON member_details(training_date_id_fk);
CREATE INDEX idx_member_details_member_id ON member_details(member_id_details_fk);
CREATE INDEX idx_member_sales_member_id ON member_sales(member_id_fk);
CREATE INDEX idx_member_relationships_member_id ON member_relationships(member_relationship_id_fk);

INSERT INTO roles(role_id, role_name) VALUES (1, 'Team Leader'),(2, 'Advisor');
INSERT INTO calendar_dates(training_date_id, training_date, start_date, thirty_days, ninety_days, one_eighty_days) VALUES (0, NULL, NULL, NULL, NULL, NULL);
INSERT INTO members(name, role_id_fk) VALUES ('Miranda Quantrill', 1),
('Ana Maria Lumina',1),
('Judi Hampton',1),
('Malgorzata Strzelecka',1),
('Alina Matei',1),
('Sara Joiner-Jarrett',1);