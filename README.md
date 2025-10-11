# HDB Search Singapore - Flask Demo Application

A comprehensive Flask web application for searching HDB (Housing & Development Board) resale flats in Singapore. This demo showcases a complete real estate search platform with interactive features, responsive design, and database integration.

## Project Structure

```
sc2006/
├── app.py                  # Main Flask application
├── requirements.txt        # Python dependencies
├── hdb_flats.db           # SQLite database (created automatically)
├── templates/             # Jinja2 HTML templates
│   ├── base.html          # Base template with navigation
│   ├── index.html         # Home page with search form
│   ├── search_results.html # Search results listing
│   └── flat_detail.html   # Detailed flat information
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

4. **Run the Flask application**:
   ```bash
   python app.py
   ```

5. **Open your browser** and navigate to:
   ```
   http://127.0.0.1:5000
   ```