import os
from flask import Flask, render_template
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from datetime import timedelta

from backend.routes.auth import auth_bp
from backend.routes.profile import profile_bp
from backend.routes.health import health_bp
from backend.routes.medication import medication_bp
from backend.routes.insights import insights_bp
from backend.routes.alerts import alerts_bp


def create_app():
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))

    app = Flask(
        __name__,
        template_folder=os.path.join(BASE_DIR, 'frontend', 'templates'),
        static_folder=os.path.join(BASE_DIR, 'frontend', 'static')
    )

    # Configuration
    app.config['JWT_SECRET_KEY'] = 'super-secret-key-change-this'
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)

    CORS(app)
    JWTManager(app)

    # Register Blueprints
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(profile_bp, url_prefix='/api/profile')
    app.register_blueprint(health_bp, url_prefix='/api/health')
    app.register_blueprint(medication_bp, url_prefix='/api/medication')
    app.register_blueprint(insights_bp, url_prefix='/api/insights')
    app.register_blueprint(alerts_bp, url_prefix='/api/alerts')

    # Frontend routes
    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/login')
    def login_page():
        return render_template('login.html')

    @app.route('/register')
    def register_page():
        return render_template('register.html')
    
    @app.route('/vitals')
    def vitals_page():
        return render_template('vitals.html')
    
    @app.route('/risk')
    def risk_page():
        return render_template('risk.html')
    
    @app.route('/insights')
    def insights_page():
        return render_template('insights.html')
    
    @app.route('/alerts')
    def alerts_page():
        return render_template('alerts.html')
    
    @app.route('/profile')
    def profile_page():
        return render_template('profile.html')
    
    @app.route('/medication')
    def medication_page():
        return render_template('medication.html')
    
    @app.route('/health_trends')
    def health_trends_page():
        return render_template('health_trends.html')
    
    @app.route('/settings')
    def settings_page():
        return render_template('settings.html')

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=5000)
