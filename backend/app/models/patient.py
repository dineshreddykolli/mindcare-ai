"""
Patient-related database models
"""
from sqlalchemy import Column, String, Date, Enum, DateTime, Text, Boolean, Integer
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
import uuid
import enum
from app.database import Base



class PatientStatus(str, enum.Enum):
    intake = "intake"
    active = "active"
    inactive = "inactive"
    discharged = "discharged"



class Patient(Base):
    __tablename__ = "patients"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    phone = Column(String(20))
    date_of_birth = Column(Date, nullable=False)
    gender = Column(String(50))
    preferred_language = Column(String(50), default="English")
    address = Column(Text)
    city = Column(String(100))
    state = Column(String(2))
    zip_code = Column(String(10))
    insurance_provider = Column(String(100))
    insurance_id = Column(String(100))
    emergency_contact_name = Column(String(200))
    emergency_contact_phone = Column(String(20))
    status = Column(Enum(PatientStatus), default=PatientStatus.intake)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<Patient {self.first_name} {self.last_name}>"



class IntakeResponse(Base):
    __tablename__ = "intake_responses"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    patient_id = Column(UUID(as_uuid=True), nullable=False, unique=True)
    
    # PHQ-9 Depression Screening
    phq9_interest = Column(Integer, nullable=True)
    phq9_depressed = Column(Integer, nullable=True)
    phq9_sleep = Column(Integer, nullable=True)
    phq9_fatigue = Column(Integer, nullable=True)
    phq9_appetite = Column(Integer, nullable=True)
    phq9_failure = Column(Integer, nullable=True)
    phq9_concentration = Column(Integer, nullable=True)
    phq9_movement = Column(Integer, nullable=True)
    phq9_self_harm = Column(Integer, nullable=True)
    
    # GAD-7 Anxiety Screening
    gad7_nervous = Column(Integer, nullable=True)
    gad7_control_worry = Column(Integer, nullable=True)
    gad7_worry_much = Column(Integer, nullable=True)
    gad7_trouble_relaxing = Column(Integer, nullable=True)
    gad7_restless = Column(Integer, nullable=True)
    gad7_irritable = Column(Integer, nullable=True)
    gad7_afraid = Column(Integer, nullable=True)
    
    # Free-text responses
    primary_concern = Column(Text, nullable=False)
    symptoms_description = Column(Text)
    goals_for_therapy = Column(Text)
    previous_therapy = Column(Boolean, default=False)
    previous_therapy_details = Column(Text)
    current_medications = Column(Text)
    substance_use = Column(Text)
    
    # Preferences
    preferred_therapist_gender = Column(String(50))
    preferred_session_format = Column(String(50))
    
    # Metadata
    submitted_at = Column(DateTime(timezone=True), server_default=func.now())
    chatbot_transcript = Column(JSONB)
    
    @property
    def phq9_total(self):
        """Calculate PHQ-9 total score"""
        scores = [
            self.phq9_interest, self.phq9_depressed, self.phq9_sleep,
            self.phq9_fatigue, self.phq9_appetite, self.phq9_failure,
            self.phq9_concentration, self.phq9_movement, self.phq9_self_harm
        ]
        return sum(s for s in scores if s is not None)
    
    @property
    def gad7_total(self):
        """Calculate GAD-7 total score"""
        scores = [
            self.gad7_nervous, self.gad7_control_worry, self.gad7_worry_much,
            self.gad7_trouble_relaxing, self.gad7_restless,
            self.gad7_irritable, self.gad7_afraid
        ]
        return sum(s for s in scores if s is not None)
    
    def __repr__(self):
        return f"<IntakeResponse for patient {self.patient_id}>"
