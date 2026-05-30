'use client';

import { SignUp } from '@clerk/nextjs';
import { useEffect } from 'react';
import posthog from 'posthog-js';

export default function SignUpPage() {
  useEffect(() => {
    posthog.capture('sign_up_page_viewed');
  }, []);

  return (
    <div className="min-h-screen bg-slate-950 flex items-center justify-center">
      <SignUp
        forceRedirectUrl="/dashboard"
      />
    </div>
  );
}
