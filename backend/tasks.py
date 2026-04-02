from extensions import celery_app, mail
from flask_mail import Message
from models import Appointment, Doctor, Treatment
from datetime import date, datetime, timedelta
from io import StringIO
import csv
from flask import render_template


@celery_app.task
def send_welcome_email(email, name, password):
    msg = Message(
        subject="Welcome to MedSyncPro",
        recipients=[email],
        body=f"""Dear {name},

Username: {email}
Password: {password}

Regards,
MedSyncPro"""
    )
    mail.send(msg)
    return "Welcome email sent"


@celery_app.task
def send_daily_reminder():
    today = date.today()

    appts = Appointment.query.filter_by(
        appointment_date=today,
        status='pending'
    ).all()

    count = 0

    for appt in appts:
        msg = Message(
            subject="Appointment Reminder",
            recipients=[appt.patient.user.username],
            body=f"""Dear {appt.patient.name},

Your appointment is today at {appt.appointment_time}
with Dr. {appt.doctor.name}.

Regards,
MedSyncPro"""
        )
        mail.send(msg)
        count += 1

    return f"{count} reminders sent"


@celery_app.task
def doc_monthly_reports():
    today = date.today()

    first_day_current_month = today.replace(day=1)
    last_day_prev_month = first_day_current_month - timedelta(days=1)
    first_day_prev_month = last_day_prev_month.replace(day=1)

    month_name = last_day_prev_month.strftime("%B %Y")

    doctors = Doctor.query.all()
    count = 0

    for doc in doctors:

        appts = Appointment.query.filter(
            Appointment.doctor_id == doc.id,
            Appointment.status == 'completed',
            Appointment.appointment_date >= first_day_prev_month,
            Appointment.appointment_date <= last_day_prev_month
        ).all()

        report_data = []

        for a in appts:
            if a.treatment:
                report_data.append({
                "date": a.appointment_date.strftime("%d-%m-%Y"),
                "patient_name": a.patient.name,
                "diagnosis": a.treatment[0].diagnosis,
                "prescription": a.treatment[0].prescription
    })

        html = render_template(
            "report.html",
            doctor_name=doc.name,
            month_name=month_name,
            appointments=report_data
        )

        msg = Message(
            subject=f"Monthly Report - {month_name}",
            recipients=[doc.user.username],
            html=html
        )

        mail.send(msg)
        count += 1

    return f"{count} reports sent"


@celery_app.task
def export_treatment_csv(patient_id, username):

    records = Treatment.query.join(Appointment).filter(
        Appointment.patient_id == patient_id
    ).all()

    output = StringIO()
    writer = csv.writer(output)

    writer.writerow([
        "Treatment ID",
        "Appointment ID",
        "Doctor Name",
        "Diagnosis",
        "Prescription",
        "Date"
    ])

    for record in records:
        writer.writerow([
            record.id,
            record.appointment_id,
            record.appointment.doctor.name,
            record.diagnosis,
            record.prescription,
            record.appointment.appointment_date.strftime('%Y-%m-%d')
        ])

    msg = Message(
        subject="Your Treatment Records",
        recipients=[username],
        body="Please find attached your treatment records."
    )

    msg.attach("treatment_records.csv", "text/csv", output.getvalue())
    mail.send(msg)

    return "CSV sent"