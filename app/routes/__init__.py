from flask import Flask

def register_blueprints(app: Flask):
    """Register all blueprints for the application."""
    from .dashboard import bp as dashboard_bp
    from .practice import bp as practice_bp
    from .exercises import bp as exercises_bp
    from .songs import bp as songs_bp
    from .timing import bp as timing_bp
    from .ear_training import bp as ear_training_bp
    from .quiz import bp as quiz_bp
    from .progressions import bp as progressions_bp
    from .admin import bp as admin_bp

    app.register_blueprint(dashboard_bp)
    app.register_blueprint(practice_bp)
    app.register_blueprint(exercises_bp)
    app.register_blueprint(songs_bp)
    app.register_blueprint(timing_bp)
    app.register_blueprint(ear_training_bp)
    app.register_blueprint(quiz_bp)
    app.register_blueprint(progressions_bp)
    app.register_blueprint(admin_bp)
