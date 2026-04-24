#!/bin/bash
# Setup PostHog environment variables in Railway

echo "Setting up PostHog in Railway..."
echo ""

# Set PostHog API Key
railway variables set POSTHOG_API_KEY="phc_z6Ac8mrQU72kWKdxkqHqykHWWCbrUbJJywFD42kKmdwV"

# Set PostHog Host
railway variables set POSTHOG_HOST="https://app.posthog.com"

# Set debug to false for production
railway variables set POSTHOG_DEBUG="false"

echo ""
echo "✅ PostHog environment variables set in Railway"
echo ""
echo "Next steps:"
echo "1. Deploy: railway up"
echo "2. Check logs: railway logs"
echo "3. Verify in PostHog dashboard"
