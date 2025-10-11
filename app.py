from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from Database import database
from Userpreferences import user_preferences

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'





@app.route('/')
def index():
    """Home page with search functionality"""
    preferences = user_preferences.get_preferences()
    return render_template('index.html', preferences=preferences, has_preferences=user_preferences.has_preferences())

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

@app.route('/preferences', methods=['GET', 'POST'])
def preferences():
    """Manage user preferences"""
    if request.method == 'POST':
        # Set preferences from form data
        flat_type = request.form.get('flat_type', '').strip()
        storey_range = request.form.get('storey_range', '').strip()
        floor_area_sqm = request.form.get('floor_area_sqm', '').strip()
        flat_model = request.form.get('flat_model', '').strip()
        price_range = request.form.get('price_range', '').strip()
        
        user_preferences.set_preferences(flat_type, storey_range, floor_area_sqm, flat_model, price_range)
        flash('Your preferences have been saved successfully!', 'success')
        return redirect(url_for('index'))
    
    # GET request - show current preferences
    current_preferences = user_preferences.get_preferences()
    return render_template('preferences.html', preferences=current_preferences)

@app.route('/clear_preferences', methods=['POST'])
def clear_preferences():
    """Clear all user preferences"""
    user_preferences.set_preferences()
    flash('Your preferences have been cleared.', 'info')
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)