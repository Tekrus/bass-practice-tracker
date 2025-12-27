"""
Bass Practice Application - Flask App Initialization
"""
import os
from flask import Flask
from .models import db


def create_app():
    """Create and configure the Flask application."""
    app = Flask(__name__)
    
    # Configuration
    basedir = os.path.abspath(os.path.dirname(__file__))
    data_dir = os.path.join(os.path.dirname(basedir), 'data')
    
    # Ensure data directory exists
    os.makedirs(data_dir, exist_ok=True)
    
    app.config['SECRET_KEY'] = 'bass-practice-local-app-secret-key'
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(data_dir, "bass_practice.db")}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Initialize extensions
    db.init_app(app)
    
    # Register blueprints
    from .routes import main_bp
    app.register_blueprint(main_bp)
    
    # Create database tables
    with app.app_context():
        db.create_all()
        
        # Initialize default data if needed
        from .seed_data import seed_database
        seed_database()
    
    return app
