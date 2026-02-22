"""
Input Validation Schemas
Comprehensive Pydantic models with validation for all forms
"""
from pydantic import BaseModel, EmailStr, validator, Field
from typing import Optional, List
from datetime import date
import re


class PatientInfoSchema(BaseModel):
    """Patient demographic information validation"""
    first_name: str = Field(..., min_length=2, max_length=100)
    last_name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    phone: str = Field(..., min_length=10, max_length=20)
    date_of_birth: date
    gender: Optional[str] = Field(None, max_length=50)
    preferred_language: str = Field(default="English", max_length=50)
    address: Optional[str] = Field(None, max_length=500)
    city: Optional[str] = Field(None, max_length=100)
    state: Optional[str] = Field(None, min_length=2, max_length=2)
    zip_code: Optional[str] = Field(None, pattern=r'^\d{5}(-\d{4})?$')
    insurance_provider: Optional[str] = Field(None, max_length=100)
    insurance_id: Optional[str] = Field(None, max_length=100)
    emergency_contact_name: Optional[str] = Field(None, max_length=200)
    emergency_contact_phone: Optional[str] = Field(None, min_length=10, max_length=20)
    
    @validator('first_name', 'last_name')
    def validate_name(cls, v):
        if not v.replace(' ', '').replace('-', '').isalpha():
            raise ValueError('Name must contain only letters, spaces, and hyphens')
        return v.strip().title()
    
    @validator('phone', 'emergency_contact_phone')
    def validate_phone(cls, v):
        if v is None:
            return v
        # Remove all non-digit characters
        digits = re.sub(r'\D', '', v)
        if len(digits) < 10 or len(digits) > 15:
            raise ValueError('Phone number must be between 10 and 15 digits')
        return digits
    
    @validator('date_of_birth')
    def validate_dob(cls, v):
        from datetime import date
        if v > date.today():
            raise ValueError('Date of birth cannot be in the future')
        age = (date.today() - v).days // 365
        if age < 13:
            raise ValueError('Patient must be at least 13 years old')
        if age > 120:
            raise ValueError('Invalid date of birth')
        return v
    
    @validator('state')
    def validate_state(cls, v):
        if v is None:
            return v
        us_states = [
            'AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'FL', 'GA',
            'HI', 'ID', 'IL', 'IN', 'IA', 'KS', 'KY', 'LA', 'ME', 'MD',
            'MA', 'MI', 'MN', 'MS', 'MO', 'MT', 'NE', 'NV', 'NH', 'NJ',
            'NM', 'NY', 'NC', 'ND', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC',
            'SD', 'TN', 'TX', 'UT', 'VT', 'VA', 'WA', 'WV', 'WI', 'WY'
        ]
        if v.upper() not in us_states:
            raise ValueError('Invalid US state code')
        return v.upper()


class PHQ9ResponseSchema(BaseModel):
    """PHQ-9 Depression Screening validation"""
    interest: int = Field(..., ge=0, le=3, description="Little interest or pleasure")
    depressed: int = Field(..., ge=0, le=3, description="Feeling down, depressed, or hopeless")
    sleep: int = Field(..., ge=0, le=3, description="Trouble falling or staying asleep")
    fatigue: int = Field(..., ge=0, le=3, description="Feeling tired or having little energy")
    appetite: int = Field(..., ge=0, le=3, description="Poor appetite or overeating")
    failure: int = Field(..., ge=0, le=3, description="Feeling bad about yourself")
    concentration: int = Field(..., ge=0, le=3, description="Trouble concentrating")
    movement: int = Field(..., ge=0, le=3, description="Moving or speaking slowly")
    self_harm: int = Field(..., ge=0, le=3, description="Thoughts of self-harm")
    
    @validator('*')
    def validate_score(cls, v):
        if v not in [0, 1, 2, 3]:
            raise ValueError('Score must be 0, 1, 2, or 3')
        return v


class GAD7ResponseSchema(BaseModel):
    """GAD-7 Anxiety Screening validation"""
    nervous: int = Field(..., ge=0, le=3, description="Feeling nervous, anxious, or on edge")
    control_worry: int = Field(..., ge=0, le=3, description="Not being able to stop or control worrying")
    worry_much: int = Field(..., ge=0, le=3, description="Worrying too much about different things")
    trouble_relaxing: int = Field(..., ge=0, le=3, description="Trouble relaxing")
    restless: int = Field(..., ge=0, le=3, description="Being so restless that it's hard to sit still")
    irritable: int = Field(..., ge=0, le=3, description="Becoming easily annoyed or irritable")
    afraid: int = Field(..., ge=0, le=3, description="Feeling afraid as if something awful might happen")
    
    @validator('*')
    def validate_score(cls, v):
        if v not in [0, 1, 2, 3]:
            raise ValueError('Score must be 0, 1, 2, or 3')
        return v


class TextResponsesSchema(BaseModel):
    """Free-text responses validation"""
    primary_concern: str = Field(..., min_length=10, max_length=2000)
    symptoms_description: Optional[str] = Field(None, max_length=2000)
    goals_for_therapy: Optional[str] = Field(None, max_length=2000)
    previous_therapy: bool = False
    previous_therapy_details: Optional[str] = Field(None, max_length=1000)
    current_medications: Optional[str] = Field(None, max_length=1000)
    substance_use: Optional[str] = Field(None, max_length=1000)
    
    @validator('primary_concern', 'symptoms_description', 'goals_for_therapy')
    def validate_text(cls, v):
        if v is None:
            return v
        # Remove excessive whitespace
        v = ' '.join(v.split())
        # Check for minimum meaningful content
        if len(v.strip()) < 10 and v is not None:
            raise ValueError('Please provide more detailed information (at least 10 characters)')
        return v


class PreferencesSchema(BaseModel):
    """Patient preferences validation"""
    therapist_gender: Optional[str] = Field(None, pattern=r'^(male|female|no_preference)$')
    session_format: Optional[str] = Field(None, pattern=r'^(in_person|telehealth|hybrid)$')


class intakeSubmissionSchema(BaseModel):
    """Complete intake submission validation"""
    patient_info: PatientInfoSchema
    phq9_responses: PHQ9ResponseSchema
    gad7_responses: GAD7ResponseSchema
    text_responses: TextResponsesSchema
    preferences: PreferencesSchema
    chatbot_transcript: Optional[List[dict]] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "patient_info": {
                    "first_name": "John",
                    "last_name": "Doe",
                    "email": "john.doe@example.com",
                    "phone": "555-123-4567",
                    "date_of_birth": "1990-01-01"
                },
                "phq9_responses": {
                    "interest": 2,
                    "depressed": 2,
                    "sleep": 1,
                    "fatigue": 2,
                    "appetite": 1,
                    "failure": 1,
                    "concentration": 1,
                    "movement": 0,
                    "self_harm": 0
                },
                "gad7_responses": {
                    "nervous": 2,
                    "control_worry": 2,
                    "worry_much": 3,
                    "trouble_relaxing": 2,
                    "restless": 1,
                    "irritable": 1,
                    "afraid": 1
                },
                "text_responses": {
                    "primary_concern": "I've been feeling anxious and overwhelmed",
                    "symptoms_description": "Difficulty sleeping, racing thoughts",
                    "goals_for_therapy": "Learn coping strategies for anxiety"
                },
                "preferences": {
                    "therapist_gender": "no_preference",
                    "session_format": "telehealth"
                }
            }
        }


class ChatMessageSchema(BaseModel):
    """Chatbot message validation"""
    user_message: str = Field(..., min_length=1, max_length=1000)
    conversation_history: Optional[List[dict]] = []
    
    @validator('user_message')
    def validate_message(cls, v):
        v = v.strip()
        if len(v) == 0:
            raise ValueError('Message cannot be empty')
        # Check for spam patterns (repeated characters)
        if len(set(v)) < 3 and len(v) > 10:
            raise ValueError('Message appears to be spam')
        return v


class TherapistAssignmentSchema(BaseModel):
    """Therapist assignment validation"""
    patient_id: str = Field(..., pattern=r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$')
    therapist_id: str = Field(..., pattern=r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$')
    assigned_by: str = Field(..., min_length=3, max_length=100)
    
    @validator('patient_id', 'therapist_id')
    def validate_uuid(cls, v):
        import uuid
        try:
            uuid.UUID(v)
        except ValueError:
            raise ValueError('Invalid UUID format')
        return v


class AlertAcknowledgementSchema(BaseModel):
    """Alert acknowledgement validation"""
    alert_id: str
    acknowledged_by: EmailStr
    notes: Optional[str] = Field(None, max_length=500)


class AlertResolutionSchema(BaseModel):
    """Alert resolution validation"""
    alert_id: str
    resolution_notes: str = Field(..., min_length=10, max_length=1000)
    
    @validator('resolution_notes')
    def validate_notes(cls, v):
        v = v.strip()
        if len(v) < 10:
            raise ValueError('Resolution notes must be at least 10 characters')
        return v


# Error response models
class ValidationError(BaseModel):
    """Validation error response"""
    field: str
    message: str


class ErrorResponse(BaseModel):
    """Standard error response"""
    status: str = "error"
    message: str
    errors: Optional[List[ValidationError]] = None


# Success response models
class SuccessResponse(BaseModel):
    """Standard success response"""
    status: str = "success"
    message: str
    data: Optional[dict] = None
