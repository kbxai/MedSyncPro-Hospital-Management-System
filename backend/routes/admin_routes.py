from flask import Blueprint, request, jsonify
from models import db,User,Doctor,Patient,Appointment,Department,Treatment
from routes.auth import authorization 
from extensions import cache
from tasks import send_welcome_email



admin_bp = Blueprint('admin_routes',__name__)

@admin_bp.route("/add-department",methods=['POST'])
@authorization("admin")
def add_dept():
    data = request.get_json()
    name = data.get('name')

    if not name:
        return jsonify(msg="Department name is required"),400

    if Department.query.filter_by(dept_name=name).first():
        return jsonify(msg="Department already exists"),409

    description = data.get('description')
    new_dept = Department(dept_name=name, description=description)

    db.session.add(new_dept)
    db.session.commit()
    cache.clear()

    return jsonify({"msg":"department added successfully"}),201

@admin_bp.route("/get-departments")
@authorization(["admin", "doctor","patient"])
@cache.cached(timeout=60)
def get_depts():
    depts = Department.query.all()

    output = [{"id":dept.id,"name":dept.dept_name} for dept in depts]

    return jsonify(output),200



@admin_bp.route("/add-doctor",methods=['POST'])
@authorization("admin")
def add_doct():
    data = request.get_json()
    username = data.get('username')

    user = User.query.filter_by(username=username).first()
    if user:
        return jsonify({"msg":"Username already Exists"}),400
    
    else:
        password = data.get('password')
        name = data.get('name')
        availability = data.get('availability')
        dept_id = data.get('dept_id')

        dept = Department.query.filter_by(id=dept_id).first()

        if not dept:
            return jsonify({"msg":"department not found"}),400

        new_user = User(username=username, role="doctor")

        try:
            new_user.validate_password(password)
        except ValueError as e:
            return jsonify(msg=str(e)), 400
        
        new_user.set_pass(password=password)
        db.session.add(new_user)
        db.session.flush()

        new_doct = Doctor(name=name,availability=availability,dept_id=dept_id,user_id=new_user.id)
        db.session.add(new_doct)


        db.session.commit()
        cache.clear()

        send_welcome_email.delay(email=data.get('username'),name=data.get('name'),password=data.get('password'))

        return jsonify({"msg":"Doctor registered successfully and credentials emailed"}),201
    
@admin_bp.route("/get-doctor/<int:id>")
@authorization("admin")
def get_doctor(id):
    doctor = Doctor.query.get(id)

    if not doctor:
        return jsonify(msg="Doctor Not found"),404

    user = User.query.get(doctor.user_id)
    if not user or user.is_blocked:
        return jsonify(msg="Doctor Not found"),404

    output = {
        "id":doctor.id,
        "name":doctor.name,
        "username":user.username,
        "availability":doctor.availability,
        "dept_id":doctor.dept_id,
        "department":doctor.department.dept_name
    }

    return jsonify(output),200
    

@admin_bp.route("/get_all_doctors")
@authorization("admin")
@cache.cached(timeout=60)
def get_all_doc():
    doctors = Doctor.query.join(User).filter(User.is_blocked == False).all()
    output = []

    for d in doctors:
            output.append({
                "id":d.id,
                "name":d.name,
                "availability":d.availability,
                "department" : d.department.dept_name

            })
    return jsonify(output),200

@admin_bp.route("/update-doctor/<int:id>",methods=['PUT'])
@authorization("admin")
def update_doctor(id):
    data = request.get_json()
    doctor = Doctor.query.get(id)

    if not doctor:
        return jsonify(msg="Doctor Not found"),404
    
    user = User.query.get(doctor.user_id)
    
    if not user or user.is_blocked:
        return jsonify(msg="Doctor Not found"),404

    
    name = data.get('name')
    dept_id = data.get('dept_id')
    availability = data.get('availability')

    if name or dept_id or availability:
        if name:
            doctor.name = name

        if dept_id:
            dept = Department.query.get(dept_id)
            if not dept:
                return jsonify(msg="department Not found"),404
            doctor.dept_id = dept_id
        
        if availability:
            doctor.availability = availability
        db.session.commit()
        cache.clear()
        return jsonify(msg="Details updated successfully"),200
    else:
        return jsonify(msg="provide details to update"),400


@admin_bp.route("/delete-doctor/<int:id>",methods=['DELETE'])
@authorization("admin")
def delete_doctor(id):
    doctor = Doctor.query.get(id)

    if not doctor:
        return jsonify(msg="Doctor Not found"),404

    user = User.query.get(doctor.user_id)
    if not user or user.is_blocked:
        return jsonify(msg="Doctor Not found"),404

    user.is_blocked = True
    user.username += f"_blocked_{user.id}"

    for appt in doctor.appointments:
        if appt.status == 'pending':
            appt.status = 'cancelled'
    
    db.session.commit()
    cache.clear()
    return jsonify(msg="Doctor blocked and appointments cancelled successfully"),200


@admin_bp.route("/search-doctors", methods=['POST'])
@authorization("admin")
def search_doctors():
    data = request.get_json() or {}
    query_str = data.get('query', '').strip()
    
    if not query_str:
        return jsonify(msg="Search query required"), 400
    
    doctors = Doctor.query.join(User).join(Department).filter(
        User.is_blocked == False,
        db.or_(
            Doctor.name.ilike(f'%{query_str}%'),
            Department.dept_name.ilike(f'%{query_str}%')
        )
    ).all()
    
    output = [{
        "id": d.id,
        "name": d.name,
        "department": d.department.dept_name if d.department else None,
        "availability": d.availability
    } for d in doctors]
    
    return jsonify(output), 200


@admin_bp.route("/search-patients", methods=['POST'])
@authorization("admin")
def search_patients():
    data = request.get_json() or {}
    query_str = data.get('query', '').strip()
    
    if not query_str:
        return jsonify(msg="Search query required"), 400
    
    patients = Patient.query.join(User).filter(
        User.is_blocked == False,
        db.or_(
            Patient.name.ilike(f'%{query_str}%'),
            User.username.ilike(f'%{query_str}%')
        )
    ).all()
    
    output = [{
        "id": p.id,
        "name": p.name,
        "age": p.age,
        "gender": p.gender,
        "username": p.user.username
    } for p in patients]
    
    return jsonify(output), 200


@admin_bp.route("/get-all-patients")
@authorization("admin")
def get_all_patients():
    patients = Patient.query.join(User).filter(User.is_blocked == False).all()
    output = [{
        "id": p.id,
        "name": p.name,
        "age": p.age,
        "gender": p.gender,
        "username": p.user.username
    } for p in patients]
    return jsonify(output), 200


@admin_bp.route("/get-all-appointments")
@authorization("admin")
def get_all_appointments():
    appts = Appointment.query.order_by(Appointment.appointment_date.desc()).all()
    output = [{
        "id": a.id,
        "patient_name": a.patient.name if a.patient else "N/A",
        "doctor_name": a.doctor.name if a.doctor else "N/A",
        "date": str(a.appointment_date),
        "time": str(a.appointment_time),
        "status": a.status
    } for a in appts]
    return jsonify(output), 200


@admin_bp.route("/get-dashboard-stats")
@authorization("admin")
def get_dashboard_stats():
    total_doctors = Doctor.query.join(User).filter(User.is_blocked == False).count()
    total_patients = Patient.query.join(User).filter(User.is_blocked == False).count()
    total_appointments = Appointment.query.count()
    pending_appointments = Appointment.query.filter_by(status='pending').count()
    
    return jsonify({
        "total_doctors": total_doctors,
        "total_patients": total_patients,
        "total_appointments": total_appointments,
        "pending_appointments": pending_appointments
    }), 200


@admin_bp.route("/delete-patient/<int:id>", methods=['DELETE'])
@authorization("admin")
def delete_patient(id):
    patient = Patient.query.get(id)
    if not patient:
        return jsonify(msg="Patient not found"), 404
        
    user = User.query.get(patient.user_id)
    if user:
        user.is_blocked = True
        user.username += f"_blocked_{user.id}" 
        
    pending_appts = Appointment.query.filter_by(patient_id=patient.id, status='pending').all()
    for appt in pending_appts:
        appt.status = 'cancelled'
        
    db.session.commit()
    cache.clear()
    return jsonify(msg="Patient blocked and pending appointments cancelled"), 200


@admin_bp.route("/patient-treatments/<int:pat_id>")
@authorization("admin")
def admin_patient_treatments(pat_id):
    treatments = Treatment.query.join(Appointment).filter(
        Appointment.patient_id == pat_id
    ).all()

    data = []
    for t in treatments:
        data.append({
            "treatment_id": t.id,
            "appointment_id": t.appointment_id,
            "diagnosis": t.diagnosis,
            "prescription": t.prescription,
            "notes": t.notes,
            "date": t.appointment.appointment_date.strftime("%Y-%m-%d") if t.appointment else None,
            "doctor_name": t.appointment.doctor.name if t.appointment and t.appointment.doctor else "N/A"
        })

    return jsonify(data), 200