from flask import Flask,render_template
from models import db,User,Doctor,Patient,Appointment
from flask_cors import CORS
from dotenv import load_dotenv
from extensions import cache, mail, jwt, celery_app
from celery.schedules import crontab
import os
load_dotenv()


app = Flask(__name__,
    static_folder='../frontend/dist/',
    template_folder='templates')

app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER', 'localhost')
app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 1025))
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME',None)
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD',None)
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER', 'admin@medsyncpro.com')


app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("SQLALCHEMY_DATABASE_URI", "sqlite:///hospital.sqlite3")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')

cache_config = {
    "DEBUG": True,
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
origins_list = allowed_origins.split(',') if allowed_origins else ['http://localhost:8080']
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
    admin_username = os.getenv('user_name') or "admin"
    if not User.query.filter_by(username=admin_username).first():
        admin = User()
        admin.username = admin_username
        admin.set_pass(os.getenv('password') or 'admin123') 
        admin.role = "admin"

        db.session.add(admin)
        db.session.commit()



@app.route("/")
def home():
    return render_template("index.html")

if __name__ == '__main__':

    app.run(debug=True)
