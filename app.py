from flask import Flask, render_template, request, jsonify, redirect, url_for
import sqlite3
import requests
import json
from datetime import datetime
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'

# Database configuration
DATABASE = 'hdb_flats.db'

def get_db_connection():
    """Get database connection"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize the database with HDB flats table"""
    conn = get_db_connection()
    conn.execute('''
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
            remaining_lease TEXT,
            resale_price REAL,
            month TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

@app.route('/')
def index():
    """Home page with search functionality"""
    return render_template('index.html')

@app.route('/search')
def search():
    """Search HDB flats based on query parameters"""
    query = request.args.get('q', '').strip()
    town = request.args.get('town', '').strip()
    flat_type = request.args.get('flat_type', '').strip()
    
    conn = get_db_connection()
    
    # Build dynamic query based on search parameters
    sql_query = '''
        SELECT * FROM hdb_flats 
        WHERE 1=1
    '''
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
    
    sql_query += ' ORDER BY resale_price DESC LIMIT 50'
    
    flats = conn.execute(sql_query, params).fetchall()
    conn.close()
    
    return render_template('search_results.html', flats=flats, query=query, town=town, flat_type=flat_type)

@app.route('/flat/<int:flat_id>')
def flat_detail(flat_id):
    """Show detailed information for a specific HDB flat"""
    conn = get_db_connection()
    flat = conn.execute('SELECT * FROM hdb_flats WHERE id = ?', (flat_id,)).fetchone()
    conn.close()
    
    if flat is None:
        return "Flat not found", 404
    
    return render_template('flat_detail.html', flat=flat)

@app.route('/api/search')
def api_search():
    """API endpoint for autocomplete search"""
    query = request.args.get('q', '').strip()
    
    if len(query) < 2:
        return jsonify([])
    
    conn = get_db_connection()
    results = conn.execute('''
        SELECT DISTINCT town, street_name, block, flat_type, resale_price, id
        FROM hdb_flats 
        WHERE town LIKE ? OR street_name LIKE ? OR block LIKE ?
        ORDER BY resale_price DESC
        LIMIT 10
    ''', (f'%{query}%', f'%{query}%', f'%{query}%')).fetchall()
    conn.close()
    
    return jsonify([dict(row) for row in results])

@app.route('/populate_data')
def populate_data():
    """Fetch HDB data from API and populate database"""
    try:
        # This is a placeholder for HDB resale API
        # In reality, you would use Singapore's HDB resale data API
        sample_data = [
            {
                'town': 'ANG MO KIO',
                'flat_type': '4 ROOM',
                'block': '221',
                'street_name': 'ANG MO KIO AVE 1',
                'storey_range': '04 TO 06',
                'floor_area_sqm': 90.0,
                'flat_model': 'New Generation',
                'lease_commence_date': 1979,
                'remaining_lease': '58 years 05 months',
                'resale_price': 428000.0,
                'month': '2024-01'
            },
            {
                'town': 'BEDOK',
                'flat_type': '3 ROOM',
                'block': '538',
                'street_name': 'BEDOK NORTH ST 3',
                'storey_range': '01 TO 03',
                'floor_area_sqm': 73.0,
                'flat_model': 'New Generation',
                'lease_commence_date': 1981,
                'remaining_lease': '60 years 02 months',
                'resale_price': 385000.0,
                'month': '2024-01'
            },
            {
                'town': 'BISHAN',
                'flat_type': '5 ROOM',
                'block': '230',
                'street_name': 'BISHAN ST 23',
                'storey_range': '07 TO 09',
                'floor_area_sqm': 110.0,
                'flat_model': 'Improved',
                'lease_commence_date': 1985,
                'remaining_lease': '64 years 08 months',
                'resale_price': 650000.0,
                'month': '2024-01'
            },
            {
                'town': 'CLEMENTI',
                'flat_type': '4 ROOM',
                'block': '312',
                'street_name': 'CLEMENTI AVE 4',
                'storey_range': '10 TO 12',
                'floor_area_sqm': 92.0,
                'flat_model': 'New Generation',
                'lease_commence_date': 1984,
                'remaining_lease': '63 years 11 months',
                'resale_price': 558000.0,
                'month': '2024-01'
            },
            {
                'town': 'JURONG WEST',
                'flat_type': '3 ROOM',
                'block': '675',
                'street_name': 'JURONG WEST ST 65',
                'storey_range': '04 TO 06',
                'floor_area_sqm': 68.0,
                'flat_model': 'New Generation',
                'lease_commence_date': 1988,
                'remaining_lease': '67 years 05 months',
                'resale_price': 325000.0,
                'month': '2024-01'
            }
        ]
        
        conn = get_db_connection()
        
        # Clear existing data
        conn.execute('DELETE FROM hdb_flats')
        
        # Insert sample data
        for flat in sample_data:
            conn.execute('''
                INSERT INTO hdb_flats (town, flat_type, block, street_name, storey_range, 
                                     floor_area_sqm, flat_model, lease_commence_date, 
                                     remaining_lease, resale_price, month)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                flat['town'], flat['flat_type'], flat['block'], flat['street_name'],
                flat['storey_range'], flat['floor_area_sqm'], flat['flat_model'],
                flat['lease_commence_date'], flat['remaining_lease'], 
                flat['resale_price'], flat['month']
            ))
        
        conn.commit()
        conn.close()
        
        return jsonify({'status': 'success', 'message': 'Database populated with sample HDB data'})
    
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

if __name__ == '__main__':
    init_db()
    app.run(debug=True)