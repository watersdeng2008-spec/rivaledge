'use client'

import posthog from 'posthog-js'
import { PostHogProvider as PHProvider, usePostHog } from 'posthog-js/react'
import { useEffect, useState } from 'react'
import { useAuth } from '@clerk/nextjs'

export function PostHogProvider({ children }: { children: React.ReactNode }) {
  const [isInitialized, setIsInitialized] = useState(false)

  useEffect(() => {
    if (typeof window !== 'undefined' && !isInitialized) {
      posthog.init(process.env.NEXT_PUBLIC_POSTHOG_KEY || '', {
        api_host: process.env.NEXT_PUBLIC_POSTHOG_HOST || 'https://us.i.posthog.com',
        person_profiles: 'identified_only',
        capture_pageview: true,
        capture_pageleave: true,
      })
      setIsInitialized(true)
    }
  }, [isInitialized])

  return (
    <PHProvider client={posthog}>
      <PostHogAuthWrapper>{children}</PostHogAuthWrapper>
    </PHProvider>
  )
}

function PostHogAuthWrapper({ children }: { children: React.ReactNode }) {
  const { userId, isSignedIn, user } = useAuth()
  const posthog = usePostHog()

  useEffect(() => {
    if (isSignedIn && userId && posthog) {
      posthog.identify(userId, {
        email: user?.primaryEmailAddress?.emailAddress,
        name: user?.fullName,
      })
    } else if (!isSignedIn && posthog) {
      posthog.reset()
    }
  }, [isSignedIn, userId, user, posthog])

  return <>{children}</>
}
