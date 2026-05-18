'use client'

import posthog from 'posthog-js'
import { PostHogProvider } from 'posthog-js/react'
import { useEffect } from 'react'

export function PHProvider({ children }: { children: React.ReactNode }) {
  useEffect(() => {
    const key = process.env.NEXT_PUBLIC_POSTHOG_KEY
    const host = process.env.NEXT_PUBLIC_POSTHOG_HOST || 'https://us.i.posthog.com'
    const enabled = process.env.NEXT_PUBLIC_ANALYTICS_ENABLED === 'true'

    if (!enabled || !key) {
      return
    }

    posthog.init(key, {
      api_host: host,
      person_profiles: 'identified_only',
      capture_pageview: false,
      disable_session_recording: true, // Prevent rrweb conflicts with Next.js
      autocapture: false, // Prevent DOM injection issues
    })
  }, [])

  return <PostHogProvider client={posthog}>{children}</PostHogProvider>
}
