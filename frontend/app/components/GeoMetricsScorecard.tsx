import { TrendingUp, TrendingDown, Minus, Sparkles, Quote, ThumbsUp, AlertCircle } from 'lucide-react';

interface GeoMetric {
  label: string;
  brand: number | string;
  competitor: number | string;
  competitorName: string;
  change?: number;
  unit?: string;
}

interface GeoMetricsScorecardProps {
  brandName: string;
  competitorName: string;
  metrics: GeoMetric[];
  lastUpdated?: string;
}

export default function GeoMetricsScorecard({
  brandName = 'Your Brand',
  competitorName = 'Top Competitor',
  metrics,
  lastUpdated = 'Updated monthly',
}: GeoMetricsScorecardProps) {
  const getTrend = (brand: number | string, competitor: number | string) => {
    const b = typeof brand === 'string' ? parseFloat(brand) : brand;
    const c = typeof competitor === 'string' ? parseFloat(competitor) : competitor;
    if (b > c) return 'up';
    if (b < c) return 'down';
    return 'neutral';
  };

  const getTrendColor = (trend: string) => {
    switch (trend) {
      case 'up': return 'text-emerald-400';
      case 'down': return 'text-red-400';
      default: return 'text-slate-400';
    }
  };

  const getTrendIcon = (trend: string) => {
    switch (trend) {
      case 'up': return <TrendingUp className="w-4 h-4" />;
      case 'down': return <TrendingDown className="w-4 h-4" />;
      default: return <Minus className="w-4 h-4" />;
    }
  };

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-2xl overflow-hidden">
      {/* Header */}
      <div className="px-6 py-5 border-b border-slate-800">
        <div className="flex items-center gap-2 mb-1">
          <Sparkles className="w-5 h-5 text-purple-400" />
          <h3 className="text-lg font-semibold text-white">AI Visibility Scorecard</h3>
        </div>
        <p className="text-slate-400 text-sm">How AI systems describe and recommend your brand vs. competitors</p>
      </div>

      {/* Comparison Table */}
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead>
            <tr className="border-b border-slate-800">
              <th className="text-left px-6 py-3 text-xs font-medium text-slate-500 uppercase tracking-wider">Metric</th>
              <th className="text-center px-4 py-3 text-xs font-medium text-blue-400 uppercase tracking-wider">{brandName}</th>
              <th className="text-center px-4 py-3 text-xs font-medium text-slate-500 uppercase tracking-wider">{competitorName}</th>
              <th className="text-right px-6 py-3 text-xs font-medium text-slate-500 uppercase tracking-wider">Trend</th>
            </tr>
          </thead>
          <tbody>
            {metrics.map((metric, i) => {
              const trend = getTrend(metric.brand, metric.competitor);
              const trendColor = getTrendColor(trend);
              const TrendIcon = getTrendIcon(trend);

              return (
                <tr key={i} className="border-b border-slate-800/50 last:border-0 hover:bg-slate-800/30 transition-colors">
                  <td className="px-6 py-4">
                    <div className="flex items-center gap-2">
                      {metric.label.includes('Visibility') && <Sparkles className="w-4 h-4 text-purple-400" />}
                      {metric.label.includes('Citation') && <Quote className="w-4 h-4 text-blue-400" />}
                      {metric.label.includes('Recommendation') && <ThumbsUp className="w-4 h-4 text-emerald-400" />}
                      {metric.label.includes('Sentiment') && <AlertCircle className="w-4 h-4 text-amber-400" />}
                      <span className="text-sm font-medium text-slate-200">{metric.label}</span>
                    </div>
                  </td>
                  <td className="px-4 py-4 text-center">
                    <span className="text-lg font-bold text-white">{metric.brand}{metric.unit}</span>
                    {metric.change !== undefined && (
                      <span className={`text-xs ml-2 ${metric.change >= 0 ? 'text-emerald-400' : 'text-red-400'}`}>
                        {metric.change >= 0 ? '+' : ''}{metric.change}{metric.unit}
                      </span>
                    )}
                  </td>
                  <td className="px-4 py-4 text-center">
                    <span className="text-lg font-medium text-slate-400">{metric.competitor}{metric.unit}</span>
                  </td>
                  <td className="px-6 py-4 text-right">
                    <div className={`inline-flex items-center gap-1 ${trendColor}`}>
                      {TrendIcon}
                      <span className="text-xs font-medium capitalize">{trend}</span>
                    </div>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      {/* Footer */}
      <div className="px-6 py-3 bg-slate-950/50 border-t border-slate-800">
        <p className="text-xs text-slate-500">{lastUpdated} • Data from ChatGPT, Claude, Perplexity, and Gemini</p>
      </div>
    </div>
  );
}
