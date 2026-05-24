-- Migration: Competitive Positioning Features
-- Date: 2026-05-24

CREATE TABLE IF NOT EXISTS ai_recommendation_share (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    brand_name TEXT NOT NULL,
    category TEXT NOT NULL,
    ars_score DECIMAL(5,2) NOT NULL,
    total_queries INT NOT NULL,
    brand_mentions INT NOT NULL,
    competitor_scores JSONB DEFAULT '{}',
    query_breakdown JSONB DEFAULT '[]',
    calculated_at TIMESTAMPTZ DEFAULT NOW(),
    period TEXT DEFAULT 'weekly',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_ars_user_brand ON ai_recommendation_share(user_id, brand_name);
CREATE INDEX IF NOT EXISTS idx_ars_calculated_at ON ai_recommendation_share(calculated_at DESC);

CREATE TABLE IF NOT EXISTS slack_configs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    workspace_id TEXT NOT NULL,
    channel_id TEXT NOT NULL,
    channel_name TEXT NOT NULL,
    alert_types TEXT[] DEFAULT ARRAY['competitor_move', 'ars_change'],
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(user_id)
);

CREATE INDEX IF NOT EXISTS idx_slack_user ON slack_configs(user_id);

CREATE TABLE IF NOT EXISTS newsletter_subscribers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email TEXT NOT NULL UNIQUE,
    source TEXT DEFAULT 'website',
    is_active BOOLEAN DEFAULT TRUE,
    subscribed_at TIMESTAMPTZ DEFAULT NOW(),
    unsubscribed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_newsletter_active ON newsletter_subscribers(is_active);

CREATE TABLE IF NOT EXISTS newsletter_archive (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    week_number INT NOT NULL,
    vertical TEXT NOT NULL,
    topic TEXT NOT NULL,
    content TEXT NOT NULL,
    html TEXT NOT NULL,
    generated_at TIMESTAMPTZ DEFAULT NOW(),
    sent_at TIMESTAMPTZ,
    subscriber_count INT DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_newsletter_week ON newsletter_archive(week_number);

CREATE TABLE IF NOT EXISTS partners (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id TEXT REFERENCES users(id) ON DELETE SET NULL,
    company_name TEXT NOT NULL,
    website TEXT,
    team_size INT,
    current_clients INT DEFAULT 0,
    target_verticals TEXT[] DEFAULT '{}',
    expected_client_volume INT,
    contact_name TEXT,
    contact_email TEXT,
    tier TEXT NOT NULL DEFAULT 'referral',
    status TEXT NOT NULL DEFAULT 'pending',
    revenue_share_percent INT DEFAULT 20,
    wholesale_discount INT DEFAULT 0,
    custom_domain TEXT,
    brand_color TEXT,
    logo_url TEXT,
    custom_pricing JSONB DEFAULT '{}',
    is_active BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_partners_status ON partners(status);
CREATE INDEX IF NOT EXISTS idx_partners_tier ON partners(tier);

CREATE TABLE IF NOT EXISTS partner_clients (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    partner_id UUID NOT NULL REFERENCES partners(id) ON DELETE CASCADE,
    user_id TEXT REFERENCES users(id) ON DELETE SET NULL,
    client_name TEXT NOT NULL,
    client_email TEXT,
    plan TEXT DEFAULT 'pro',
    monthly_revenue DECIMAL(10,2) DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_partner_clients_partner ON partner_clients(partner_id);

CREATE TABLE IF NOT EXISTS audit_leads (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email TEXT,
    brand_name TEXT NOT NULL,
    category TEXT NOT NULL,
    competitors TEXT[] DEFAULT '{}',
    ars_score DECIMAL(5,2),
    source TEXT DEFAULT 'free_audit',
    converted_to_trial BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_audit_leads_email ON audit_leads(email);
CREATE INDEX IF NOT EXISTS idx_audit_leads_created ON audit_leads(created_at DESC);

ALTER TABLE ai_recommendation_share ENABLE ROW LEVEL SECURITY;
ALTER TABLE slack_configs ENABLE ROW LEVEL SECURITY;
ALTER TABLE newsletter_subscribers ENABLE ROW LEVEL SECURITY;
ALTER TABLE newsletter_archive ENABLE ROW LEVEL SECURITY;
ALTER TABLE partners ENABLE ROW LEVEL SECURITY;
ALTER TABLE partner_clients ENABLE ROW LEVEL SECURITY;
ALTER TABLE audit_leads ENABLE ROW LEVEL SECURITY;

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE schemaname = 'public' AND tablename = 'ai_recommendation_share' AND policyname = 'Users can view own ARS') THEN
        CREATE POLICY "Users can view own ARS" ON ai_recommendation_share
            FOR ALL USING (user_id = auth.uid()::text);
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE schemaname = 'public' AND tablename = 'slack_configs' AND policyname = 'Users can view own slack config') THEN
        CREATE POLICY "Users can view own slack config" ON slack_configs
            FOR ALL USING (user_id = auth.uid()::text);
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE schemaname = 'public' AND tablename = 'newsletter_subscribers' AND policyname = 'Admins can manage newsletter') THEN
        CREATE POLICY "Admins can manage newsletter" ON newsletter_subscribers
            FOR ALL USING (auth.uid()::text IN (SELECT id FROM users WHERE plan = 'enterprise'));
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE schemaname = 'public' AND tablename = 'newsletter_subscribers' AND policyname = 'Public can subscribe') THEN
        CREATE POLICY "Public can subscribe" ON newsletter_subscribers
            FOR INSERT WITH CHECK (true);
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE schemaname = 'public' AND tablename = 'partners' AND policyname = 'Partners can view own data') THEN
        CREATE POLICY "Partners can view own data" ON partners
            FOR ALL USING (user_id = auth.uid()::text);
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE schemaname = 'public' AND tablename = 'partner_clients' AND policyname = 'Partners can view own clients') THEN
        CREATE POLICY "Partners can view own clients" ON partner_clients
            FOR ALL USING (
                EXISTS (
                    SELECT 1
                    FROM partners
                    WHERE partners.id = partner_clients.partner_id
                    AND partners.user_id = auth.uid()::text
                )
            );
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE schemaname = 'public' AND tablename = 'audit_leads' AND policyname = 'Admins can view audit leads') THEN
        CREATE POLICY "Admins can view audit leads" ON audit_leads
            FOR ALL USING (auth.uid()::text IN (SELECT id FROM users WHERE plan = 'enterprise'));
    END IF;
END
$$;

SELECT 'Migration complete: Competitive positioning features' AS status;
