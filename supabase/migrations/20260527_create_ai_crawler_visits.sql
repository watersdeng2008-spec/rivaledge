-- Migration: Create AI crawler visit tracking
-- Created: 2026-05-27

CREATE TABLE IF NOT EXISTS ai_crawler_visits (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    crawler_name TEXT NOT NULL,
    crawler_company TEXT NOT NULL,
    crawler_pattern TEXT NOT NULL,
    page_url TEXT NOT NULL,
    ip_address TEXT,
    user_agent TEXT,
    visited_at TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_crawler_visits_name ON ai_crawler_visits(crawler_name);
CREATE INDEX IF NOT EXISTS idx_crawler_visits_url ON ai_crawler_visits(page_url);
CREATE INDEX IF NOT EXISTS idx_crawler_visits_date ON ai_crawler_visits(visited_at);
CREATE INDEX IF NOT EXISTS idx_crawler_visits_company ON ai_crawler_visits(crawler_company);

CREATE OR REPLACE VIEW ai_crawler_daily_summary AS
SELECT
    DATE(visited_at) AS date,
    crawler_name,
    crawler_company,
    COUNT(*) AS visit_count,
    COUNT(DISTINCT page_url) AS unique_pages
FROM ai_crawler_visits
GROUP BY DATE(visited_at), crawler_name, crawler_company
ORDER BY date DESC, visit_count DESC;

CREATE OR REPLACE VIEW ai_crawler_top_pages AS
SELECT
    page_url,
    COUNT(*) AS total_visits,
    COUNT(DISTINCT crawler_name) AS unique_crawlers,
    MAX(visited_at) AS last_visited
FROM ai_crawler_visits
GROUP BY page_url
ORDER BY total_visits DESC;

ALTER TABLE ai_crawler_visits ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Allow service role insert"
    ON ai_crawler_visits
    FOR INSERT
    TO service_role
    WITH CHECK (true);

CREATE POLICY "Allow service role read"
    ON ai_crawler_visits
    FOR SELECT
    TO service_role
    USING (true);
