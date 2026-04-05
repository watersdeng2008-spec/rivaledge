-- Migration: Create personalized_emails table
-- Created: 2026-04-05

CREATE TABLE IF NOT EXISTS personalized_emails (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Relationship
    lead_id UUID NOT NULL REFERENCES leads(id) ON DELETE CASCADE,
    
    -- Email content
    template_used VARCHAR(50) NOT NULL, -- 'competitor_angle', 'pricing_angle', etc.
    subject TEXT NOT NULL,
    body TEXT NOT NULL,
    
    -- Personalization tracking
    personalization_score INTEGER, -- 1-10 quality score
    personalization_notes JSONB DEFAULT '{}', -- What was personalized
    
    -- Status workflow
    status VARCHAR(50) DEFAULT 'draft', -- 'draft', 'approved', 'sent', 'paused', 'rejected'
    
    -- Review tracking
    reviewed_by VARCHAR(255), -- Who approved/rejected
    reviewed_at TIMESTAMP,
    review_notes TEXT,
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_personalized_emails_lead ON personalized_emails(lead_id);
CREATE INDEX idx_personalized_emails_status ON personalized_emails(status);
CREATE INDEX idx_personalized_emails_template ON personalized_emails(template_used);

-- Trigger for updated_at
CREATE TRIGGER update_personalized_emails_updated_at 
    BEFORE UPDATE ON personalized_emails 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

-- Comments
COMMENT ON TABLE personalized_emails IS 'AI-personalized email drafts for sales outreach';
COMMENT ON COLUMN personalized_emails.personalization_score IS 'AI-assigned quality score 1-10';
COMMENT ON COLUMN personalized_emails.status IS 'Approval workflow status';
