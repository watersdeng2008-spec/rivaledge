-- Migration: Add emails_sent table for tracking automated emails
-- Created: 2026-04-25

CREATE TABLE IF NOT EXISTS emails_sent (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    email_type VARCHAR(50) NOT NULL,  -- 'onboarding_followup', 'weekly_digest', etc.
    sent_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    subject VARCHAR(255),
    opened_at TIMESTAMP WITH TIME ZONE,
    clicked_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Index for efficient queries
CREATE INDEX IF NOT EXISTS idx_emails_sent_user_id ON emails_sent(user_id);
CREATE INDEX IF NOT EXISTS idx_emails_sent_type ON emails_sent(email_type);
CREATE INDEX IF NOT EXISTS idx_emails_sent_sent_at ON emails_sent(sent_at);

-- Add comment
COMMENT ON TABLE emails_sent IS 'Tracks automated emails sent to users for analytics and deduplication';
