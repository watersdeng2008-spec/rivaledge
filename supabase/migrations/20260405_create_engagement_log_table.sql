-- Migration: Create engagement_log table
-- Created: 2026-04-05

CREATE TABLE IF NOT EXISTS engagement_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Relationship
    lead_id UUID NOT NULL REFERENCES leads(id) ON DELETE CASCADE,
    sequence_email_id UUID REFERENCES email_sequences(id) ON DELETE SET NULL,
    
    -- Event details
    action VARCHAR(50) NOT NULL, -- 'open', 'click', 'reply', 'bounce', 'unsubscribe', 'forward'
    
    -- Context
    metadata JSONB DEFAULT '{}', -- Flexible context data
    -- Examples:
    -- { "link_clicked": "pricing", "ip_address": "1.2.3.4", "user_agent": "..." }
    -- { "reply_snippet": "Thanks for reaching out...", "sentiment": "positive" }
    -- { "bounce_reason": "mailbox_full", "bounce_code": "4.2.2" }
    
    -- Source tracking
    source VARCHAR(50), -- 'instantly_webhook', 'resend_webhook', 'manual', 'api'
    
    -- Timestamps
    occurred_at TIMESTAMP NOT NULL, -- When the event actually happened
    recorded_at TIMESTAMP DEFAULT NOW(), -- When we logged it
    
    -- Raw data (for debugging)
    raw_payload JSONB -- Original webhook payload if applicable
);

-- Indexes
CREATE INDEX idx_engagement_log_lead ON engagement_log(lead_id);
CREATE INDEX idx_engagement_log_action ON engagement_log(action);
CREATE INDEX idx_engagement_log_occurred ON engagement_log(occurred_at);
CREATE INDEX idx_engagement_log_recorded ON engagement_log(recorded_at DESC);

-- Comments
COMMENT ON TABLE engagement_log IS 'Audit log of all lead engagement events';
COMMENT ON COLUMN engagement_log.action IS 'Type of engagement event';
COMMENT ON COLUMN engagement_log.metadata IS 'Flexible JSON context for the event';
