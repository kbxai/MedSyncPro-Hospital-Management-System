from extensions import celery_app
from app import app
from tasks import send_daily_reminder, send_welcome_email, doc_monthly_reports, export_treatment_csv


celery_app.conf.update(
    task_track_started=True,
    worker_pool='solo',  
)