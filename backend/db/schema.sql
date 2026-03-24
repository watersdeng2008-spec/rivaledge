-- RivalEdge Supabase Schema
-- Run this in Supabase SQL Editor

-- Users (synced from Clerk via webhook)
create table if not exists users (
  id text primary key,            -- Clerk user ID
  email text not null,
  plan text default 'solo',       -- 'solo' | 'pro'
  stripe_customer_id text,        -- Stripe customer ID (set on first checkout)
  created_at timestamptz default now()
);

-- Competitors tracked per user
create table if not exists competitors (
  id uuid primary key default gen_random_uuid(),
  user_id text references users(id) on delete cascade,
  url text not null,
  name text,
  profile jsonb,                  -- scraped metadata: title, description, etc.
  created_at timestamptz default now()
);

-- Snapshots of competitor pages over time
create table if not exists snapshots (
  id uuid primary key default gen_random_uuid(),
  competitor_id uuid references competitors(id) on delete cascade,
  content jsonb not null,         -- full scraped content
  diff jsonb,                     -- diff from previous snapshot
  created_at timestamptz default now()
);

-- AI-generated digest emails
create table if not exists digests (
  id uuid primary key default gen_random_uuid(),
  user_id text references users(id) on delete cascade,
  content text not null,          -- markdown digest body
  sent_at timestamptz,
  created_at timestamptz default now()
);

-- Indexes for performance
create index if not exists competitors_user_id_idx on competitors(user_id);
create index if not exists snapshots_competitor_id_idx on snapshots(competitor_id);
create index if not exists snapshots_created_at_idx on snapshots(created_at desc);
create index if not exists digests_user_id_idx on digests(user_id);

-- Row Level Security (enable after testing)
-- alter table users enable row level security;
-- alter table competitors enable row level security;
-- alter table snapshots enable row level security;
-- alter table digests enable row level security;
