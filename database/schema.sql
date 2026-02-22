-- MindCare AI Database Schema
-- PostgreSQL 14+

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create ENUM types
CREATE TYPE risk_level AS ENUM ('low', 'moderate', 'high', 'critical');
CREATE TYPE patient_status AS ENUM ('intake', 'active', 'inactive', 'discharged');
CREATE TYPE session_status AS ENUM ('scheduled', 'completed', 'cancelled', 'no_show');
CREATE TYPE therapist_specialty AS ENUM ('anxiety', 'depression', 'trauma', 'addiction', 'family', 'couples', 'child', 'eating_disorders', 'general');

-- Patients table
CREATE TABLE patients (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    phone VARCHAR(20),
    date_of_birth DATE NOT NULL,
    gender VARCHAR(50),
    preferred_language VARCHAR(50) DEFAULT 'English',
    address TEXT,
    city VARCHAR(100),
    state VARCHAR(2),
    zip_code VARCHAR(10),
    insurance_provider VARCHAR(100),
    insurance_id VARCHAR(100),
    emergency_contact_name VARCHAR(200),
    emergency_contact_phone VARCHAR(20),
    status patient_status DEFAULT 'intake',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Therapists table
CREATE TABLE therapists (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    phone VARCHAR(20),
    license_number VARCHAR(50) UNIQUE NOT NULL,
    license_state VARCHAR(2) NOT NULL,
    specialties therapist_specialty[] NOT NULL,
    languages VARCHAR(50)[] DEFAULT ARRAY['English'],
    max_caseload INTEGER DEFAULT 30,
    current_caseload INTEGER DEFAULT 0,
    availability_hours JSONB, -- Store weekly schedule
    accepts_high_risk BOOLEAN DEFAULT true,
    years_experience INTEGER,
    bio TEXT,
    success_rate DECIMAL(5,2) DEFAULT 0.0, -- Calculated field
    active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Intake responses table
CREATE TABLE intake_responses (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    patient_id UUID REFERENCES patients(id) ON DELETE CASCADE,
    
    -- PHQ-9 Depression Screening (9 questions, 0-3 each, total 0-27)
    phq9_interest INTEGER CHECK (phq9_interest BETWEEN 0 AND 3),
    phq9_depressed INTEGER CHECK (phq9_depressed BETWEEN 0 AND 3),
    phq9_sleep INTEGER CHECK (phq9_sleep BETWEEN 0 AND 3),
    phq9_fatigue INTEGER CHECK (phq9_fatigue BETWEEN 0 AND 3),
    phq9_appetite INTEGER CHECK (phq9_appetite BETWEEN 0 AND 3),
    phq9_failure INTEGER CHECK (phq9_failure BETWEEN 0 AND 3),
    phq9_concentration INTEGER CHECK (phq9_concentration BETWEEN 0 AND 3),
    phq9_movement INTEGER CHECK (phq9_movement BETWEEN 0 AND 3),
    phq9_self_harm INTEGER CHECK (phq9_self_harm BETWEEN 0 AND 3),
    phq9_total INTEGER GENERATED ALWAYS AS (
        phq9_interest + phq9_depressed + phq9_sleep + phq9_fatigue + 
        phq9_appetite + phq9_failure + phq9_concentration + phq9_movement + phq9_self_harm
    ) STORED,
    
    -- GAD-7 Anxiety Screening (7 questions, 0-3 each, total 0-21)
    gad7_nervous INTEGER CHECK (gad7_nervous BETWEEN 0 AND 3),
    gad7_control_worry INTEGER CHECK (gad7_control_worry BETWEEN 0 AND 3),
    gad7_worry_much INTEGER CHECK (gad7_worry_much BETWEEN 0 AND 3),
    gad7_trouble_relaxing INTEGER CHECK (gad7_trouble_relaxing BETWEEN 0 AND 3),
    gad7_restless INTEGER CHECK (gad7_restless BETWEEN 0 AND 3),
    gad7_irritable INTEGER CHECK (gad7_irritable BETWEEN 0 AND 3),
    gad7_afraid INTEGER CHECK (gad7_afraid BETWEEN 0 AND 3),
    gad7_total INTEGER GENERATED ALWAYS AS (
        gad7_nervous + gad7_control_worry + gad7_worry_much + 
        gad7_trouble_relaxing + gad7_restless + gad7_irritable + gad7_afraid
    ) STORED,
    
    -- Free-text responses
    primary_concern TEXT NOT NULL,
    symptoms_description TEXT,
    goals_for_therapy TEXT,
    previous_therapy BOOLEAN DEFAULT false,
    previous_therapy_details TEXT,
    current_medications TEXT,
    substance_use TEXT,
    
    -- Preferences
    preferred_therapist_gender VARCHAR(50),
    preferred_session_format VARCHAR(50), -- in-person, telehealth, hybrid
    
    -- Metadata
    submitted_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    chatbot_transcript JSONB, -- Store full chatbot conversation
    
    UNIQUE(patient_id)
);

-- Risk assessments table
CREATE TABLE risk_assessments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    patient_id UUID REFERENCES patients(id) ON DELETE CASCADE,
    intake_id UUID REFERENCES intake_responses(id) ON DELETE CASCADE,
    
    phq9_risk_score DECIMAL(5,2) NOT NULL, 
    gad7_risk_score DECIMAL(5,2) NOT NULL,
    sentiment_score DECIMAL(5,2),
    crisis_keywords_detected TEXT[], 
    self_harm_risk BOOLEAN DEFAULT false,
    
    overall_risk_score DECIMAL(5,2) NOT NULL CHECK (overall_risk_score BETWEEN 0 AND 100),
    risk_level risk_level NOT NULL,
    
    ai_summary TEXT,
    recommended_urgency VARCHAR(50),
    
    assessed_by VARCHAR(50) DEFAULT 'AI_SYSTEM',
    assessed_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    reviewed_by_clinician BOOLEAN DEFAULT false,
    clinician_notes TEXT
);

-- Create indexes separately
CREATE INDEX idx_risk_level ON risk_assessments(risk_level);
CREATE INDEX idx_patient_id ON risk_assessments(patient_id);

-- Therapist-patient assignments
CREATE TABLE assignments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    patient_id UUID REFERENCES patients(id) ON DELETE CASCADE,
    therapist_id UUID REFERENCES therapists(id) ON DELETE CASCADE,
    
    -- Assignment details
    match_score DECIMAL(5,2), -- AI-generated match quality 0-100
    match_reasoning TEXT, -- AI explanation of match
    assigned_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    assigned_by VARCHAR(100), -- 'AI_SYSTEM' or admin email
    
    -- Status
    active BOOLEAN DEFAULT true,
    ended_at TIMESTAMP WITH TIME ZONE,
    end_reason TEXT,
    
    UNIQUE(patient_id, therapist_id, active)
);

-- Sessions table
CREATE TABLE sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    patient_id UUID REFERENCES patients(id) ON DELETE CASCADE,
    therapist_id UUID REFERENCES therapists(id) ON DELETE CASCADE,
    assignment_id UUID REFERENCES assignments(id) ON DELETE CASCADE,
    
    -- Session details
    scheduled_at TIMESTAMP WITH TIME ZONE NOT NULL,
    duration_minutes INTEGER DEFAULT 50,
    session_type VARCHAR(50), -- initial, followup, crisis
    session_format VARCHAR(50), -- in-person, telehealth
    
    -- Status
    status session_status DEFAULT 'scheduled',
    completed_at TIMESTAMP WITH TIME ZONE,
    cancelled_at TIMESTAMP WITH TIME ZONE,
    cancellation_reason TEXT,
    
    -- Clinical notes
    therapist_notes TEXT,
    patient_mood_rating INTEGER CHECK (patient_mood_rating BETWEEN 1 AND 10),
    progress_notes TEXT,
    
    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes separately
CREATE INDEX idx_patient_sessions ON sessions(patient_id, scheduled_at);
CREATE INDEX idx_therapist_sessions ON sessions(therapist_id, scheduled_at);

-- Dropout predictions table
CREATE TABLE dropout_predictions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    patient_id UUID REFERENCES patients(id) ON DELETE CASCADE,
    
    -- Prediction
    dropout_probability DECIMAL(5,2) NOT NULL CHECK (dropout_probability BETWEEN 0 AND 100),
    risk_factors TEXT[], -- Contributing factors
    
    -- Features used
    sessions_attended INTEGER DEFAULT 0,
    sessions_cancelled INTEGER DEFAULT 0,
    sessions_no_show INTEGER DEFAULT 0,
    avg_response_time_hours DECIMAL(10,2),
    sentiment_trend DECIMAL(5,2), -- Trend over time
    days_since_last_session INTEGER,
    
    -- Model metadata
    model_version VARCHAR(50),
    predicted_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- Intervention tracking
    intervention_recommended BOOLEAN DEFAULT false,
    intervention_taken BOOLEAN DEFAULT false,
    intervention_notes TEXT
);
-- Create indexes separately
CREATE INDEX idx_high_dropout ON dropout_predictions(dropout_probability DESC);

-- Alerts table
CREATE TABLE alerts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    patient_id UUID REFERENCES patients(id) ON DELETE CASCADE,
    
    -- Alert details
    alert_type VARCHAR(50) NOT NULL, -- crisis_keyword, high_risk, dropout_risk, no_show
    severity VARCHAR(20) NOT NULL, -- low, medium, high, critical
    title VARCHAR(255) NOT NULL,
    description TEXT,
    
    -- Related entities
    risk_assessment_id UUID REFERENCES risk_assessments(id),
    dropout_prediction_id UUID REFERENCES dropout_predictions(id),
    
    -- Status
    acknowledged BOOLEAN DEFAULT false,
    acknowledged_by VARCHAR(100),
    acknowledged_at TIMESTAMP WITH TIME ZONE,
    resolved BOOLEAN DEFAULT false,
    resolved_at TIMESTAMP WITH TIME ZONE,
    resolution_notes TEXT,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
-- Create indexes separately
CREATE INDEX idx_active_alerts ON alerts(acknowledged, resolved, created_at);

-- Audit log for compliance
CREATE TABLE audit_log (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_email VARCHAR(255) NOT NULL,
    user_role VARCHAR(50) NOT NULL,
    action VARCHAR(100) NOT NULL,
    resource_type VARCHAR(50),
    resource_id UUID,
    details JSONB,
    ip_address INET,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
-- Create indexes separately
CREATE INDEX idx_audit_user ON audit_log(user_email, created_at);
CREATE INDEX idx_audit_resource ON audit_log(resource_type, resource_id);

-- Update timestamp trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply update triggers
CREATE TRIGGER update_patients_updated_at BEFORE UPDATE ON patients
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_therapists_updated_at BEFORE UPDATE ON therapists
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Sample data for testing
INSERT INTO therapists (first_name, last_name, email, phone, license_number, license_state, specialties, languages, years_experience, bio, accepts_high_risk) VALUES
('Sarah', 'Johnson', 'sjohnson@mindcare.com', '555-0101', 'PSY-12345-CA', 'CA', ARRAY['trauma', 'anxiety']::therapist_specialty[], ARRAY['English', 'Spanish'], 8, 'Specializing in trauma-informed care and EMDR therapy.', true),
('Michael', 'Chen', 'mchen@mindcare.com', '555-0102', 'LCSW-67890-CA', 'CA', ARRAY['depression', 'anxiety']::therapist_specialty[], ARRAY['English', 'Mandarin'], 5, 'CBT and mindfulness-based approaches to depression and anxiety.', true),
('Emily', 'Rodriguez', 'erodriguez@mindcare.com', '555-0103', 'MFT-11111-CA', 'CA', ARRAY['couples', 'family']::therapist_specialty[], ARRAY['English', 'Spanish'], 12, 'Family systems therapy and relationship counseling.', false),
('David', 'Thompson', 'dthompson@mindcare.com', '555-0104', 'PSY-22222-CA', 'CA', ARRAY['addiction', 'trauma']::therapist_specialty[], ARRAY['English'], 15, 'Substance abuse treatment and dual diagnosis.', true),
('Jessica', 'Kim', 'jkim@mindcare.com', '555-0105', 'LMFT-33333-CA', 'CA', ARRAY['child', 'anxiety']::therapist_specialty[], ARRAY['English', 'Korean'], 6, 'Play therapy and child anxiety treatment.', false);

-- Create views for common queries
CREATE VIEW high_risk_patients AS
SELECT 
    p.id,
    p.first_name,
    p.last_name,
    p.email,
    ra.overall_risk_score,
    ra.risk_level,
    ra.assessed_at,
    ra.crisis_keywords_detected,
    a.active as has_assignment
FROM patients p
JOIN risk_assessments ra ON p.id = ra.patient_id
LEFT JOIN assignments a ON p.id = a.patient_id AND a.active = true
WHERE ra.risk_level IN ('high', 'critical')
ORDER BY ra.overall_risk_score DESC;

CREATE VIEW therapist_caseloads AS
SELECT 
    t.id,
    t.first_name,
    t.last_name,
    t.specialties,
    t.max_caseload,
    t.current_caseload,
    COUNT(DISTINCT a.patient_id) as active_patients,
    (t.max_caseload - t.current_caseload) as capacity_remaining,
    ROUND((t.current_caseload::DECIMAL / t.max_caseload * 100), 2) as utilization_percent
FROM therapists t
LEFT JOIN assignments a ON t.id = a.therapist_id AND a.active = true
WHERE t.active = true
GROUP BY t.id, t.first_name, t.last_name, t.specialties, t.max_caseload, t.current_caseload;

-- Grant permissions (adjust for your setup)
-- GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO mindcare_app;
-- GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO mindcare_app;
