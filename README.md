# Property Calculator

A Flask-based web application for real estate property calculations, mapping, and financial analysis.

## Features

- 🏠 Property acquisition cost calculations
- 💰 Operating expenses tracking
- 📊 Cash flow analysis
- 📈 Annual growth projections
- 🗺️ Interactive property map with real estate data
- 👤 User authentication and management
- 💳 Credit score analysis and loan eligibility

## Quick Start

### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd property_calculator
   ```

2. **Set up virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment (optional)**
   ```bash
   cp .env.example .env
   # Edit .env with your preferred settings
   ```

5. **Run the application**
   ```bash
   python run.py
   ```

   Or run directly:
   ```bash
   python main.py
   ```

6. **Access the application**
   Open your browser and go to: http://127.0.0.1:8080

## Configuration

### Environment Variables

Create a `.env` file in the project root:

```env
FLASK_SECRET_KEY=your-super-secret-key-change-this-in-production
FLASK_ENV=development
FLASK_DEBUG=True
DATABASE_URL=sqlite:///instance/users.db
PORT=8080
```

### Security Notes

- **Always change the default secret key in production**
- Use a strong, randomly generated secret key
- Consider using environment-specific configuration files

## Project Structure

```
property_calculator/
├── main.py              # Main Flask application
├── map.py              # Map generation script
├── run.py              # Startup script
├── requirements.txt    # Python dependencies
├── .env               # Environment configuration
├── .gitignore         # Git ignore rules
├── instance/          # Database storage
├── static/            # CSS, JS, images
├── templates/         # HTML templates
└── *.csv             # Property data files
```

## Development

### Running in Development Mode

```bash
# Activate virtual environment
source venv/bin/activate

# Set development environment
export FLASK_DEBUG=True

# Run the application
python run.py
```

### Generating Maps

The application includes property mapping functionality. To regenerate maps:

```bash
python map.py
```

This will process the CSV data files and generate an interactive map saved to `templates/map.html`.

## Troubleshooting

### Common Issues

1. **Import errors**: Make sure virtual environment is activated and dependencies are installed
2. **Database errors**: Ensure the `instance/` directory exists and has write permissions
3. **Port conflicts**: Change the PORT in `.env` if 8080 is already in use

### Dependency Issues

If you encounter import errors:

```bash
# Reinstall dependencies
pip install --upgrade -r requirements.txt

# Or install specific packages
pip install flask flask-sqlalchemy python-dotenv pandas folium matplotlib
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is for educational purposes.