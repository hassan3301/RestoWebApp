from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from apscheduler.schedulers.background import BackgroundScheduler
from dotenv import load_dotenv
import os

load_dotenv()

db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')

    from app.models import Inventory, Sales, SalesItem, Waste
    db.init_app(app)
    migrate.init_app(app, db)

    from app.routes.main import bp as main_bp
    app.register_blueprint(main_bp)


    if not os.getenv("FLASK_SKIP_JOBS"):
        from app.services import sync
        

        def job_wrapper():
            with app.app_context():
                print("Running Square sync job...")
                sync.sync_sales_from_square()

        scheduler = BackgroundScheduler()
        scheduler.add_job(func=job_wrapper, trigger="interval", minutes=2)
        scheduler.start()


    return app