'use client';

import { useEffect } from 'react';
import posthog from 'posthog-js';

export default function PostHogPageLeave() {
  useEffect(() => {
    const handleBeforeUnload = () => {
      posthog.capture('$pageleave', {
        $current_url: window.location.href,
        $pathname: window.location.pathname,
      });
    };

    window.addEventListener('beforeunload', handleBeforeUnload);
    return () => window.removeEventListener('beforeunload', handleBeforeUnload);
  }, []);

  return null;
}
