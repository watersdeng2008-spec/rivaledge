-- Migration: Create leads table for sales agent
-- Created: 2026-04-05

CREATE TABLE IF NOT EXISTS leads (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Contact info
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255),
    title VARCHAR(255),
    
    -- Company info
    company VARCHAR(255),
    company_size VARCHAR(50), -- '1-10', '11-50', '51-200', '201-500', '500+'
    industry VARCHAR(100),
    company_website VARCHAR(500),
    
    -- Social/Research
    linkedin_url TEXT,
    twitter_handle VARCHAR(100),
    
    -- Lead scoring
    priority_score INTEGER DEFAULT 0, -- 0-100
    pain_signals JSONB DEFAULT '[]', -- Array of detected pain points
    
    -- Source tracking
    source VARCHAR(50) NOT NULL, -- 'linkedin', 'apollo', 'manual', 'referral'
    source_details JSONB DEFAULT '{}', -- Platform-specific data
    
    -- Status workflow
    status VARCHAR(50) DEFAULT 'new', -- 'new', 'enriched', 'personalized', 'contacted', 'replied', 'qualified', 'disqualified', 'converted'
    
    -- Engagement tracking
    emails_sent INTEGER DEFAULT 0,
    emails_opened INTEGER DEFAULT 0,
    emails_clicked INTEGER DEFAULT 0,
    last_contacted_at TIMESTAMP,
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Indexes for common queries
CREATE INDEX idx_leads_email ON leads(email);
CREATE INDEX idx_leads_status ON leads(status);
CREATE INDEX idx_leads_company ON leads(company);
CREATE INDEX idx_leads_source ON leads(source);
CREATE INDEX idx_leads_priority_score ON leads(priority_score DESC);
CREATE INDEX idx_leads_created_at ON leads(created_at DESC);
CREATE INDEX idx_leads_status_score ON leads(status, priority_score DESC);

-- Trigger to update updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_leads_updated_at 
    BEFORE UPDATE ON leads 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

-- Comments for documentation
COMMENT ON TABLE leads IS 'Sales leads for RivalEdge outreach';
COMMENT ON COLUMN leads.priority_score IS '0-100 score based on ICP fit';
COMMENT ON COLUMN leads.pain_signals IS 'JSON array of detected pain points (e.g., ["pricing_change", "new_competitor"])';
COMMENT ON COLUMN leads.status IS 'Lead lifecycle status';
