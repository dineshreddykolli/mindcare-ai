-- Authentication Tables Migration
-- Add user authentication and session management

-- User roles enum
CREATE TYPE user_role AS ENUM ('admin', 'therapist', 'staff', 'patient');

-- Users table
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    role user_role NOT NULL DEFAULT 'staff',
    
    -- Account status
    is_active BOOLEAN DEFAULT true,
    is_verified BOOLEAN DEFAULT false,
    email_verified_at TIMESTAMP WITH TIME ZONE,
    
    -- Security
    failed_login_attempts INTEGER DEFAULT 0,
    last_login TIMESTAMP WITH TIME ZONE,
    password_changed_at TIMESTAMP WITH TIME ZONE,
    
    -- Multi-factor authentication
    mfa_enabled BOOLEAN DEFAULT false,
    mfa_secret VARCHAR(32),
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_email (email),
    INDEX idx_role (role),
    INDEX idx_active (is_active)
);

-- Refresh tokens table
CREATE TABLE refresh_tokens (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL,
    token VARCHAR(255) UNIQUE NOT NULL,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    revoked BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_token (token),
    INDEX idx_user_id (user_id),
    INDEX idx_expires_at (expires_at)
);

-- Link existing patients to users (if needed)
ALTER TABLE patients ADD COLUMN user_id UUID REFERENCES users(id);

-- Link existing therapists to users
ALTER TABLE therapists ADD COLUMN user_id UUID REFERENCES users(id);

-- Create default admin user (password: admin123)
-- Hash generated with bcrypt
INSERT INTO users (email, hashed_password, first_name, last_name, role, is_active, is_verified) VALUES
('admin@mindcare.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5yvJMz8oIhZRq', 'Admin', 'User', 'admin', true, true),
('therapist@mindcare.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5yvJMz8oIhZRq', 'Test', 'Therapist', 'therapist', true, true),
('staff@mindcare.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5yvJMz8oIhZRq', 'Staff', 'Member', 'staff', true, true);

-- Update trigger for users table
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- View for user activity
CREATE VIEW user_activity AS
SELECT 
    u.id,
    u.email,
    u.first_name,
    u.last_name,
    u.role,
    u.is_active,
    u.last_login,
    u.failed_login_attempts,
    COUNT(DISTINCT rt.id) as active_sessions
FROM users u
LEFT JOIN refresh_tokens rt ON u.id = rt.user_id 
    AND rt.revoked = false 
    AND rt.expires_at > CURRENT_TIMESTAMP
GROUP BY u.id, u.email, u.first_name, u.last_name, u.role, u.is_active, u.last_login, u.failed_login_attempts;

-- Audit log entries for authentication
CREATE TABLE auth_audit_log (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id),
    event_type VARCHAR(50) NOT NULL, -- login, logout, failed_login, password_change, etc.
    ip_address INET,
    user_agent TEXT,
    success BOOLEAN NOT NULL,
    failure_reason TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_user_id (user_id),
    INDEX idx_event_type (event_type),
    INDEX idx_created_at (created_at)
);

-- Clean up expired refresh tokens (run periodically)
CREATE OR REPLACE FUNCTION cleanup_expired_tokens()
RETURNS void AS $$
BEGIN
    DELETE FROM refresh_tokens 
    WHERE expires_at < CURRENT_TIMESTAMP - INTERVAL '7 days';
END;
$$ LANGUAGE plpgsql;

-- Comments for documentation
COMMENT ON TABLE users IS 'User accounts for authentication and authorization';
COMMENT ON TABLE refresh_tokens IS 'JWT refresh tokens for session management';
COMMENT ON TABLE auth_audit_log IS 'Security audit log for authentication events';
COMMENT ON COLUMN users.mfa_secret IS 'TOTP secret key for two-factor authentication';
COMMENT ON COLUMN users.failed_login_attempts IS 'Counter for failed login attempts (locks account after 5)';
