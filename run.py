#!/usr/bin/env python3
"""
Startup script for the Property Calculator Flask application.
This script handles initialization and provides better error handling.
"""

import os
import sys
from pathlib import Path

def check_environment():
    """Check if virtual environment and dependencies are set up correctly."""
    try:
        import flask
        import flask_sqlalchemy
        import pandas
        import folium
        print("✅ All dependencies are installed")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("Please run: pip install -r requirements.txt")
        return False

def ensure_directories():
    """Ensure required directories exist."""
    instance_dir = Path("instance")
    instance_dir.mkdir(exist_ok=True)
    print("✅ Instance directory ready")

def main():
    """Main startup function."""
    print("🚀 Starting Property Calculator...")
    
    # Check environment
    if not check_environment():
        sys.exit(1)
    
    # Ensure directories exist
    ensure_directories()
    
    # Check for .env file
    if not Path(".env").exists():
        print("⚠️  .env file not found. Using default configuration.")
    
    # Import and run the Flask app
    try:
        from main import app, db
        
        # Create database tables
        with app.app_context():
            db.create_all()
            print("✅ Database initialized")
        
        print("🌐 Starting Flask server...")
        print("📍 Access the app at: http://127.0.0.1:8080")
        
        # Get configuration from environment
        debug_mode = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
        port = int(os.getenv('PORT', 8080))
        
        app.run(debug=debug_mode, port=port, host='127.0.0.1')
        
    except Exception as e:
        print(f"❌ Failed to start application: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()