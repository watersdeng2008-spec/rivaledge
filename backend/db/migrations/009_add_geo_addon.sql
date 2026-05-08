-- Migration: Add GEO add-on tracking to users table
ALTER TABLE users ADD COLUMN IF NOT EXISTS has_geo_addon boolean default false;
