export default function PrivacyPage() {
  return (
    <div className="min-h-screen bg-slate-950 text-white">
      <div className="max-w-3xl mx-auto px-6 py-16">
        <h1 className="text-4xl font-bold mb-4">Privacy Policy</h1>
        <p className="text-slate-400 mb-8">Last updated: April 1, 2026</p>

        <div className="prose prose-invert max-w-none space-y-8">
          <section>
            <h2 className="text-2xl font-semibold mb-3">Overview</h2>
            <p className="text-slate-300">RivalEdge (&quot;we&quot;, &quot;our&quot;, &quot;us&quot;) is operated by Aether Holding LLC. This Privacy Policy explains how we collect, use, and protect your information when you use rivaledge.ai.</p>
          </section>

          <section>
            <h2 className="text-2xl font-semibold mb-3">Information We Collect</h2>
            <ul className="text-slate-300 space-y-2 list-disc list-inside">
              <li><strong>Account information:</strong> Email address and name when you sign up</li>
              <li><strong>Usage data:</strong> Competitor URLs you add, features you use, and session activity</li>
              <li><strong>Payment information:</strong> Processed securely by Stripe — we do not store card details</li>
              <li><strong>Communications:</strong> Messages you send to our support team</li>
            </ul>
          </section>

          <section>
            <h2 className="text-2xl font-semibold mb-3">How We Use Your Information</h2>
            <ul className="text-slate-300 space-y-2 list-disc list-inside">
              <li>To provide and improve the RivalEdge service</li>
              <li>To send weekly competitor intelligence digests to your email</li>
              <li>To process payments and manage your subscription</li>
              <li>To respond to support requests</li>
              <li>To send product updates (you can unsubscribe at any time)</li>
            </ul>
          </section>

          <section>
            <h2 className="text-2xl font-semibold mb-3">Data We Monitor</h2>
            <p className="text-slate-300">RivalEdge monitors publicly available information on competitor websites you specify, including pricing pages, product listings, and marketing copy. We do not access private data, bypass authentication, or collect personal information about third parties.</p>
          </section>

          <section>
            <h2 className="text-2xl font-semibold mb-3">Data Sharing</h2>
            <p className="text-slate-300">We do not sell your personal information. We share data only with:</p>
            <ul className="text-slate-300 space-y-2 list-disc list-inside mt-2">
              <li><strong>Stripe</strong> — for payment processing</li>
              <li><strong>Supabase</strong> — for secure data storage</li>
              <li><strong>Resend</strong> — for email delivery</li>
              <li>Legal authorities when required by law</li>
            </ul>
          </section>

          <section>
            <h2 className="text-2xl font-semibold mb-3">Data Retention</h2>
            <p className="text-slate-300">We retain your account data for as long as your account is active. You may request deletion of your account and data at any time by emailing support@rivaledge.ai.</p>
          </section>

          <section>
            <h2 className="text-2xl font-semibold mb-3">Security</h2>
            <p className="text-slate-300">We use industry-standard security measures including encrypted connections (HTTPS), secure authentication via Clerk, and encrypted database storage. We never store payment card details.</p>
          </section>

          <section>
            <h2 className="text-2xl font-semibold mb-3">Your Rights</h2>
            <ul className="text-slate-300 space-y-2 list-disc list-inside">
              <li>Access or export your data at any time</li>
              <li>Request correction of inaccurate data</li>
              <li>Request deletion of your account and data</li>
              <li>Opt out of marketing emails</li>
            </ul>
          </section>

          <section>
            <h2 className="text-2xl font-semibold mb-3">Contact</h2>
            <p className="text-slate-300">For privacy questions or requests, contact us at: <a href="mailto:support@rivaledge.ai" className="text-blue-400 hover:underline">support@rivaledge.ai</a></p>
            <p className="text-slate-300 mt-2">Aether Holding LLC · Buffalo Grove, IL 60089</p>
          </section>
        </div>
      </div>
    </div>
  );
}
