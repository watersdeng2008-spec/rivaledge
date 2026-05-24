"use client";

import Link from "next/link";

export default function SocialAdminPage() {
  return (
    <div className="min-h-screen bg-slate-950 text-white">
      {/* Nav */}
      <nav className="border-b border-slate-800 px-6 py-4">
        <div className="max-w-6xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-4">
            <Link href="/dashboard" className="text-slate-400 hover:text-white">
              ← Back to Dashboard
            </Link>
          </div>
          <span className="text-xl font-bold text-blue-400">Social Media</span>
        </div>
      </nav>

      <div className="max-w-6xl mx-auto px-6 py-8">
        <h1 className="text-3xl font-bold mb-4">Social Media Posting</h1>
        
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 mb-6">
          <h2 className="text-xl font-semibold mb-4">Status</h2>
          <div className="flex items-center gap-2 mb-4">
            <span className="w-3 h-3 rounded-full bg-green-500"></span>
            <span className="text-green-400">Active via Browser Automation</span>
          </div>
          <p className="text-slate-400 mb-4">
            Social media posting is now handled through managed browser automation.
            Posts are scheduled and published directly via LinkedIn and X/Twitter web interfaces.
          </p>
          
          <div className="grid md:grid-cols-2 gap-4">
            <div className="bg-slate-800 rounded-lg p-4">
              <h3 className="font-semibold mb-2">LinkedIn</h3>
              <p className="text-sm text-slate-400">1 post/day, Mon-Fri, 8 AM CDT</p>
              <p className="text-sm text-slate-400">Logged in as Waters Deng</p>
            </div>
            <div className="bg-slate-800 rounded-lg p-4">
              <h3 className="font-semibold mb-2">X/Twitter</h3>
              <p className="text-sm text-slate-400">1 post/day, Mon-Fri, 9 AM CDT</p>
              <p className="text-sm text-slate-400">@RivalEdgeAI</p>
            </div>
          </div>
        </div>

        <div className="bg-slate-900 border border-slate-800 rounded-xl p-6">
          <h2 className="text-xl font-semibold mb-4">Recent Posts</h2>
          <p className="text-slate-400">
            Posts are managed through the autonomous social agent. 
            Check the daily notes for posting history and performance.
          </p>
        </div>
      </div>
    </div>
  );
}
