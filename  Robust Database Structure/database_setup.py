import sqlite3

def create_database():
    # Connect to SQLite database (or create it if it doesn't exist)
    conn = sqlite3.connect('/workspaces/Example_Database/Simple Database Structure/simple_geotechnical_database.db')
    cursor = conn.cursor()

    # Create Point_Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Point_Table (
        id VARCHAR PRIMARY KEY,
        geom TEXT,
        spt_type VARCHAR(256),
        spt_source VARCHAR(256),
        elevation NUMERIC,
        latitude DOUBLE NOT NULL,
        longitude DOUBLE NOT NULL,
        functionalkey VARCHAR(256),
        date_complete VARCHAR(256),
        total_depth NUMERIC
    )
    ''')

    # Create SPT_Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS SPT_Table (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sample_bottom NUMERIC,
        sample_top NUMERIC,
        functionalkey TEXT NOT NULL,
        sample_num INTEGER,
        sample_length NUMERIC,
        blow1 INTEGER,
        blow2 INTEGER,
        blow3 INTEGER,
        blow4 INTEGER,
        penetration1 NUMERIC,
        penetration2 NUMERIC,
        penetration3 NUMERIC,
        penetration4 NUMERIC,
        FOREIGN KEY (functionalkey) REFERENCES Point_Table(id)
    )
    ''')

    # Create Lith_Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Lith_Table (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sample_top NUMERIC,
        sample_bottom NUMERIC,
        desc_and_notes TEXT,
        functionalkey TEXT NOT NULL,
        FOREIGN KEY (functionalkey) REFERENCES Point_Table(id)
    )
    ''')

    # Commit changes and close connection
    conn.commit()
    conn.close()

    print("Database created successfully.")

if __name__ == "__main__":
    create_database()