-- Migration: Create email_sequences table
-- Created: 2026-04-05

CREATE TABLE IF NOT EXISTS email_sequences (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Relationship
    lead_id UUID NOT NULL REFERENCES leads(id) ON DELETE CASCADE,
    
    -- Sequence info
    sequence_name VARCHAR(100) DEFAULT 'default', -- 'default', 'aggressive', 'nurture'
    email_number INTEGER NOT NULL, -- 1, 2, 3, 4 (which email in sequence)
    
    -- Email content
    subject TEXT NOT NULL,
    body TEXT NOT NULL,
    
    -- Scheduling
    scheduled_at TIMESTAMP NOT NULL,
    sent_at TIMESTAMP,
    
    -- Engagement tracking
    delivered_at TIMESTAMP,
    opened_at TIMESTAMP,
    clicked_at TIMESTAMP,
    replied_at TIMESTAMP,
    bounced_at TIMESTAMP,
    
    -- Engagement counts
    open_count INTEGER DEFAULT 0,
    click_count INTEGER DEFAULT 0,
    
    -- Status
    status VARCHAR(50) DEFAULT 'scheduled', -- 'scheduled', 'sending', 'sent', 'delivered', 'bounced', 'failed', 'paused'
    error_message TEXT,
    
    -- External IDs (from email provider)
    external_message_id VARCHAR(255), -- Instantly/Resend message ID
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_email_sequences_lead ON email_sequences(lead_id);
CREATE INDEX idx_email_sequences_status ON email_sequences(status);
CREATE INDEX idx_email_sequences_scheduled ON email_sequences(scheduled_at);
CREATE INDEX idx_email_sequences_sent ON email_sequences(sent_at);

-- Trigger for updated_at
CREATE TRIGGER update_email_sequences_updated_at 
    BEFORE UPDATE ON email_sequences 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

-- Comments
COMMENT ON TABLE email_sequences IS 'Email sequence tracking for sales outreach';
COMMENT ON COLUMN email_sequences.email_number IS 'Position in sequence (1=initial, 2=follow-up 1, etc.)';
COMMENT ON COLUMN email_sequences.external_message_id IS 'Message ID from email service provider';
