from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash,check_password_hash
import re

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    username = db.Column(db.String(80),unique=True,nullable=False)
    password = db.Column(db.String(200),nullable=False)

    def set_pass(self,password):
        self.password = generate_password_hash(password)
    
    def check_pass(self,password):
        return check_password_hash(self.password,password)
    
    def validate_password(self,password):
        if len(password) < 8:
            raise ValueError("Password must be at least 8 characters")
        if not re.search(r'[A-Z]', password):
            raise ValueError("Password must contain uppercase letter")
        if not re.search(r'[0-9]', password):
            raise ValueError("Password must contain number")
        if not re.search(r'[!@#$%^&*]', password):
            raise ValueError("Password must contain special character")
        return True

    role = db.Column(db.String(10),nullable=False)

    is_blocked = db.Column(db.Boolean,default=False)

    doctor = db.relationship('Doctor',backref='user',uselist=False)
    patient = db.relationship('Patient',backref='user',uselist=False)


class Doctor(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(20),nullable=False)
    availability = db.Column(db.String(100),nullable=False)

    dept_id = db.Column(db.Integer,db.ForeignKey("department.id"),nullable=False)
    user_id = db.Column(db.Integer,db.ForeignKey("user.id"),nullable=False)

    appointments = db.relationship("Appointment",backref='doctor',lazy=True)



class Patient(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(20),nullable=False)
    age = db.Column(db.Integer,nullable=False)
    gender = db.Column(db.String(20),nullable=False)

    user_id = db.Column(db.Integer,db.ForeignKey("user.id"),nullable=False)

    appointments = db.relationship("Appointment",backref='patient',lazy=True)


class Appointment(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    
    patient_id = db.Column(db.Integer,db.ForeignKey("patient.id"),nullable=False)
    doctor_id = db.Column(db.Integer,db.ForeignKey("doctor.id"),nullable=False)
    __table_args__ = (
        db.UniqueConstraint('doctor_id', 'appointment_date', 'appointment_time', name='unique_doctor_slot'),
    )

    appointment_date = db.Column(db.Date())
    appointment_time = db.Column(db.Time())
    status = db.Column(db.String(10))

class Department(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    dept_name = db.Column(db.String(200))
    description = db.Column(db.String(30))

    doctors = db.relationship('Doctor',backref='department')


class Treatment(db.Model):
    id = db.Column(db.Integer,primary_key=True)

    appointment_id = db.Column(db.Integer,db.ForeignKey('appointment.id'),nullable=False)
    diagnosis = db.Column(db.String(100))
    prescription = db.Column(db.String(100))
    notes = db.Column(db.String(100))

    appointment = db.relationship('Appointment',backref='treatment',uselist=False)

