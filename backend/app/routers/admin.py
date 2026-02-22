"""
Admin Dashboard API endpoints
Provides analytics, metrics, and oversight functions
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import List, Optional
from datetime import datetime, timedelta

from app.database import get_db
from app.models.patient import Patient, PatientStatus
from app.models.therapist import Therapist, Assignment
from app.models.risk import RiskAssessment, RiskLevel, Alert, DropoutPrediction

router = APIRouter(prefix="/api/admin", tags=["Admin"])


@router.get("/dashboard")
async def get_dashboard_metrics(
    db: Session = Depends(get_db)
):
    """
    Get comprehensive dashboard metrics
    """
    
    # active patients
    active_patients = db.query(func.count(Patient.id)).filter(
        Patient.status == PatientStatus.active
    ).scalar()
    
    # intake patients (waiting for assignment)
    intake_patients = db.query(func.count(Patient.id)).filter(
        Patient.status == PatientStatus.intake
    ).scalar()
    
    # high risk patients
    high_risk_count = db.query(func.count(RiskAssessment.id)).filter(
        RiskAssessment.risk_level.in_([RiskLevel.high, RiskLevel.critical])
    ).scalar()
    
    # critical patients needing immediate attention
    critical_count = db.query(func.count(RiskAssessment.id)).filter(
        RiskAssessment.risk_level == RiskLevel.critical
    ).scalar()
    
    # active alerts (unresolved)
    active_alerts = db.query(func.count(Alert.id)).filter(
        Alert.resolved == False
    ).scalar()
    
    # Therapist utilization
    therapist_stats = db.query(
        func.count(Therapist.id).label("total_therapists"),
        func.sum(Therapist.current_caseload).label("total_patients_assigned"),
        func.sum(Therapist.max_caseload).label("total_capacity"),
        func.avg(Therapist.current_caseload / Therapist.max_caseload * 100).label("avg_utilization")
    ).filter(
        Therapist.active == True
    ).first()
    
    # Patients at high dropout risk
    high_dropout_risk = db.query(func.count(DropoutPrediction.id)).filter(
        DropoutPrediction.dropout_probability >= 70
    ).scalar()
    
    # Recent intakes (last 7 days)
    seven_days_ago = datetime.now() - timedelta(days=7)
    recent_intakes = db.query(func.count(Patient.id)).filter(
        Patient.created_at >= seven_days_ago,
        Patient.status == PatientStatus.intake
    ).scalar()
    
    return {
        "overview": {
            "active_patients": active_patients or 0,
            "intake_queue": intake_patients or 0,
            "high_risk_patients": high_risk_count or 0,
            "critical_patients": critical_count or 0,
            "active_alerts": active_alerts or 0,
            "high_dropout_risk": high_dropout_risk or 0,
            "recent_intakes_7d": recent_intakes or 0
        },
        "therapists": {
            "total_active": therapist_stats.total_therapists or 0,
            "total_assigned_patients": int(therapist_stats.total_patients_assigned or 0),
            "total_capacity": int(therapist_stats.total_capacity or 0),
            "average_utilization_percent": round(float(therapist_stats.avg_utilization or 0), 2)
        },
        "timestamp": datetime.now().isoformat()
    }


@router.get("/high-risk-patients")
async def get_high_risk_patients(
    limit: int = Query(20, le=100),
    db: Session = Depends(get_db)
):
    """
    Get list of high-risk patients requiring attention
    """
    
    # Query high risk patients with their latest assessment
    results = db.query(
        Patient,
        RiskAssessment
    ).join(
        RiskAssessment, Patient.id == RiskAssessment.patient_id
    ).filter(
        RiskAssessment.risk_level.in_([RiskLevel.high, RiskLevel.critical])
    ).order_by(
        desc(RiskAssessment.overall_risk_score)
    ).limit(limit).all()
    
    patients = []
    for patient, risk in results:
        # Check if assigned
        assignment = db.query(Assignment).filter(
            Assignment.patient_id == patient.id,
            Assignment.active == True
        ).first()
        
        patients.append({
            "patient_id": str(patient.id),
            "name": f"{patient.first_name} {patient.last_name}",
            "email": patient.email,
            "phone": patient.phone,
            "risk_level": risk.risk_level.value,
            "risk_score": float(risk.overall_risk_score),
            "urgency": risk.recommended_urgency,
            "crisis_keywords": risk.crisis_keywords_detected or [],
            "assessed_at": risk.assessed_at.isoformat(),
            "has_therapist": assignment is not None,
            "therapist_id": str(assignment.therapist_id) if assignment else None,
            "status": patient.status.value
        })
    
    return {
        "patients": patients,
        "count": len(patients)
    }


@router.get("/alerts")
async def get_active_alerts(
    severity: Optional[str] = None,
    limit: int = Query(50, le=200),
    db: Session = Depends(get_db)
):
    """
    Get active (unresolved) alerts
    """
    
    query = db.query(Alert, Patient).join(
        Patient, Alert.patient_id == Patient.id
    ).filter(
        Alert.resolved == False
    )
    
    if severity:
        query = query.filter(Alert.severity == severity)
    
    query = query.order_by(desc(Alert.created_at)).limit(limit)
    
    results = query.all()
    
    alerts = []
    for alert, patient in results:
        alerts.append({
            "alert_id": str(alert.id),
            "patient_id": str(patient.id),
            "patient_name": f"{patient.first_name} {patient.last_name}",
            "alert_type": alert.alert_type,
            "severity": alert.severity,
            "title": alert.title,
            "description": alert.description,
            "created_at": alert.created_at.isoformat(),
            "acknowledged": alert.acknowledged,
            "acknowledged_by": alert.acknowledged_by
        })
    
    return {
        "alerts": alerts,
        "count": len(alerts)
    }


@router.post("/alerts/{alert_id}/acknowledge")
async def acknowledge_alert(
    alert_id: str,
    acknowledged_by: str,
    db: Session = Depends(get_db)
):
    """
    Acknowledge an alert
    """
    
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    alert.acknowledged = True
    alert.acknowledged_by = acknowledged_by
    alert.acknowledged_at = datetime.now()
    
    db.commit()
    
    return {"status": "success", "message": "Alert acknowledged"}


@router.post("/alerts/{alert_id}/resolve")
async def resolve_alert(
    alert_id: str,
    resolution_notes: str,
    db: Session = Depends(get_db)
):
    """
    Resolve an alert
    """
    
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    alert.resolved = True
    alert.resolved_at = datetime.now()
    alert.resolution_notes = resolution_notes
    
    db.commit()
    
    return {"status": "success", "message": "Alert resolved"}


@router.get("/therapists/caseloads")
async def get_therapist_caseloads(
    db: Session = Depends(get_db)
):
    """
    Get all therapists with their caseload information
    """
    
    therapists = db.query(Therapist).filter(
        Therapist.active == True
    ).all()
    
    result = []
    for therapist in therapists:
        # Count active assignments
        active_count = db.query(func.count(Assignment.id)).filter(
            Assignment.therapist_id == therapist.id,
            Assignment.active == True
        ).scalar()
        
        result.append({
            "therapist_id": str(therapist.id),
            "name": f"{therapist.first_name} {therapist.last_name}",
            "email": therapist.email,
            "specialties": therapist.specialties,
            "languages": therapist.languages,
            "max_caseload": therapist.max_caseload,
            "current_caseload": active_count or 0,
            "capacity_remaining": max(0, therapist.max_caseload - (active_count or 0)),
            "utilization_percent": round(((active_count or 0) / therapist.max_caseload * 100), 2) if therapist.max_caseload > 0 else 0,
            "accepts_high_risk": therapist.accepts_high_risk,
            "years_experience": therapist.years_experience
        })
    
    # Sort by utilization
    result.sort(key=lambda x: x["utilization_percent"], reverse=True)
    
    return {
        "therapists": result,
        "count": len(result)
    }


@router.post("/assign-patient")
async def manually_assign_patient(
    assignment_data: dict,
    db: Session = Depends(get_db)
):
    """
    Manually assign a patient to a therapist
    """
    
    patient_id = assignment_data.get("patient_id")
    therapist_id = assignment_data.get("therapist_id")
    assigned_by = assignment_data.get("assigned_by", "admin")
    
    # Verify patient exists
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    # Verify therapist exists and has capacity
    therapist = db.query(Therapist).filter(Therapist.id == therapist_id).first()
    if not therapist:
        raise HTTPException(status_code=404, detail="Therapist not found")
    
    if not therapist.has_capacity:
        raise HTTPException(status_code=400, detail="Therapist at full capacity")
    
    # Create assignment
    assignment = Assignment(
        patient_id=patient_id,
        therapist_id=therapist_id,
        match_score=None,  # Manual assignment
        match_reasoning="Manually assigned by admin",
        assigned_by=assigned_by,
        active=True
    )
    
    db.add(assignment)
    
    # Update patient status
    patient.status = PatientStatus.active
    
    # Update therapist caseload
    therapist.current_caseload += 1
    
    db.commit()
    
    return {
        "status": "success",
        "assignment_id": str(assignment.id),
        "message": f"Patient assigned to {therapist.first_name} {therapist.last_name}"
    }
