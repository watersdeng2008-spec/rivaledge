-- Sales Agent Tracking Schema
-- Run this in Supabase SQL Editor

-- Track sales agent runs
CREATE TABLE IF NOT EXISTS sales_agent_logs (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    run_id TEXT NOT NULL,
    started_at TIMESTAMPTZ NOT NULL,
    completed_at TIMESTAMPTZ,
    target_count INTEGER DEFAULT 0,
    companies_processed INTEGER DEFAULT 0,
    decision_makers_found INTEGER DEFAULT 0,
    emails_generated INTEGER DEFAULT 0,
    emails_added_to_instantly INTEGER DEFAULT 0,
    errors JSONB DEFAULT '[]'::jsonb,
    details JSONB DEFAULT '[]'::jsonb,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Track lead performance (for conversion analysis)
CREATE TABLE IF NOT EXISTS sales_leads (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    run_id TEXT,
    domain TEXT NOT NULL,
    industry TEXT,
    company_name TEXT,
    decision_maker_name TEXT,
    decision_maker_title TEXT,
    email TEXT,
    email_subject TEXT,
    email_body TEXT,
    template_used TEXT,
    added_to_instantly BOOLEAN DEFAULT FALSE,
    instantly_lead_id TEXT,
    status TEXT DEFAULT 'new', -- new, sent, replied, bounced, unsubscribed
    reply_received_at TIMESTAMPTZ,
    reply_content TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Track performance by industry/template (for optimization)
CREATE TABLE IF NOT EXISTS sales_performance (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    industry TEXT NOT NULL,
    template_used TEXT NOT NULL,
    total_sent INTEGER DEFAULT 0,
    total_replies INTEGER DEFAULT 0,
    reply_rate DECIMAL(5,2) DEFAULT 0,
    positive_replies INTEGER DEFAULT 0,
    meetings_booked INTEGER DEFAULT 0,
    last_updated TIMESTAMPTZ DEFAULT NOW()
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_sales_agent_logs_run_id ON sales_agent_logs(run_id);
CREATE INDEX IF NOT EXISTS idx_sales_leads_domain ON sales_leads(domain);
CREATE INDEX IF NOT EXISTS idx_sales_leads_status ON sales_leads(status);
CREATE INDEX IF NOT EXISTS idx_sales_leads_industry ON sales_leads(industry);
CREATE INDEX IF NOT EXISTS idx_sales_performance_industry ON sales_performance(industry);

-- Enable RLS (admin only)
ALTER TABLE sales_agent_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE sales_leads ENABLE ROW LEVEL SECURITY;
ALTER TABLE sales_performance ENABLE ROW LEVEL SECURITY;

-- Create policies (admin only)
CREATE POLICY "Admin full access" ON sales_agent_logs
    FOR ALL USING (auth.uid() IN (
        SELECT id FROM users WHERE plan = 'admin'
    ));

CREATE POLICY "Admin full access" ON sales_leads
    FOR ALL USING (auth.uid() IN (
        SELECT id FROM users WHERE plan = 'admin'
    ));

CREATE POLICY "Admin full access" ON sales_performance
    FOR ALL USING (auth.uid() IN (
        SELECT id FROM users WHERE plan = 'admin'
    ));
