'use client'

import posthog from 'posthog-js'
import { PostHogProvider } from 'posthog-js/react'
import { useEffect } from 'react'

export function PHProvider({ children }: { children: React.ReactNode }) {
  useEffect(() => {
    posthog.init('phc_z6Ac8mrQU72kWKdxkqHqykHWWCbrUbJJywFD42kKmdwV', {
      api_host: 'https://us.i.posthog.com',
      person_profiles: 'identified_only',
      capture_pageview: false, // handled by PostHogPageView
    })
  }, [])

  return <PostHogProvider client={posthog}>{children}</PostHogProvider>
}
