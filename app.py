from flask import Flask, render_template, request, jsonify, redirect, url_for
from Database import Database

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'

database = Database()

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
    
    flats = database.search_flats(query, town, flat_type)
    
    return render_template('search_results.html', flats=flats, query=query, town=town, flat_type=flat_type)

@app.route('/flat/<int:flat_id>')
def flat_detail(flat_id):
    """Show detailed information for a specific HDB flat"""
    flat = database.query_id(flat_id)
    if flat is None:
        return redirect(url_for('index'))
    return render_template('flat_detail.html', flat=flat)


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
        
        conn = database.connect()
        
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
    app.run(debug=True)