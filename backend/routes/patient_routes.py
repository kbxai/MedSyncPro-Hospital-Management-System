from flask import Blueprint, request, jsonify
from models import db, User, Doctor, Patient, Appointment, Department,Treatment
from sqlalchemy.exc import IntegrityError
from flask_jwt_extended import get_jwt_identity
from routes.auth import authorization
from datetime import datetime,timedelta
from extensions import cache
from tasks import export_treatment_csv
patient_bp = Blueprint("patient_routes",__name__)


@patient_bp.route("/update-patient/<int:id>",methods=['GET','PUT'])
@authorization('patient')
def update_patient(id):
    identity = get_jwt_identity()
    current_user = User.query.filter_by(username=identity, is_blocked=False).first()
    
    if not current_user or not current_user.patient:
        return jsonify(msg="Unauthorized"), 403
    

    if current_user.patient.id != id:
        return jsonify(msg="Unauthorized - can only access your own profile"), 403
    
    patient = Patient.query.get(id)
    
    if not patient:
        return jsonify(msg="Patient Not found"),404 
    
    user = User.query.get(patient.user_id)
    
    if not user or user.is_blocked:
        return jsonify(msg="Patient Not found"),404
    

    if request.method == 'GET':
        return jsonify({
            "id": patient.id,
            "name": patient.name,
            "age": patient.age,
            "gender": patient.gender,
            "username": user.username
        }), 200
    
    data = request.get_json()

    
    name = data.get('name')
    age = data.get('age')
    gender = data.get('gender')


    if name or age or gender:
        if name:
            patient.name = name

        if age:
            patient.age = age
        
        if gender:
            patient.gender = gender

        db.session.commit()
        return jsonify(msg="Details updated successfully"),200
    else:
        return jsonify(msg="provide details to update"),400

@patient_bp.route("/get-patient-by-token/",methods=['POST'])
@authorization('patient')
def get_patient_by_token():
    identity = get_jwt_identity()
    user = User.query.filter_by(username=identity,is_blocked=False).first()

    if not user or not user.patient:
        return jsonify(msg="Patient not found"),404
    
    patient = user.patient

    json = {
        "id":patient.id} 
    
    return jsonify(json),200



@patient_bp.route("/search-doctors/",methods=['POST'])
@authorization('patient')
def search_doctors():
    user = User.query.filter_by(username=get_jwt_identity(),is_blocked=False).first()
    if not user or not user.patient:
        return jsonify(msg="Unauthorized"),403
    data = request.get_json(silent=True) or {}
    dept_id = data.get("dept_id")

    if not dept_id:
        docts = Doctor.query.join(User).filter(User.is_blocked == False).all()
        json = []

        for doct in docts:
            json.append({
                "id":doct.id,
                "name":doct.name,
                "department": doct.department.dept_name,
                "availability":doct.availability
            })
        return jsonify(json)
    
    dept = Department.query.get(dept_id)
    if not dept:
        return jsonify(msg="Department not found"),404
    
    docts = Doctor.query.join(User).filter(User.is_blocked == False,Doctor.dept_id==dept_id).all()
    json = []

    for doct in docts:
        json.append({
            "id":doct.id,
            "name":doct.name,
            "department": dept.dept_name,
            "availability":doct.availability
        })
    return jsonify(json)
    


@patient_bp.route('/get-available-slots', methods=['POST'])
@authorization('patient')

def get_available_slots():
    user = User.query.filter_by(username=get_jwt_identity(),is_blocked=False).first()
    if not user or not user.patient:
        return jsonify(msg="Unauthorized"),403
    data = request.get_json(silent=True) or {}
    doct_id = data.get('doct_id')
    date_str = data.get('date')
    

    if not doct_id or not date_str:
        return jsonify(msg="doct_id and date are required"), 400

    try:
        appt_date = datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        return jsonify(msg="Invalid date format. Use YYYY-MM-DD"), 400

    today = datetime.now().date()
    max_date = today + timedelta(days=7)

    if not (today <= appt_date <= max_date):
        return jsonify(msg="Bookings are strictly limited to the next 7 days"), 400

    doctor = Doctor.query.join(User).filter(
        Doctor.id == doct_id,
        User.is_blocked == False
    ).first()
    if not doctor or not doctor.availability:
        return jsonify(msg="Doctor not found"), 404

    try:
        days_part, hrs_part = doctor.availability.split('|', 1)
        allowed_days = [d.strip().upper() for d in days_part.split(',') if d.strip()]
        if not allowed_days:
            return jsonify(msg="Doctor availability days are missing"), 400

        start_str, end_str = [p.strip() for p in hrs_part.split('-', 1)]
        start_t = datetime.strptime(start_str, '%H:%M').time()
        end_t   = datetime.strptime(end_str, '%H:%M').time()

        if start_t >= end_t:
            return jsonify(msg="Doctor availability time range is invalid (end must be after start, same day)"), 400
    except Exception:
        return jsonify(msg="Invalid availability format. Use MON,TUE|09:00-17:00"), 400

    appt_day = appt_date.strftime('%a')[:3].upper()
    if appt_day not in allowed_days:
        return jsonify([]), 200

    start_dt = datetime.combine(appt_date, start_t)
    end_dt   = datetime.combine(appt_date, end_t)

    slots = []
    cur = start_dt
    while cur < end_dt:
        slots.append(cur.strftime('%H:%M'))
        cur += timedelta(minutes=30)

    booked = Appointment.query.filter(
        Appointment.doctor_id==doctor.id,
        Appointment.appointment_date==appt_date,
        Appointment.status != 'cancelled'
    ).all()
    booked_times = {a.appointment_time.strftime('%H:%M') for a in booked}
    available = []
    now = datetime.now()
    is_today = appt_date == now.date()

    for s in slots:
        if s in booked_times:
            continue
        
        slot_time = datetime.strptime(s, '%H:%M').time()
        if is_today and slot_time <= now.time():
            continue
            
        available.append(s)

    return jsonify(available), 200


@patient_bp.route("/book-appointment/",methods=['POST'])
@authorization('patient')
def book_appt():
    user = User.query.filter_by(username=get_jwt_identity(),is_blocked=False).first()
    if not user or not user.patient:
        return jsonify(msg="Unauthorized"),403
    data = request.get_json()

    doct_id = data.get("doct_id")
    date_str = data.get("date")
    time_str = data.get("time")

    if not all([doct_id, date_str, time_str]):
        return jsonify(msg="Doctor ID, date, and time are required"), 400
    
    doct = Doctor.query.join(User).filter(User.is_blocked == False,Doctor.id == doct_id).first()
    if not doct or not doct.availability:
        return jsonify(msg="Doctor not found"),404


    appt_date = datetime.strptime(date_str,"%Y-%m-%d").date()
    appt_time = datetime.strptime(time_str,"%H:%M").time()
    appt_day = appt_date.strftime("%a").upper()[:3]

    today = datetime.now().date()
    max_date = today + timedelta(days=7)

    if not (today <= appt_date <= max_date):
        return jsonify(msg="Bookings are strictly limited to the next 7 days"), 400

    try:
        days,hrs = doct.availability.split("|")
        days_list = [d.strip().upper() for d in days.split(',')]
        start,end = hrs.split("-")

        start_time = datetime.strptime(start.strip(),"%H:%M").time()
        end_time = datetime.strptime(end.strip(),"%H:%M").time()

    except Exception:
        return jsonify(msg="Doctor availability format is wrong"),500
    
    if appt_day not in days_list:
        return jsonify(msg=f"Doctor not available on {appt_day}"),400
    
    if not (start_time <= appt_time < end_time):
        return jsonify(msg="Selected time is outside doctor's working hours"),400
    
    if Appointment.query.filter_by(doctor_id=doct_id,appointment_date=appt_date,appointment_time=appt_time,status="pending").first():
        return jsonify(msg="Appointment already booked or in pending at this date and time"),400

    cancelled = Appointment.query.filter_by(
        doctor_id=doct_id, appointment_date=appt_date,
        appointment_time=appt_time, status='cancelled'
    ).first()
    if cancelled:
        db.session.delete(cancelled)

    new_appt = Appointment(
        patient_id=user.patient.id,
        doctor_id=doct.id,
        appointment_date=appt_date,
        appointment_time=appt_time,
        status="pending"
    )

    try:
        db.session.add(new_appt)
        db.session.commit()
        return jsonify(msg="Appointment Booked successfully"),201
    except IntegrityError:
        db.session.rollback()
        return jsonify(msg="This slot was just booked by someone else!"), 409

@patient_bp.route("/appointments", methods=['GET'])
@authorization('patient')
def my_appts():
    identity = get_jwt_identity()
    user = User.query.filter_by(username=identity, is_blocked=False).first()
    
    if not user or not user.patient:
        return jsonify(msg="Patient not found"), 404
    
    appts = Appointment.query.filter_by(patient_id=user.patient.id).all()
    
    output = []
    for a in appts:
        treatment = Treatment.query.filter_by(appointment_id=a.id).first()
        
        output.append({
            "id": a.id,
            "doctor_id": a.doctor_id,
            "doctor_name": a.doctor.name,
            "date": str(a.appointment_date),
            "time": str(a.appointment_time),
            "status": a.status,
            "diagnosis": treatment.diagnosis if treatment else "N/A",
            "prescription": treatment.prescription if treatment else "Awaiting Checkup"
        })
    return jsonify(output), 200

    



@patient_bp.route('/cancel-appointment/<int:appt_id>', methods=['PUT'])
@authorization('patient')
def cancel_appointment(appt_id):
    identity = get_jwt_identity()
    user = User.query.filter_by(username=identity, is_blocked=False).first()
    
    if not user:
        return jsonify(msg="User not found"), 401
    
    patient = Patient.query.filter_by(user_id=user.id).first()
    if not patient:
        return jsonify(msg="Patient profile not found"), 404
    
    appt = Appointment.query.filter_by(
        id=appt_id,
        patient_id=patient.id,
        status='pending'
    ).first()
    
    if not appt:
        return jsonify(msg="Appointment not found or already completed/cancelled"), 404
    
    appt.status = 'cancelled'
    db.session.commit()
    return jsonify(msg="Appointment cancelled successfully"), 200


@patient_bp.route('/reschedule-appointment/<int:appt_id>', methods=['PUT'])
@authorization('patient')
def reschedule_appointment(appt_id):
    identity = get_jwt_identity()
    user = User.query.filter_by(username=identity, is_blocked=False).first()

    if not user or not user.patient:
        return jsonify(msg="Patient not found"), 404

    appt = Appointment.query.filter_by(
        id=appt_id,
        patient_id=user.patient.id,
        status='pending'
    ).first()

    if not appt:
        return jsonify(msg="Appointment not found or cannot be rescheduled"), 404

    data = request.get_json()
    date_str = data.get('date')
    time_str = data.get('time')

    if not date_str or not time_str:
        return jsonify(msg="Date and time are required"), 400

    new_date = datetime.strptime(date_str, '%Y-%m-%d').date()
    new_time = datetime.strptime(time_str, '%H:%M').time()

    today = datetime.now().date()
    max_date = today + timedelta(days=7)

    if not (today <= new_date <= max_date):
        return jsonify(msg="Bookings are limited to the next 7 days"), 400

    doctor = Doctor.query.join(User).filter(
        Doctor.id == appt.doctor_id,
        User.is_blocked == False
    ).first()

    if not doctor or not doctor.availability or doctor.user.is_blocked:
        return jsonify(msg="Doctor is no longer available"), 404

    try:
        days, hrs = doctor.availability.split('|')
        days_list = [d.strip().upper() for d in days.split(',')]
        start, end = hrs.split('-')
        start_time = datetime.strptime(start.strip(), '%H:%M').time()
        end_time = datetime.strptime(end.strip(), '%H:%M').time()
    except Exception:
        return jsonify(msg="Doctor availability format error"), 500

    appt_day = new_date.strftime('%a').upper()[:3]
    if appt_day not in days_list:
        return jsonify(msg=f"Doctor not available on {appt_day}"), 400

    if not (start_time <= new_time < end_time):
        return jsonify(msg="Time is outside doctor's working hours"), 400

    conflict = Appointment.query.filter_by(
        doctor_id=appt.doctor_id,
        appointment_date=new_date,
        appointment_time=new_time,
        status='pending'
    ).first()

    if conflict and conflict.id != appt.id:
        return jsonify(msg="This slot is already booked"), 400

    cancelled_at_new = Appointment.query.filter_by(
        doctor_id=appt.doctor_id, appointment_date=new_date,
        appointment_time=new_time, status='cancelled'
    ).first()
    if cancelled_at_new:
        db.session.delete(cancelled_at_new)

    appt.appointment_date = new_date
    appt.appointment_time = new_time

    try:
        db.session.commit()
        return jsonify(msg="Appointment rescheduled successfully"), 200
    except IntegrityError:
        db.session.rollback()
        return jsonify(msg="Slot was just taken"), 409


@patient_bp.route('/export-treatments', methods=['POST'])
@authorization('patient')
def export_treatments_csv():
    try:
        identity = get_jwt_identity()

        user = User.query.filter_by(username=identity, is_blocked=False).first()
        
        if not user or not user.patient:

            return jsonify(msg="Patient not found"), 404
        
        patient = user.patient


        export_treatment_csv.delay(patient.id, user.username)
        return jsonify(msg=f"Treatment records sent to {user.username}"), 200
    except Exception as e:
        return jsonify(msg="Service temporarily unavailable. Please try again later."), 503