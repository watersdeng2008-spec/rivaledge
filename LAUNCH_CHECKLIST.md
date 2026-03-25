# RivalEdge Launch Checklist

## Pre-Launch (Complete before first user)
- [ ] Railway backend deployed and healthy (/health returns 200)
- [ ] Vercel frontend deployed (rivaledge.ai resolves)
- [ ] Supabase schema applied (all 4 tables created)
- [ ] Clerk webhook registered at /api/webhooks/clerk
- [ ] Stripe webhook registered at /api/billing/webhook
- [ ] Test signup flow end-to-end (sign up → add competitor → receive welcome email)
- [ ] Test checkout flow (Solo plan → Stripe → plan updates in dashboard)
- [ ] Test weekly digest (trigger manually via /api/digest/generate → send via /api/digest/send/{id})
- [ ] DNS: rivaledge.ai → Vercel (add CNAME in domain registrar)
- [ ] Resend: verify rivaledge.ai domain for email sending
- [ ] @RivalEdgeAI X account live with pinned tweet
- [ ] u/RivalEdgeAI Reddit account ready

## Launch Day
- [ ] Post Thread 1 on @RivalEdgeAI
- [ ] Post on r/indiehackers
- [ ] Post on r/SaaS
- [ ] DM 20 target users who complained about competitor tracking
- [ ] Monitor Railway logs for errors
- [ ] Monitor Supabase for new user signups

## Post-Launch (Week 1)
- [ ] First paid subscriber
- [ ] First weekly digest sent to real user
- [ ] Collect feedback from beta users
- [ ] Fix top 3 issues reported
