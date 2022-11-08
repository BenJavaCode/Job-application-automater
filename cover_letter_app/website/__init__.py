from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect

from configurations.config import GEOGRAPHIES, DevelopmentConfig


# GLOBAL SESSION FACTORY
db = SQLAlchemy()
csrf = CSRFProtect()
    

def refresh_database(app):
    db.drop_all(app=app)
    db.create_all(app=app)
    print('DB refreshed')
    
def create_database(app):
    db.create_all(app=app)
    print('DB created')
    
# Populate geography on app creation
def create_geographies(app, db, Geography):
    with app.app_context():
        for i, geo_name in enumerate(GEOGRAPHIES):
            geo = Geography(id=i+1, name=geo_name)
            if not Geography.query.filter_by(name=geo_name).first():
                db.session.add(geo)
            db.session.commit() 
    

# CREATE APP
def create_app():
    app = Flask(__name__)
    app.config.from_object(DevelopmentConfig())
    

    db.init_app(app)
    csrf.init_app(app)

    from .routing.home import home
    from .routing.auth import auth
    from .routing.scrapingquery import scrapingquery
    from .routing.scraping import scraper

    app.register_blueprint(auth, url_prefix='/')
    app.register_blueprint(home, url_prefix='/')
    app.register_blueprint(scraper, url_prefix='/')
    app.register_blueprint(scrapingquery, url_prefix='/')
    
    from .persistence.models import User
    from website.persistence.models import Geography

    create_database(app)
    #refresh_database(app)
    create_geographies(app, db, Geography=Geography)
    
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login_'
    login_manager.init_app(app)

    # Get user from session
    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    return app