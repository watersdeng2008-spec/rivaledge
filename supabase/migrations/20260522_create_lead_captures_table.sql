-- Migration: Create lead_captures table for website lead capture
-- Created: 2026-05-22

CREATE TABLE IF NOT EXISTS lead_captures (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Contact info
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    
    -- Company info
    company_name VARCHAR(255),
    company_url TEXT,
    
    -- Competitor info
    competitor_url TEXT,
    
    -- Source tracking
    capture_source VARCHAR(50) NOT NULL, -- 'homepage', 'pricing', 'exit_intent', 'demo'
    
    -- UTM / attribution
    utm_source VARCHAR(100),
    utm_medium VARCHAR(100),
    utm_campaign VARCHAR(100),
    
    -- Status
    email_sent BOOLEAN DEFAULT false,
    email_sent_at TIMESTAMP,
    
    -- Engagement
    viewed_demo BOOLEAN DEFAULT false,
    signed_up BOOLEAN DEFAULT false,
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Indexes for common queries
CREATE INDEX idx_lead_captures_email ON lead_captures(email);
CREATE INDEX idx_lead_captures_source ON lead_captures(capture_source);
CREATE INDEX idx_lead_captures_created_at ON lead_captures(created_at DESC);
CREATE INDEX idx_lead_captures_email_sent ON lead_captures(email_sent);

-- Trigger to update updated_at
CREATE OR REPLACE FUNCTION update_lead_captures_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

DROP TRIGGER IF EXISTS update_lead_captures_updated_at ON lead_captures;
CREATE TRIGGER update_lead_captures_updated_at 
    BEFORE UPDATE ON lead_captures 
    FOR EACH ROW 
    EXECUTE FUNCTION update_lead_captures_updated_at();

-- Comments for documentation
COMMENT ON TABLE lead_captures IS 'Website lead captures from interactive forms';
COMMENT ON COLUMN lead_captures.capture_source IS 'Where the lead was captured: homepage, pricing, exit_intent, demo';
COMMENT ON COLUMN lead_captures.email_sent IS 'Whether welcome email was sent';
