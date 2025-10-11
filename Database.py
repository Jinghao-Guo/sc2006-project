import sqlite3

# Database configuration
DATABASE = 'hdb_flats.db'

class Database:
    """Database connection handler"""
    
    def __init__(self, db_path=DATABASE):
        self.db_path = db_path
        self.connection = None
    
    def connect(self):
        """Establish a database connection"""
        if self.connection is None:
            self.connection = sqlite3.connect(self.db_path)
            self.connection.row_factory = sqlite3.Row
    
    def close(self):
        """Close the database connection"""
        if self.connection:
            self.connection.close()
            self.connection = None
    
    def initdb(self):
        """Initialize the database with HDB flats table"""
        self.connect()
        self.connection.execute('''
            CREATE TABLE IF NOT EXISTS hdb_flats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                town TEXT NOT NULL,
                flat_type TEXT NOT NULL,
                block TEXT NOT NULL,
                street_name TEXT NOT NULL,
                storey_range TEXT NOT NULL,
                floor_area_sqm REAL,
                flat_model TEXT,
                lease_commence_date INTEGER,
                resale_price REAL
                )
        ''')
        self.connection.commit()
        self.close()
    def insert_flat(self, town, flat_type, block, street_name, storey_range,
                    floor_area_sqm, flat_model, lease_commence_date, resale_price):
        """Insert a new flat record into the database"""
        self.connect()
        self.connection.execute('''
            INSERT INTO hdb_flats (town, flat_type, block, street_name, storey_range,
                                   floor_area_sqm, flat_model, lease_commence_date,
                                   resale_price)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (town, flat_type, block, street_name, storey_range,
              floor_area_sqm, flat_model, lease_commence_date, resale_price))
        self.connection.commit()
        self.close()

    def search_flats(self, query, town, flat_type):
        """Search for HDB flats with given filters and sorting"""
        self.connect()
        sql_query = "SELECT * FROM hdb_flats WHERE 1=1"
        params = []

        if query:
            sql_query += ' AND (town LIKE ? OR street_name LIKE ? OR block LIKE ?)'
            params.extend([f'%{query}%', f'%{query}%', f'%{query}%'])
    
        if town:
            sql_query += ' AND town LIKE ?'
            params.append(f'%{town}%')
        
        if flat_type:
            sql_query += ' AND flat_type LIKE ?'
            params.append(f'%{flat_type}%')
        
        sql_query += f' ORDER BY resale_price DESC LIMIT 10'
        
        flats = self.connection.execute(sql_query, params).fetchall()
        self.close()
        return flats
    
    def query_id(self, id):
        """Query a flat by its ID"""
        self.connect()
        flat = self.connection.execute('SELECT * FROM hdb_flats WHERE id = ?', (id,)).fetchone()
        self.close()
        return flat
    def clear_data(self):
        """Clear all data from the hdb_flats table"""
        self.connect()
        self.connection.execute('DELETE FROM hdb_flats')
        self.connection.commit()
        self.close()

database = Database()
    
