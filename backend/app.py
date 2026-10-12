from flask import Flask, jsonify, send_from_directory
from models import db,User,Doctor,Patient,Appointment
from flask_cors import CORS
from dotenv import load_dotenv
from extensions import cache, mail, jwt, celery_app
from celery.schedules import crontab
import os
from pathlib import Path
from sqlalchemy import inspect, text
from sqlalchemy.engine import URL
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
FRONTEND_DIST = BASE_DIR.parent / "frontend" / "dist"
IS_PRODUCTION = os.getenv("APP_ENV", "development").lower() == "production"

def _required_secret(name):
    value = os.getenv(name)
    if IS_PRODUCTION and (not value or len(value) < 32):
        raise RuntimeError(f"{name} must be set to a random value of at least 32 characters in production")
    return value or "development-only-secret-change-me"

app = Flask(__name__, static_folder=str(FRONTEND_DIST), template_folder="templates")

app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER', 'localhost')
app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 1025))
app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS', 'false').lower() == 'true'
app.config['MAIL_USE_SSL'] = os.getenv('MAIL_USE_SSL', 'false').lower() == 'true'
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME',None)
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD',None)
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER', 'admin@medsyncpro.com')


database_uri = os.getenv("SQLALCHEMY_DATABASE_URI")
if not database_uri and os.getenv("DATABASE_HOST"):
    database_uri = URL.create(
        "postgresql+psycopg",
        username=os.getenv("DATABASE_USER", "medsync"),
        password=os.getenv("DATABASE_PASSWORD"),
        host=os.getenv("DATABASE_HOST"),
        port=int(os.getenv("DATABASE_PORT", "5432")),
        database=os.getenv("DATABASE_NAME", "medsync"),
    )
app.config['SQLALCHEMY_DATABASE_URI'] = database_uri or f"sqlite:///{BASE_DIR / 'instance' / 'hospital.sqlite3'}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = _required_secret('JWT_SECRET_KEY')

cache_config = {
    "DEBUG": not IS_PRODUCTION,
    "CACHE_TYPE": "RedisCache",
    "CACHE_REDIS_URL": os.getenv('REDIS_URL', 'redis://127.0.0.1:6379/0'),
    "CACHE_DEFAULT_TIMEOUT": 300
}


mail.init_app(app)
cache.init_app(app, config=cache_config)
jwt.init_app(app)
db.init_app(app)

celery_app.conf.update(
    broker_url=os.getenv('REDIS_URL', 'redis://127.0.0.1:6379/0'),
    result_backend=os.getenv('REDIS_URL', 'redis://127.0.0.1:6379/0'),
    task_ignore_result=False,
    beat_schedule={
        'send-daily-reminder': {
            'task': 'tasks.send_daily_reminder',
            'schedule': crontab(hour='8', minute='0')
        },
        'monthly-reports':{
            'task':'tasks.doc_monthly_reports',
            'schedule': crontab(hour=2, minute=0, day_of_month=1)
            # 'schedule': crontab(hour='*', minute='*/1')
        },
    },
    timezone='Asia/Kolkata',
    result_expires=3600,
)


class ContextTask(celery_app.Task):
    def __call__(self, *args, **kwargs):
        with app.app_context():
            return self.run(*args, **kwargs)

celery_app.Task = ContextTask

allowed_origins = os.getenv('CORS_ALLOWED_ORIGINS')
origins_list = [origin.strip() for origin in (allowed_origins or 'http://localhost:8080').split(',') if origin.strip()]
CORS(app, origins=origins_list)



from routes.auth import auth_bp
from routes.admin_routes import admin_bp
from routes.doctor_routes import doctor_bp
from routes.patient_routes import patient_bp

app.register_blueprint(auth_bp,url_prefix='/auth')
app.register_blueprint(patient_bp,url_prefix='/patient')
app.register_blueprint(admin_bp,url_prefix='/admin')
app.register_blueprint(doctor_bp,url_prefix='/doctor')


with app.app_context():
    db.create_all()
    user_columns = {column["name"] for column in inspect(db.engine).get_columns("user")}
    if "password_setup_token_hash" not in user_columns:
        if db.engine.dialect.name == "sqlite":
            db.session.execute(text("ALTER TABLE user ADD COLUMN password_setup_token_hash VARCHAR(128)"))
            db.session.execute(text("ALTER TABLE user ADD COLUMN password_setup_expires_at DATETIME"))
        elif db.engine.dialect.name == "postgresql":
            db.session.execute(text('ALTER TABLE "user" ADD COLUMN IF NOT EXISTS password_setup_token_hash VARCHAR(128)'))
            db.session.execute(text('ALTER TABLE "user" ADD COLUMN IF NOT EXISTS password_setup_expires_at TIMESTAMP'))
        db.session.commit()
    admin_username = os.getenv('ADMIN_USERNAME') or os.getenv('user_name')
    admin_password = os.getenv('ADMIN_BOOTSTRAP_PASSWORD') or os.getenv('password')
    bootstrap_admin = os.getenv("BOOTSTRAP_ADMIN", "true").lower() == "true"
    if IS_PRODUCTION and bootstrap_admin and (not admin_username or not admin_password):
        raise RuntimeError("ADMIN_USERNAME and ADMIN_BOOTSTRAP_PASSWORD are required for the initial production bootstrap")
    if bootstrap_admin and admin_username and admin_password and not User.query.filter_by(username=admin_username).first():
        admin = User()
        admin.username = admin_username
        admin.set_pass(admin_password)
        admin.role = "admin"

        db.session.add(admin)
        db.session.commit()


@app.route("/")
def home():
    index_path = FRONTEND_DIST / "index.html"
    if index_path.exists():
        return send_from_directory(FRONTEND_DIST, "index.html")
    return jsonify(msg="Frontend build is not available"), 503


@app.route("/healthz")
def healthz():
    return jsonify(status="ok"), 200


@app.route("/readyz")
def readyz():
    try:
        db.session.execute(text("SELECT 1"))
        return jsonify(status="ready"), 200
    except Exception:
        app.logger.exception("Readiness check failed")
        return jsonify(status="not_ready"), 503


@app.errorhandler(500)
def handle_server_error(error):
    app.logger.error("Unhandled application error", exc_info=True)
    return jsonify(msg="Internal server error"), 500

if __name__ == '__main__':

    app.run(debug=True)
