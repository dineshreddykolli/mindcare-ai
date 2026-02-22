"""
Risk assessment and alert models
"""
from sqlalchemy import Column, String, Integer, Boolean, DateTime, Text, ARRAY, Numeric, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid
import enum
from app.database import Base


class RiskLevel(str, enum.Enum):
    low = "low"
    moderate = "moderate"
    high = "high"
    critical = "critical"


class RiskAssessment(Base):
    __tablename__ = "risk_assessments"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    patient_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    intake_id = Column(UUID(as_uuid=True))
    
    # Risk components
    phq9_risk_score = Column(Numeric(5, 2), nullable=False)
    gad7_risk_score = Column(Numeric(5, 2), nullable=False)
    sentiment_score = Column(Numeric(5, 2))  # -1.0 to 1.0
    crisis_keywords_detected = Column(ARRAY(String))
    self_harm_risk = Column(Boolean, default=False)
    
    # Overall risk
    overall_risk_score = Column(Numeric(5, 2), nullable=False)
    risk_level = Column(Enum(RiskLevel), nullable=False)
    
    # AI analysis
    ai_summary = Column(Text)
    recommended_urgency = Column(String(50))
    
    # Metadata
    assessed_by = Column(String(50), default="AI_SYSTEM")
    assessed_at = Column(DateTime(timezone=True), server_default=func.now())
    reviewed_by_clinician = Column(Boolean, default=False)
    clinician_notes = Column(Text)
    
    def __repr__(self):
        return f"<RiskAssessment {self.risk_level} for patient {self.patient_id}>"


class DropoutPrediction(Base):
    __tablename__ = "dropout_predictions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    patient_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    
    # Prediction
    dropout_probability = Column(Numeric(5, 2), nullable=False)
    risk_factors = Column(ARRAY(String))
    
    # Features used
    sessions_attended = Column(Integer, default=0)
    sessions_cancelled = Column(Integer, default=0)
    sessions_no_show = Column(Integer, default=0)
    avg_response_time_hours = Column(Numeric(10, 2))
    sentiment_trend = Column(Numeric(5, 2))
    days_since_last_session = Column(Integer)
    
    # Model metadata
    model_version = Column(String(50))
    predicted_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Intervention tracking
    intervention_recommended = Column(Boolean, default=False)
    intervention_taken = Column(Boolean, default=False)
    intervention_notes = Column(Text)
    
    def __repr__(self):
        return f"<DropoutPrediction {self.dropout_probability}% for patient {self.patient_id}>"


class Alert(Base):
    __tablename__ = "alerts"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    patient_id = Column(UUID(as_uuid=True), nullable=False)
    
    # Alert details
    alert_type = Column(String(50), nullable=False)
    severity = Column(String(20), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    
    # Related entities
    risk_assessment_id = Column(UUID(as_uuid=True))
    dropout_prediction_id = Column(UUID(as_uuid=True))
    
    # Status
    acknowledged = Column(Boolean, default=False)
    acknowledged_by = Column(String(100))
    acknowledged_at = Column(DateTime(timezone=True))
    resolved = Column(Boolean, default=False)
    resolved_at = Column(DateTime(timezone=True))
    resolution_notes = Column(Text)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<Alert {self.alert_type} - {self.severity}>"
