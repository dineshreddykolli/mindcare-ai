"""
Therapist-related database models
"""
from sqlalchemy import Column, String, Integer, Boolean, DateTime, Text, ARRAY, Numeric
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
import uuid
from app.database import Base


class Therapist(Base):
    __tablename__ = "therapists"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    phone = Column(String(20))
    license_number = Column(String(50), unique=True, nullable=False)
    license_state = Column(String(2), nullable=False)
    specialties = Column(ARRAY(String), nullable=False)
    languages = Column(ARRAY(String), default=["English"])
    max_caseload = Column(Integer, default=30)
    current_caseload = Column(Integer, default=0)
    availability_hours = Column(JSONB)  # Weekly schedule
    accepts_high_risk = Column(Boolean, default=True)
    years_experience = Column(Integer)
    bio = Column(Text)
    success_rate = Column(Numeric(5, 2), default=0.0)
    active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    @property
    def has_capacity(self):
        """Check if therapist has capacity for new patients"""
        return self.current_caseload < self.max_caseload
    
    @property
    def capacity_remaining(self):
        """Calculate remaining capacity"""
        return max(0, self.max_caseload - self.current_caseload)
    
    @property
    def utilization_percent(self):
        """Calculate utilization percentage"""
        if self.max_caseload == 0:
            return 0.0
        return round((self.current_caseload / self.max_caseload) * 100, 2)
    
    def __repr__(self):
        return f"<Therapist {self.first_name} {self.last_name}>"


class Assignment(Base):
    __tablename__ = "assignments"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    patient_id = Column(UUID(as_uuid=True), nullable=False)
    therapist_id = Column(UUID(as_uuid=True), nullable=False)
    
    # Assignment details
    match_score = Column(Numeric(5, 2))
    match_reasoning = Column(Text)
    assigned_at = Column(DateTime(timezone=True), server_default=func.now())
    assigned_by = Column(String(100))
    
    # Status
    active = Column(Boolean, default=True)
    ended_at = Column(DateTime(timezone=True))
    end_reason = Column(Text)
    
    def __repr__(self):
        return f"<Assignment {self.patient_id} -> {self.therapist_id}>"
