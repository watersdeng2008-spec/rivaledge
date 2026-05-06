-- 008: Add unique constraint to competitors table (user_id, url)
-- Prevents duplicate competitor URLs per user.
-- Also prevents the plan-reset bug from creating phantom duplicates.

CREATE UNIQUE INDEX IF NOT EXISTS idx_competitors_user_url
  ON competitors (user_id, url);
