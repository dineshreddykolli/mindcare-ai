"""
Therapist Matching API endpoints
AI-powered patient-therapist matching
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict
import uuid


from app.database import get_db
from app.models.patient import Patient, IntakeResponse
from app.models.therapist import Therapist, Assignment
from app.models.risk import RiskAssessment
from app.services.matching_service import therapist_matcher
from app.services.ai_service import ai_service


router = APIRouter(prefix="/api/matching", tags=["Matching"])



@router.post("/recommend")
async def get_therapist_recommendations(
    request_data: Dict,
    db: Session = Depends(get_db)
):
    """
    Get AI-powered therapist recommendations for a patient

    Expects:
    - patient_id: str (UUID)
    - top_n: int (optional, default 3)
    """

    patient_id_str = request_data.get("patient_id")
    top_n = request_data.get("top_n", 3)

    if not patient_id_str:
        raise HTTPException(status_code=400, detail="patient_id is required")

    try:
        patient_id = uuid.UUID(patient_id_str)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid patient ID format")

    # Get patient
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    # Get patient's intake
    intake = db.query(IntakeResponse).filter(
        IntakeResponse.patient_id == patient_id
    ).first()

    if not intake:
        raise HTTPException(status_code=404, detail="No intake found for patient")

    # Get patient's risk assessment
    risk_assessment = db.query(RiskAssessment).filter(
        RiskAssessment.patient_id == patient_id
    ).order_by(RiskAssessment.assessed_at.desc()).first()

    # Prepare patient data for matching
    patient_data = {
        "patient_id": str(patient.id),
        "risk_level": risk_assessment.risk_level if risk_assessment else None,
        "primary_concern": intake.primary_concern,
        "preferred_language": patient.preferred_language,
        "preferred_gender": intake.preferred_therapist_gender
    }

    # Get recommendations
    matches = therapist_matcher.find_best_matches(
        db=db,
        patient_data=patient_data,
        top_n=top_n
    )

    # Format results with AI-generated reasoning
    recommendations = []
    for therapist, score, reasoning in matches:
        therapist_info = {
            "name": f"{therapist.first_name} {therapist.last_name}",
            "specialties": therapist.specialties,
            "languages": therapist.languages,
            "years_experience": therapist.years_experience,
            "accepts_high_risk": therapist.accepts_high_risk
        }

        ai_reasoning = await ai_service.generate_therapist_match_reasoning(
            patient_info=patient_data,
            therapist_info=therapist_info,
            match_score=score
        )

        recommendations.append({
            "therapist_id": str(therapist.id),
            "name": f"{therapist.first_name} {therapist.last_name}",
            "email": therapist.email,
            "specialties": therapist.specialties,
            "languages": therapist.languages,
            "years_experience": therapist.years_experience,
            "match_score": score,
            "match_reasoning": reasoning,
            "ai_explanation": ai_reasoning,
            "capacity_remaining": therapist.capacity_remaining,
            "bio": therapist.bio
        })

    return {
        "patient_id": str(patient.id),
        "recommendations": recommendations,
        "count": len(recommendations)
    }



@router.post("/assign")
async def assign_recommended_therapist(
    assignment_data: Dict,
    db: Session = Depends(get_db)
):
    """
    Assign patient to a recommended therapist

    Expects:
    - patient_id: str
    - therapist_id: str
    - match_score: float (from recommendation)
    - match_reasoning: str (from recommendation)
    """

    patient_id = assignment_data.get("patient_id")
    therapist_id = assignment_data.get("therapist_id")
    match_score = assignment_data.get("match_score")
    match_reasoning = assignment_data.get("match_reasoning")

    if not patient_id or not therapist_id:
        raise HTTPException(status_code=400, detail="patient_id and therapist_id required")

    try:
        patient_uuid = uuid.UUID(patient_id)
        therapist_uuid = uuid.UUID(therapist_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid ID format")

    patient = db.query(Patient).filter(Patient.id == patient_uuid).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    therapist = db.query(Therapist).filter(Therapist.id == therapist_uuid).first()
    if not therapist:
        raise HTTPException(status_code=404, detail="Therapist not found")

    if not therapist.has_capacity:
        raise HTTPException(status_code=400, detail="Therapist at full capacity")

    existing = db.query(Assignment).filter(
        Assignment.patient_id == patient_uuid,
        Assignment.active == True
    ).first()

    if existing:
        raise HTTPException(status_code=400, detail="Patient already has an active assignment")

    assignment = Assignment(
        patient_id=patient_uuid,
        therapist_id=therapist_uuid,
        match_score=match_score,
        match_reasoning=match_reasoning,
        assigned_by="AI_SYSTEM",
        active=True
    )

    db.add(assignment)

    patient.status = "active"
    therapist.current_caseload += 1

    db.commit()
    db.refresh(assignment)

    return {
        "status": "success",
        "assignment_id": str(assignment.id),
        "message": f"Patient successfully assigned to {therapist.first_name} {therapist.last_name}",
        "therapist_email": therapist.email
    }



@router.get("/availability")
async def check_therapist_availability(
    specialty: str = None,
    language: str = None,
    accepts_high_risk: bool = None,
    db: Session = Depends(get_db)
):
    """
    Check therapist availability with filters
    """

    query = db.query(Therapist).filter(
        Therapist.active == True
    )

    if specialty:
        query = query.filter(Therapist.specialties.contains([specialty]))

    if language:
        query = query.filter(Therapist.languages.contains([language]))

    if accepts_high_risk is not None:
        query = query.filter(Therapist.accepts_high_risk == accepts_high_risk)

    therapists = query.all()

    available = []
    for therapist in therapists:
        if therapist.has_capacity:
            available.append({
                "therapist_id": str(therapist.id),
                "name": f"{therapist.first_name} {therapist.last_name}",
                "specialties": therapist.specialties,
                "languages": therapist.languages,
                "capacity_remaining": therapist.capacity_remaining,
                "utilization_percent": therapist.utilization_percent
            })

    return {
        "available_therapists": available,
        "count": len(available)
    }
