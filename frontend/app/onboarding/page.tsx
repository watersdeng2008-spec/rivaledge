"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { useUser, useAuth } from "@clerk/nextjs";

export default function OnboardingPage() {
  const [step, setStep] = useState(1);
  const [loading, setLoading] = useState(false);
  const [companyName, setCompanyName] = useState("");
  const [companyUrl, setCompanyUrl] = useState("");
  const [industry, setIndustry] = useState("");
  const [trackingPrefs, setTrackingPrefs] = useState<string[]>([]);
  
  const router = useRouter();
  const { user, isLoaded } = useUser();
  const { getToken } = useAuth();

  useEffect(() => {
    if (isLoaded && !user) {
      router.push("/sign-in");
    }
  }, [user, isLoaded, router]);

  const industries = [
    "E-commerce / Retail",
    "SaaS / Software",
    "Healthcare / Telehealth",
    "Finance / Fintech",
    "Manufacturing",
    "Education",
    "Other",
  ];

  const trackingOptions = [
    { id: "price_changes", label: "Price Changes" },
    { id: "new_partnerships", label: "New Partnerships" },
    { id: "product_launches", label: "Product Launches" },
    { id: "new_locations", label: "New Locations" },
    { id: "marketing_campaigns", label: "Marketing Campaigns" },
    { id: "team_changes", label: "Team Changes" },
    { id: "funding_news", label: "Funding News" },
  ];

  const handleNext = async () => {
    // Get Clerk session token
    const token = await getToken();
    const headers: HeadersInit = {
      "Content-Type": "application/json",
    };
    if (token) {
      headers["Authorization"] = `Bearer ${token}`;
    }

    if (step === 1) {
      setLoading(true);
      try {
        const response = await fetch("/api/onboarding/step/1", {
          method: "POST",
          headers,
          body: JSON.stringify({
            company_name: companyName,
            company_url: companyUrl,
            industry: industry,
          }),
        });
        if (response.ok) setStep(2);
        else {
          const error = await response.json();
          console.error("Step 1 error:", error);
        }
      } finally { setLoading(false); }
    } else if (step === 2) {
      setLoading(true);
      try {
        const response = await fetch("/api/onboarding/step/2", {
          method: "POST",
          headers,
          body: JSON.stringify({
            tracking_preferences: trackingPrefs,
          }),
        });
        if (response.ok) setStep(3);
        else {
          const error = await response.json();
          console.error("Step 2 error:", error);
        }
      } finally { setLoading(false); }
    } else if (step === 3) {
      setStep(4);
    } else if (step === 4) {
      router.push("/dashboard");
    }
  };

  const toggleTracking = (id: string) => {
    setTrackingPrefs((prev) => 
      prev.includes(id) ? prev.filter((t) => t !== id) : [...prev, id]
    );
  };

  if (!isLoaded) return <div>Loading...</div>;
  if (!user) return <div>Redirecting to sign in...</div>;return(
    <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
      <div className="max-w-md w-full bg-white rounded-lg shadow-lg p-8">
        <div className="mb-8">
          <div className="flex justify-between mb-2">
            {[1, 2, 3, 4].map((s) => (
              <div key={s} className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium ${s <= step ? "bg-blue-600 text-white" : "bg-gray-200 text-gray-600"}`}>
                {s}
              </div>
            ))}
          </div>
          <div className="h-2 bg-gray-200 rounded-full">
            <div className="h-2 bg-blue-600 rounded-full transition-all" style={{ width: `${(step / 4) * 100}%` }} />
          </div>
        </div>

        {step === 1 && (
          <div>
            <h2 className="text-2xl font-bold mb-2">Welcome to RivalEdge</h2>
            <p className="text-gray-600 mb-6">Let&apos;s set up your competitive intelligence. First, tell us about your company.</p>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-1">Company Name *</label>
                <input 
                  type="text" 
                  name="companyName"
                  id="companyName"
                  value={companyName} 
                  onChange={(e) => setCompanyName(e.target.value)} 
                  className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 text-black"
                  placeholder="Acme Inc."
                  autoComplete="off"
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-1">Company Website</label>
                <input 
                  type="url" 
                  name="companyUrl"
                  id="companyUrl"
                  value={companyUrl} 
                  onChange={(e) => setCompanyUrl(e.target.value)} 
                  className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 text-black"
                  placeholder="https://acme.com"
                  autoComplete="off"
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-1">Industry</label>
                <select 
                  name="industry"
                  id="industry"
                  value={industry} 
                  onChange={(e) => setIndustry(e.target.value)} 
                  className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 text-black"
                >
                  <option value="">Select an industry</option>
                  {industries.map((ind) => <option key={ind} value={ind}>{ind}</option>)}
                </select>
              </div>
            </div>
          </div>
        )}

        {step === 2 && (
          <div>
            <h2 className="text-2xl font-bold mb-2">What to Track</h2>
            <p className="text-gray-600 mb-6">Select what you want to monitor about your competitors.</p>
            <div className="space-y-3">
              {trackingOptions.map((option) => (
                <label key={option.id} className="flex items-center p-3 border rounded-lg cursor-pointer hover:bg-gray-50">
                  <input 
                    type="checkbox"
                    name={option.id}
                    checked={trackingPrefs.includes(option.id)} 
                    onChange={() => toggleTracking(option.id)} 
                    className="w-4 h-4 text-blue-600 rounded"
                  />                  <span className="ml-3">{option.label}</span>
                </label>
              ))}
            </div>
          </div>
        )}

        {step === 3 && (
          <div>
            <h2 className="text-2xl font-bold mb-2">Add Competitors</h2>
            <p className="text-gray-600 mb-6">You&apos;ll add competitors in the next step. For now, let&apos;s preview whatyou&apos;ll get.</p>
            <div className="bg-blue-50 p-4 rounded-lg">
              <h3 className="font-semibold mb-2">Your Competitive Briefing will include:</h3>
              <ul className="space-y-2 text-sm">
                {trackingPrefs.map((pref) => {
                  const option = trackingOptions.find((o) => o.id === pref);
                  return <li key={pref} className="flex items-center"><span className="w-2 h-2 bg-blue-600 rounded-full mr-2" />{option?.label}</li>;
                })}
              </ul>
            </div>
          </div>
        )}

        {step === 4 && (
          <div>
            <h2 className="text-2xl font-bold mb-2">You&apos;re All Set!</h2>
            <p className="text-gray-600 mb-6">Here&apos;s what we&apos;ll track for {companyName}:</p>
            <div className="bg-green-50 p-4 rounded-lg mb-6">
              <h3 className="font-semibold text-green-800 mb-2">Configuration Summary</h3>
              <ul className="space-y-1 text-sm text-green-700">
                <li>Company: {companyName}</li>
                <li>Industry: {industry || "Not specified"}</li>
                <li>Tracking: {trackingPrefs.length} items</li>
              </ul>
            </div>
            <p className="text-gray-600">You&apos;ll receive your first competitive briefing tomorrow morning.</p>
          </div>
        )}

        <div className="mt-8 flex justify-between">
          {step > 1 && <button onClick={() => setStep(step - 1)} className="px-4 py-2 text-gray-600 hover:text-gray-800">Back</button>}
          <button 
            onClick={handleNext} 
            disabled={loading || (step === 1 && !companyName) || (step === 2 && trackingPrefs.length === 0)} 
            className="ml-auto px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? "Saving..." : step === 4 ? "Go to Dashboard" : "Next"}
          </button>
        </div>
      </div>
    </div>
  );
}
