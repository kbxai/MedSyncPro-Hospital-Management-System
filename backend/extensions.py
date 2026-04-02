from flask_caching import Cache
from flask_mail import Mail
from flask_jwt_extended import JWTManager
from celery import Celery

cache = Cache()
mail = Mail()
jwt = JWTManager()
celery_app = Celery('tasks')