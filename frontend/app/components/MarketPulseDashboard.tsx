'use client';

import { useState } from 'react';
import {
  TrendingUp,
  TrendingDown,
  Zap,
  Eye,
  DollarSign,
  MessageSquare,
  AlertTriangle,
  ChevronLeft,
  ChevronRight,
  Sparkles,
  Target,
  BarChart3,
} from 'lucide-react';

interface CompetitorMove {
  competitor: string;
  action: string;
  impact: 'high' | 'medium' | 'low';
  date: string;
  category: 'pricing' | 'product' | 'messaging' | 'hiring' | 'partnership';
}

interface VisibilityChange {
  brand: string;
  previousScore: number;
  currentScore: number;
  change: number;
  trend: 'up' | 'down' | 'stable';
}

interface PricingChange {
  competitor: string;
  oldPrice: string;
  newPrice: string;
  change: string;
  date: string;
}

interface SentimentShift {
  brand: string;
  platform: string;
  previous: number;
  current: number;
  change: number;
}

interface MarketPulseData {
  weekOf: string;
  competitorMoves: CompetitorMove[];
  visibilityWinners: VisibilityChange[];
  visibilityLosers: VisibilityChange[];
  emergingCompetitors: string[];
  pricingChanges: PricingChange[];
  sentimentShifts: SentimentShift[];
}

const mockData: MarketPulseData = {
  weekOf: 'May 26 — June 1, 2026',
  competitorMoves: [
    { competitor: 'Klue', action: 'Launched AI-powered battle card generator', impact: 'high', date: 'May 28', category: 'product' },
    { competitor: 'Crayon', action: 'Raised pricing on Enterprise tier by 15%', impact: 'medium', date: 'May 29', category: 'pricing' },
    { competitor: 'Profound', action: 'New GEO certification program for agencies', impact: 'medium', date: 'May 27', category: 'partnership' },
    { competitor: 'Peec AI', action: 'Hired former Google AI lead as CTO', impact: 'high', date: 'May 30', category: 'hiring' },
  ],
  visibilityWinners: [
    { brand: 'RivalEdge', previousScore: 38, currentScore: 42, change: 4, trend: 'up' },
    { brand: 'Profound', previousScore: 61, currentScore: 67, change: 6, trend: 'up' },
  ],
  visibilityLosers: [
    { brand: 'Peec AI', previousScore: 45, currentScore: 41, change: -4, trend: 'down' },
    { brand: 'Otterly', previousScore: 33, currentScore: 29, change: -4, trend: 'down' },
  ],
  emergingCompetitors: ['Nectar (raised $30M for AI-native CI)', 'Competify (YC W26, GEO-focused)'],
  pricingChanges: [
    { competitor: 'Crayon', oldPrice: '$899/mo', newPrice: '$1,034/mo', change: '+15%', date: 'May 29' },
  ],
  sentimentShifts: [
    { brand: 'Klue', platform: 'G2', previous: 4.3, current: 4.5, change: 0.2 },
    { brand: 'Crayon', platform: 'G2', previous: 4.1, current: 3.9, change: -0.2 },
  ],
};

const impactColors = {
  high: 'bg-red-500/10 text-red-400 border-red-500/20',
  medium: 'bg-amber-500/10 text-amber-400 border-amber-500/20',
  low: 'bg-slate-500/10 text-slate-400 border-slate-500/20',
};

const categoryIcons = {
  pricing: DollarSign,
  product: Zap,
  messaging: MessageSquare,
  hiring: Target,
  partnership: Sparkles,
};

export default function MarketPulseDashboard() {
  const [data] = useState<MarketPulseData>(mockData);

  return (
    <div className="bg-slate-950 min-h-screen text-white p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold mb-2">Market Pulse</h1>
          <p className="text-slate-400">What&apos;s changing in your market?</p>
        </div>

        {/* Week Selector */}
        <div className="flex items-center gap-4 mb-8">
          <button className="p-2 hover:bg-slate-800 rounded-lg transition-colors">
            <ChevronLeft className="w-5 h-5 text-slate-400" />
          </button>
          <span className="text-lg font-medium">{data.weekOf}</span>
          <button className="p-2 hover:bg-slate-800 rounded-lg transition-colors">
            <ChevronRight className="w-5 h-5 text-slate-400" />
          </button>
        </div>

        {/* Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {/* Competitor Moves */}
          <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6">
            <div className="flex items-center gap-2 mb-4">
              <Zap className="w-5 h-5 text-blue-400" />
              <h2 className="text-lg font-semibold">Top Competitor Moves</h2>
            </div>
            <div className="space-y-3">
              {data.competitorMoves.map((move, i) => {
                const Icon = categoryIcons[move.category];
                return (
                  <div key={i} className="flex items-start gap-3 p-3 bg-slate-800/50 rounded-lg">
                    <div className="w-8 h-8 bg-slate-700 rounded-lg flex items-center justify-center flex-shrink-0">
                      <Icon className="w-4 h-4 text-slate-400" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-1">
                        <span className="font-medium text-sm">{move.competitor}</span>
                        <span className={`text-xs px-2 py-0.5 rounded-full border ${impactColors[move.impact]}`}>
                          {move.impact}
                        </span>
                      </div>
                      <p className="text-slate-400 text-sm">{move.action}</p>
                      <p className="text-slate-500 text-xs mt-1">{move.date}</p>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* AI Visibility Winners */}
          <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6">
            <div className="flex items-center gap-2 mb-4">
              <TrendingUp className="w-5 h-5 text-emerald-400" />
              <h2 className="text-lg font-semibold">AI Visibility Winners</h2>
            </div>
            <div className="space-y-3">
              {data.visibilityWinners.map((winner, i) => (
                <div key={i} className="flex items-center justify-between p-3 bg-slate-800/50 rounded-lg">
                  <span className="font-medium text-sm">{winner.brand}</span>
                  <div className="flex items-center gap-3">
                    <div className="text-right">
                      <div className="text-lg font-bold text-emerald-400">{winner.currentScore}%</div>
                      <div className="text-xs text-slate-500">from {winner.previousScore}%</div>
                    </div>
                    <div className="flex items-center gap-1 text-emerald-400">
                      <TrendingUp className="w-4 h-4" />
                      <span className="text-sm font-medium">+{winner.change}</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* AI Visibility Losers */}
          <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6">
            <div className="flex items-center gap-2 mb-4">
              <TrendingDown className="w-5 h-5 text-red-400" />
              <h2 className="text-lg font-semibold">AI Visibility Losers</h2>
            </div>
            <div className="space-y-3">
              {data.visibilityLosers.map((loser, i) => (
                <div key={i} className="flex items-center justify-between p-3 bg-slate-800/50 rounded-lg">
                  <span className="font-medium text-sm">{loser.brand}</span>
                  <div className="flex items-center gap-3">
                    <div className="text-right">
                      <div className="text-lg font-bold text-red-400">{loser.currentScore}%</div>
                      <div className="text-xs text-slate-500">from {loser.previousScore}%</div>
                    </div>
                    <div className="flex items-center gap-1 text-red-400">
                      <TrendingDown className="w-4 h-4" />
                      <span className="text-sm font-medium">{loser.change}</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Emerging Competitors */}
          <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6">
            <div className="flex items-center gap-2 mb-4">
              <AlertTriangle className="w-5 h-5 text-amber-400" />
              <h2 className="text-lg font-semibold">Emerging Competitors</h2>
            </div>
            <div className="space-y-3">
              {data.emergingCompetitors.map((comp, i) => (
                <div key={i} className="flex items-center gap-3 p-3 bg-slate-800/50 rounded-lg">
                  <div className="w-8 h-8 bg-amber-500/10 rounded-lg flex items-center justify-center">
                    <Eye className="w-4 h-4 text-amber-400" />
                  </div>
                  <span className="text-sm">{comp}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Pricing Changes */}
          <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6">
            <div className="flex items-center gap-2 mb-4">
              <DollarSign className="w-5 h-5 text-blue-400" />
              <h2 className="text-lg font-semibold">Pricing Changes</h2>
            </div>
            <div className="space-y-3">
              {data.pricingChanges.map((change, i) => (
                <div key={i} className="p-3 bg-slate-800/50 rounded-lg">
                  <div className="flex items-center justify-between mb-2">
                    <span className="font-medium text-sm">{change.competitor}</span>
                    <span className="text-xs text-slate-500">{change.date}</span>
                  </div>
                  <div className="flex items-center gap-3">
                    <span className="text-slate-400 line-through text-sm">{change.oldPrice}</span>
                    <span className="text-white font-medium">{change.newPrice}</span>
                    <span className="text-red-400 text-sm">{change.change}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Sentiment Shifts */}
          <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6">
            <div className="flex items-center gap-2 mb-4">
              <MessageSquare className="w-5 h-5 text-purple-400" />
              <h2 className="text-lg font-semibold">Sentiment Shifts</h2>
            </div>
            <div className="space-y-3">
              {data.sentimentShifts.map((shift, i) => (
                <div key={i} className="flex items-center justify-between p-3 bg-slate-800/50 rounded-lg">
                  <div>
                    <span className="font-medium text-sm">{shift.brand}</span>
                    <span className="text-slate-500 text-xs ml-2">{shift.platform}</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="flex items-center gap-1">
                      {Array.from({ length: 5 }).map((_, j) => (
                        <div
                          key={j}
                          className={`w-2 h-2 rounded-full ${
                            j < Math.round(shift.current) ? 'bg-purple-400' : 'bg-slate-700'
                          }`}
                        />
                      ))}
                    </div>
                    <span className={`text-sm font-medium ${shift.change >= 0 ? 'text-emerald-400' : 'text-red-400'}`}>
                      {shift.change >= 0 ? '+' : ''}{shift.change}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Summary Footer */}
        <div className="mt-8 p-6 bg-gradient-to-r from-blue-600/5 via-purple-600/10 to-blue-600/5 border border-slate-800 rounded-2xl">
          <div className="flex items-center gap-2 mb-2">
            <BarChart3 className="w-5 h-5 text-blue-400" />
            <h3 className="text-lg font-semibold">Weekly Summary</h3>
          </div>
          <p className="text-slate-300 leading-relaxed">
            This week saw <span className="text-white font-medium">2 major competitor moves</span> (Klue AI launch, Peec AI CTO hire), 
            <span className="text-emerald-400 font-medium"> 2 brands gaining AI visibility</span>, and 
            <span className="text-red-400 font-medium"> 2 brands losing ground</span>. 
            Crayon raised Enterprise pricing by 15% — potential opportunity for positioning. 
            Watch Nectar ($30M raise) and Competify (YC W26) as emerging threats.
          </p>
        </div>
      </div>
    </div>
  );
}
