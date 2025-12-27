#!/usr/bin/env python
"""
Bass Practice Application - Entry Point

Run this file to start the application:
    python run.py

Then open your browser to http://localhost:5000
"""
from app import create_app

app = create_app()

if __name__ == '__main__':
    print("\n" + "="*50)
    print("   Bass Practice Application")
    print("="*50)
    print("\n   Open your browser to: http://localhost:5000")
    print("\n   Press Ctrl+C to stop the server")
    print("="*50 + "\n")
    
    app.run(debug=True, host='localhost', port=5000)
