import psycopg2
import os


def get_db_connection():
    return psycopg2.connect(
        dbname=os.getenv('DB_NAME', ''),
        user=os.getenv('DB_USER', ''),
        password=os.getenv('DB_PASSWORD',''),
        host=os.getenv('DB_HOST', ''),
        port=os.getenv('DB_PORT', ''),
        sslmode=os.getenv('DB_SSLMODE', '')
    )

def drop_tables(conn, cursor):
    try:
        cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';")
        tables = [row[0] for row in cursor.fetchall()]


        for table in tables:
            cursor.execute(f"DROP TABLE IF EXISTS {table} CASCADE;")
        conn.commit()
        print("All tables dropped successfully.")
    except psycopg2.OperationalError as e:
        print(f"Error dropping tables: {e}")
        conn.rollback()

def create_tables(conn, cursor):


    tables_and_refs = '''

CREATE TABLE Project (
    id SERIAL PRIMARY KEY,
    gml_id VARCHAR(255) UNIQUE NOT NULL,
    description TEXT,
    name VARCHAR(255),
    name_code_space VARCHAR(255),
    internal_identifier VARCHAR(255),
    internal_identifier_code_space VARCHAR(255),
    address TEXT  -- Adding project address
);

CREATE TABLE SamplingFeature (
    gml_id VARCHAR(255) NOT NULL,
    name VARCHAR(255),
    internal_identifier VARCHAR(255),
    status VARCHAR(255),
    investigation_target VARCHAR(255),
    project_id INTEGER REFERENCES Project(id),
    total_measured_depth DOUBLE PRECISION,
    borehole_purpose VARCHAR(255),
    borehole_type VARCHAR(255),
    drill_start_date DATE,  -- Adding drill start date
    drill_completion_date DATE,  -- Adding drill completion date
    PRIMARY KEY (gml_id)
);

CREATE TABLE PointLocation (
    id SERIAL PRIMARY KEY,
    latitude DOUBLE PRECISION NOT NULL,
    longitude DOUBLE PRECISION NOT NULL,
    height DOUBLE PRECISION,
    srs_dimension INTEGER,
    srs_name VARCHAR(255),
    sampling_feature_id VARCHAR(255) REFERENCES SamplingFeature(gml_id)
);

CREATE TABLE DrivenPenetrationTest (
    id SERIAL PRIMARY KEY,
    gml_id VARCHAR(255) UNIQUE NOT NULL,
    test_procedure_method_name VARCHAR(255),
    accrediting_body VARCHAR(255),
    short_method_name VARCHAR(255),
    penetration_test_type VARCHAR(255),
    hammer_type VARCHAR(255),
    hammer_efficiency DOUBLE PRECISION,
    total_penetration DOUBLE PRECISION,
    point_location_id INTEGER REFERENCES PointLocation(id)
);

CREATE TABLE DriveSet (
    id SERIAL PRIMARY KEY,
    driven_penetration_test_id INTEGER REFERENCES DrivenPenetrationTest(id),
    drive_set_index INTEGER,
    blow_count INTEGER,
    penetration DOUBLE PRECISION
);

CREATE TABLE TestResult (
    id SERIAL PRIMARY KEY,
    gml_id VARCHAR(255) UNIQUE NOT NULL,
    driven_penetration_test_id INTEGER REFERENCES DrivenPenetrationTest(id)
);

CREATE TABLE LinearExtent (
    id SERIAL PRIMARY KEY,
    gml_id VARCHAR(255) UNIQUE NOT NULL,
    srs_dimension INTEGER,
    srs_name VARCHAR(255),
    pos_list TEXT,
    test_result_id INTEGER REFERENCES TestResult(id)
);

CREATE TABLE ResultSet (
    id SERIAL PRIMARY KEY,
    parameters VARCHAR(255),
    data_values TEXT,
    linear_extent_id INTEGER REFERENCES LinearExtent(id)
);

CREATE TABLE PropertyParameters (
    id SERIAL PRIMARY KEY,
    gml_id VARCHAR(255) UNIQUE NOT NULL,
    property_name VARCHAR(255),
    type_data VARCHAR(255),
    property_class VARCHAR(255),
    driven_penetration_test_id INTEGER REFERENCES DrivenPenetrationTest(id)
);

CREATE TABLE BusinessAssociate (
    id SERIAL PRIMARY KEY,
    gml_id VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL
);

-- New table to store predefined roles
CREATE TABLE RoleType (
    id SERIAL PRIMARY KEY,
    role_name VARCHAR(255) UNIQUE NOT NULL
);

-- Revised Role table with reference to RoleType
CREATE TABLE Role (
    id SERIAL PRIMARY KEY,
    role_type_id INTEGER REFERENCES RoleType(id),
    business_associate_id INTEGER REFERENCES BusinessAssociate(id),
    sampling_feature_id VARCHAR(255) REFERENCES SamplingFeature(gml_id)
);

-- New table for Rock Quality Designation (RQD) under LinearExtent
CREATE TABLE RockQualityDesignation (
    id SERIAL PRIMARY KEY,
    linear_extent_id INTEGER REFERENCES LinearExtent(id),
    rqd_value DOUBLE PRECISION,
    rqd_depth DOUBLE PRECISION,
    rqd_description TEXT
);

-- New table for Coring Data under LinearExtent
CREATE TABLE CoringData (
    id SERIAL PRIMARY KEY,
    linear_extent_id INTEGER REFERENCES LinearExtent(id),
    coring_method VARCHAR(255),
    core_diameter DOUBLE PRECISION,
    core_recovery DOUBLE PRECISION,
    core_description TEXT
);


-- Inserting into Project table
INSERT INTO Project (gml_id, description, name, name_code_space, internal_identifier, internal_identifier_code_space, address)
VALUES ('Project_600819', 'Route 676 Improvements', '111644', 'ODOT PID', '600819', 'Ohio State ID', '123 Main St, Columbus, OH');

-- Inserting into SamplingFeature table
INSERT INTO SamplingFeature (gml_id, name, internal_identifier, status, investigation_target, project_id, total_measured_depth, borehole_purpose, borehole_type, drill_start_date, drill_completion_date)
VALUES ('Location_B-001-0-20', 'B-001-0-20', 'B-001-0-20', 'Final', 'Natural Ground', 1, 41.00, 'Landslide', 'BH', '2023-01-15', '2023-01-20');

-- Inserting into PointLocation table
INSERT INTO PointLocation (latitude, longitude, height, srs_dimension, srs_name, sampling_feature_id)
VALUES (39.474660, -81.796858, 818.6, 3, 'urn:diggs:def:crs:DIGGS:0.1:4326_5702', 'Location_B-001-0-20');

-- Inserting into DrivenPenetrationTest table
INSERT INTO DrivenPenetrationTest (gml_id, test_procedure_method_name, accrediting_body, short_method_name, penetration_test_type, hammer_type, hammer_efficiency, total_penetration, point_location_id)
VALUES ('DGS490A-782-2E22-1768-42C85', 'Standard Test Method for Standard Penetration Test (SPT) and Split-Barrel Sampling of Soils', 'ASTM', 'ASTM 1586/1586M', 'SPT', 'CME Automatic', 84, 1.50, 1);

-- Inserting into DriveSet table
INSERT INTO DriveSet (driven_penetration_test_id, drive_set_index, blow_count, penetration)
VALUES (1, 1, 9, 0.5), (1, 2, 10, 0.6);

-- Inserting into TestResult table
INSERT INTO TestResult (gml_id, driven_penetration_test_id)
VALUES ('DGSA78B-2FE-1942', 1), ('DGSA78B-2FE-1943', 1);

-- Inserting into LinearExtent table
INSERT INTO LinearExtent (gml_id, srs_dimension, srs_name, pos_list, test_result_id)
VALUES ('LE001', 2, 'urn:ogc:def:crs:EPSG::4326', '1.0 1.5 2.0 2.5', 1);

-- Inserting into RockQualityDesignation table
INSERT INTO RockQualityDesignation (linear_extent_id, rqd_value, rqd_depth, rqd_description)
VALUES (1, 75.0, 10.0, 'Good quality rock');

-- Inserting into CoringData table
INSERT INTO CoringData (linear_extent_id, coring_method, core_diameter, core_recovery, core_description)
VALUES (1, 'Diamond Drilling', 50.0, 95.0, 'Recovered core in good condition');

'''
    
    # execute commands
    try:
        for command in tables_and_refs.split(";"):
            # Remove leading and trailing spaces to avoid empty statements when splitting the string by the semicolon.
            command = command.strip()

            # Check if the command is not an empty string (e.g., after a trailing semicolon)
            if command:
                cursor.execute(command)
        conn.commit()

    except psycopg2.OperationalError as e:
        print(f"Error creating tables or references: {e}")
        conn.rollback()



def main():
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                drop_tables(conn,cursor)
                create_tables(conn,cursor)
    except psycopg2.OperationalError as e:
        print(f"Unable to connect to the database: {e}")

if __name__ == "__main__":
    main()
