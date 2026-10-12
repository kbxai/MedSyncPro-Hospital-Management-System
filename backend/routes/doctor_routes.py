from flask import Blueprint, request, jsonify
from models import db, User, Doctor, Appointment, Treatment
from flask_jwt_extended import get_jwt_identity
from routes.auth import authorization
from extensions import cache

doctor_bp = Blueprint("doctor_routes", __name__)


@doctor_bp.route("/get_my_appointments/",methods=['GET'])
@authorization("doctor")
def get_my_appointments():
    identity = get_jwt_identity()
    user = User.query.filter_by(username=identity,is_blocked=False).first_or_404()

    if not user.doctor:
        return jsonify({"msg": "Doctor profile not found"}), 401

    doc_id = user.doctor.id
    appointments = Appointment.query.filter(
        Appointment.doctor_id == doc_id, Appointment.status != "cancelled").all()

    data = []
    for appt in appointments:
        data.append({
            "id": appt.id,
            "patient_id": appt.patient_id,
            "doctor_id": appt.doctor_id,
            "appointment_date": appt.appointment_date.strftime("%B%d,%Y") if appt.appointment_date else "N/A",
            "appointment_time": appt.appointment_time.strftime("%H:%M") if appt.appointment_time else "N/A",
            "status": appt.status,
            "patient_name": appt.patient.name if appt.patient else None,
        })
    
    return jsonify(data),200

@doctor_bp.route("/add_treatment/<int:appt_id>",methods=["POST"])
@authorization("doctor")
def add_treatment(appt_id):
    data = request.get_json()
    identity = get_jwt_identity()
    user = User.query.filter_by(username=identity,is_blocked=False).first_or_404()

    if not user.doctor:
        return jsonify({"msg": "Doctor profile not found"}), 401
    
    doc_id = user.doctor.id
    appointment = Appointment.query.filter_by(id=appt_id,doctor_id=doc_id,status="pending").first()

    if not appointment:
        return jsonify({"msg": "appointment not found"}), 404
    

    appointment.status = "completed"

    treatment = Treatment(appointment_id=appt_id,diagnosis=data.get("diagnosis"),prescription=data.get("prescription"),notes=data.get("notes"))
    db.session.add(treatment)
    db.session.commit()

    return jsonify(msg="Treatment added successfully"),200



@doctor_bp.route('/cancel-appointment/<int:appt_id>', methods=['PUT'])
@authorization('doctor')
def cancel_appointment(appt_id):
    identity = get_jwt_identity()
    user = User.query.filter_by(username=identity, is_blocked=False).first_or_404()
    doctor = Doctor.query.filter_by(user_id=user.id).first_or_404()
    
    appointment = Appointment.query.filter_by(id=appt_id, doctor_id=doctor.id).first_or_404()
    
    if appointment.status not in ['pending']:
        return {"msg": "Cannot cancel this appointment"}, 400
    
    appointment.status = 'cancelled'
    db.session.commit()
    
    return {"msg": "Appointment cancelled successfully"}, 200


@doctor_bp.route("/patient-history/<int:pat_id>")
@authorization("doctor")
def patient_history(pat_id):
    identity = get_jwt_identity()
    user = User.query.filter_by(username=identity,is_blocked=False).first_or_404()

    if not user.doctor:
        return jsonify({"msg": "Doctor profile not found"}), 401

    treatments = Treatment.query.join(Appointment).filter(
        Appointment.patient_id == pat_id,
        Appointment.doctor_id == user.doctor.id,
    ).all()

    data = []
    for treatment in treatments:
        data.append({
            "treatment_id": treatment.id,
            "appointment_id": treatment.appointment_id,
            "diagnosis": treatment.diagnosis,
            "prescription": treatment.prescription,
            "notes": treatment.notes,
            "appointment_date": treatment.appointment.appointment_date.strftime("%B%d,%Y") if treatment.appointment else None,
            "appointment_time": treatment.appointment.appointment_time.strftime("%H:%M") if treatment.appointment else "N/A"
        })
    
    return jsonify(data),200


@doctor_bp.route("/update-availability", methods=['PUT'])
@authorization("doctor")
def update_availability():
    identity = get_jwt_identity()
    user = User.query.filter_by(username=identity, is_blocked=False).first_or_404()

    if not user.doctor:
        return jsonify(msg="Doctor profile not found"), 401

    data = request.get_json()
    availability = data.get("availability")

    if not availability:
        return jsonify(msg="Availability is required"), 400

    user.doctor.availability = availability
    db.session.commit()
    cache.clear()

    return jsonify(msg="Availability updated successfully"), 200
