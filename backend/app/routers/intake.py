"""
Intake API endpoints
Handles patient intake, chatbot interactions, and intake analysis
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict, List
from datetime import datetime
import uuid


from app.database import get_db
from app.models.patient import Patient, IntakeResponse, PatientStatus
from app.models.risk import RiskAssessment, Alert
from app.services.ai_service import ai_service
from app.services.risk_scorer import risk_scorer


router = APIRouter(prefix="/api/intake", tags=["Intake"])


@router.post("/submit")
async def submit_intake(
    intake_data: Dict,
    db: Session = Depends(get_db)
):
    """
    Submit completed intake form with all responses

    Expected fields:
    - patient_info: Basic demographics
    - phq9_responses: PHQ-9 questionnaire (9 items)
    - gad7_responses: GAD-7 questionnaire (7 items)
    - text_responses: Primary concern, symptoms, goals, etc.
    - preferences: Therapist preferences
    """

    try:
        # 1. Create or update patient record
        patient_info = intake_data.get("patient_info", {})

        # Check if patient exists
        existing_patient = db.query(Patient).filter(
            Patient.email == patient_info.get("email")
        ).first()

        if existing_patient:
            patient = existing_patient
            # Check if intake already exists for this patient
            existing_intake = db.query(IntakeResponse).filter(
                IntakeResponse.patient_id == patient.id
            ).first()
            if existing_intake:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Intake already submitted for this patient. Please contact support to update."
                )
        else:
            patient = Patient(
                first_name=patient_info.get("first_name"),
                last_name=patient_info.get("last_name"),
                email=patient_info.get("email"),
                phone=patient_info.get("phone"),
                date_of_birth=patient_info.get("date_of_birth"),
                gender=patient_info.get("gender"),
                preferred_language=patient_info.get("preferred_language", "English"),
                address=patient_info.get("address"),
                city=patient_info.get("city"),
                state=patient_info.get("state"),
                zip_code=patient_info.get("zip_code"),
                insurance_provider=patient_info.get("insurance_provider"),
                insurance_id=patient_info.get("insurance_id"),
                emergency_contact_name=patient_info.get("emergency_contact_name"),
                emergency_contact_phone=patient_info.get("emergency_contact_phone"),
                status=PatientStatus.intake  # ← FIXED: was PatientStatus.INTAKE
            )
            db.add(patient)
            db.commit()
            db.refresh(patient)

        # 2. Create intake response
        phq9 = intake_data.get("phq9_responses", {})
        gad7 = intake_data.get("gad7_responses", {})
        text_resp = intake_data.get("text_responses", {})
        prefs = intake_data.get("preferences", {})

        intake_response = IntakeResponse(
            patient_id=patient.id,
            # PHQ-9
            phq9_interest=phq9.get("interest"),
            phq9_depressed=phq9.get("depressed"),
            phq9_sleep=phq9.get("sleep"),
            phq9_fatigue=phq9.get("fatigue"),
            phq9_appetite=phq9.get("appetite"),
            phq9_failure=phq9.get("failure"),
            phq9_concentration=phq9.get("concentration"),
            phq9_movement=phq9.get("movement"),
            phq9_self_harm=phq9.get("self_harm"),
            # GAD-7
            gad7_nervous=gad7.get("nervous"),
            gad7_control_worry=gad7.get("control_worry"),
            gad7_worry_much=gad7.get("worry_much"),
            gad7_trouble_relaxing=gad7.get("trouble_relaxing"),
            gad7_restless=gad7.get("restless"),
            gad7_irritable=gad7.get("irritable"),
            gad7_afraid=gad7.get("afraid"),
            # Text responses
            primary_concern=text_resp.get("primary_concern"),
            symptoms_description=text_resp.get("symptoms_description"),
            goals_for_therapy=text_resp.get("goals_for_therapy"),
            previous_therapy=text_resp.get("previous_therapy", False),
            previous_therapy_details=text_resp.get("previous_therapy_details"),
            current_medications=text_resp.get("current_medications"),
            substance_use=text_resp.get("substance_use"),
            # Preferences
            preferred_therapist_gender=prefs.get("therapist_gender"),
            preferred_session_format=prefs.get("session_format"),
            chatbot_transcript=intake_data.get("chatbot_transcript")
        )
        db.add(intake_response)
        db.commit()
        db.refresh(intake_response)

        # 3. Perform AI analysis
        ai_analysis = await ai_service.analyze_intake_text(
            primary_concern=text_resp.get("primary_concern", ""),
            symptoms=text_resp.get("symptoms_description"),
            goals=text_resp.get("goals_for_therapy")
        )

        # 4. Calculate risk score
        risk_result = risk_scorer.calculate_overall_risk(
            phq9_score=intake_response.phq9_total,
            gad7_score=intake_response.gad7_total,
            sentiment_score=ai_analysis.get("sentiment_score", 0.0),
            crisis_keywords=ai_analysis.get("crisis_keywords_detected", []),
            self_harm_score=phq9.get("self_harm", 0)
        )

        # 5. Create risk assessment
        risk_assessment = RiskAssessment(
            patient_id=patient.id,
            intake_id=intake_response.id,
            phq9_risk_score=risk_result["component_scores"]["phq9_risk"],
            gad7_risk_score=risk_result["component_scores"]["gad7_risk"],
            sentiment_score=ai_analysis.get("sentiment_score"),
            crisis_keywords_detected=ai_analysis.get("crisis_keywords_detected", []),
            self_harm_risk=(phq9.get("self_harm", 0) >= 2),
            overall_risk_score=risk_result["overall_risk_score"],
            risk_level=risk_result["risk_level"],
            ai_summary=ai_analysis.get("summary"),
            recommended_urgency=risk_result["recommended_urgency"]
        )
        db.add(risk_assessment)
        db.commit()
        db.refresh(risk_assessment)

        # 6. Create alerts if high risk or crisis detected
        if risk_result["risk_level"].value in ["high", "critical"]:
            alert = Alert(
                patient_id=patient.id,
                risk_assessment_id=risk_assessment.id,
                alert_type="high_risk",
                severity=risk_result["risk_level"].value,
                title=f"High Risk Patient: {patient.first_name} {patient.last_name}",
                description=f"Risk score: {risk_result['overall_risk_score']}/100. Urgency: {risk_result['recommended_urgency']}"
            )
            db.add(alert)

        if ai_analysis.get("crisis_keywords_detected"):
            crisis_alert = Alert(
                patient_id=patient.id,
                risk_assessment_id=risk_assessment.id,
                alert_type="crisis_keyword",
                severity="critical",
                title=f"Crisis Keywords Detected: {patient.first_name} {patient.last_name}",
                description=f"Keywords: {', '.join(ai_analysis['crisis_keywords_detected'])}"
            )
            db.add(crisis_alert)

        db.commit()

        return {
            "status": "success",
            "patient_id": str(patient.id),
            "risk_assessment": {
                "risk_level": risk_result["risk_level"].value,
                "risk_score": risk_result["overall_risk_score"],
                "urgency": risk_result["recommended_urgency"]
            },
            "message": "Intake submitted successfully. Our team will contact you shortly."
        }

    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing intake: {str(e)}"
        )


@router.post("/chat")
async def chatbot_interaction(
    message: Dict,
    db: Session = Depends(get_db)
):
    """
    Handle chatbot conversation during intake

    Expects:
    - user_message: str
    - conversation_history: List[Dict] (optional)
    """

    user_message = message.get("user_message")
    conversation_history = message.get("conversation_history", [])

    if not user_message:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="user_message is required"
        )

    try:
        bot_response = await ai_service.chatbot_response(
            conversation_history=conversation_history,
            current_question=user_message
        )

        return {
            "status": "success",
            "bot_message": bot_response
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Chatbot error: {str(e)}"
        )


@router.get("/patient/{patient_id}")
async def get_patient_intake(
    patient_id: str,
    db: Session = Depends(get_db)
):
    """
    Get patient's intake response
    """

    try:
        patient_uuid = uuid.UUID(patient_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid patient ID format"
        )

    intake = db.query(IntakeResponse).filter(
        IntakeResponse.patient_id == patient_uuid
    ).first()

    if not intake:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Intake not found for this patient"
        )

    return {
        "patient_id": str(intake.patient_id),
        "phq9_total": intake.phq9_total,
        "gad7_total": intake.gad7_total,
        "primary_concern": intake.primary_concern,
        "submitted_at": intake.submitted_at
    }
