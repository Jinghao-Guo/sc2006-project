# HDB Search Singapore - Demo Application

A comprehensive Flask web application for searching HDB (Housing & Development Board) resale flats in Singapore. This demo showcases a complete real estate search platform with interactive features, responsive design, and database integration.

## Project Structure

```
sc2006/
├── app.py                  # Main Flask application
├── Database.py             # Database-related operations
├── dataPrepare.py          # Data preparation script
├── requirements.txt        # Python dependencies
├── scoreCalculator.py      # Score calculation logic
├── Userpreferences.py      # User preferences handling
├── templates/             # Jinja2 HTML templates
│   ├── base.html          # Base template with navigation
│   ├── compare_result.html # Comparison result page
│   ├── comparison.html    # Comparison page
│   ├── favorites.html     # Favorites page
│   ├── flat_detail.html   # Detailed flat information
│   ├── index.html         # Home page with search form
│   ├── preferences.html   # Preferences page
│   └── search_results.html # Search results listing
└── static/                # Static assets
    ├── css/
    │   └── style.css      # Custom styles
    └── js/
        └── script.js      # Interactive JavaScript
```

## Installation & Setup

1. **Clone or download the project files**

2. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Populate data from gov website**
   ```bash
   python dataPrepare.py
   ```
   This may take some time as dataset is very large

4. **Set your google map api key**
   ```bash
   export GOOGLE_MAPS_API_KEY="your-api-key-here"
   ```

5. **Run the Flask application**:
   ```bash
   python app.py
   ```

6. **Open your browser** and navigate to:
   ```
   http://127.0.0.1:5000
   ```
