# HDB Search Singapore - Flask Demo Application

A comprehensive Flask web application for searching HDB (Housing & Development Board) resale flats in Singapore. This demo showcases a complete real estate search platform with interactive features, responsive design, and database integration.

## Features

- **Interactive Search**: Real-time search suggestions with autocomplete
- **Advanced Filtering**: Search by town, flat type, and keywords
- **Detailed Property Views**: Comprehensive flat information with pricing analysis
- **Responsive Design**: Mobile-friendly interface using Bootstrap
- **Database Integration**: SQLite database with API data population
- **Modern UI/UX**: Clean, professional design with smooth animations

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

3. **Run the Flask application**:
   ```bash
   python app.py
   ```

4. **Open your browser** and navigate to:
   ```
   http://127.0.0.1:5000
   ```

5. **Populate sample data**:
   - Visit: http://127.0.0.1:5000/populate_data
   - Or click "Populate Data" in the navigation menu

## How to Use

### Home Page
- Use the search box to find HDB flats by location, street name, or block number
- Filter by town and flat type using the dropdown menus
- Get real-time search suggestions as you type

### Search Results
- Browse through paginated results showing flat summaries
- View key details: price, floor area, storey range, remaining lease
- Click "View Details" to see comprehensive flat information

### Flat Details
- Access complete property information
- View pricing analysis including price per square meter
- See property age, lease information, and neighborhood details
- Print or share property information

## Database Schema

The SQLite database contains the following HDB flat information:

- **Location**: Town, street name, block number
- **Property Details**: Flat type, floor area, storey range, flat model
- **Financial**: Resale price, sale month
- **Lease Information**: Lease commence date, remaining lease
- **Metadata**: Creation timestamp, unique ID

## API Endpoints

- `GET /` - Home page
- `GET /search` - Search results page
- `GET /flat/<id>` - Flat detail page
- `GET /api/search` - JSON search suggestions
- `GET /populate_data` - Populate database with sample data

## Technologies Used

- **Backend**: Flask 2.3.3, SQLite
- **Frontend**: HTML5, CSS3, JavaScript
- **UI Framework**: Bootstrap 5.1.3
- **Icons**: Font Awesome 6.0.0
- **Template Engine**: Jinja2

## Sample Data

The application includes sample HDB resale data from various Singapore towns including:
- Ang Mo Kio
- Bedok
- Bishan
- Clementi
- Jurong West

## Real API Integration

In a production environment, you would integrate with Singapore's official HDB resale data API:
- **Data.gov.sg**: https://data.gov.sg/dataset/resale-flat-prices
- Replace the sample data in `populate_data()` with actual API calls
- Implement scheduled data updates for real-time information

## Development Features

- **Debug Mode**: Enabled for development with hot reload
- **Error Handling**: Comprehensive error management
- **Responsive Design**: Mobile-first approach
- **Accessibility**: WCAG compliance considerations
- **Performance**: Optimized database queries and caching

## Production Deployment

For production deployment:

1. Set `app.run(debug=False)`
2. Use a production WSGI server like Gunicorn
3. Configure environment variables for sensitive data
4. Set up proper database with connection pooling
5. Implement user authentication and authorization
6. Add comprehensive logging and monitoring

## Future Enhancements

- User accounts and saved searches
- Property comparison features
- Market trend analysis and charts
- Email alerts for new listings
- Advanced mapping integration
- Mobile app development

## License

This is a demo application for educational purposes.

## Support

For questions or issues, please check the code comments or Flask documentation.