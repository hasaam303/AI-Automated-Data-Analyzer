import { Sparkles, AlertTriangle, TrendingUp } from "lucide-react";

export default function InsightCard({ insights, patterns }) {
  return (
    <div className="space-y-4">
      {/* AI Narrative */}
      <div className="card border-l-2 border-brand">
        <div className="flex items-center gap-2 mb-3">
          <Sparkles className="w-4 h-4 text-brand" />
          <h3 className="font-semibold text-slate-200">AI Insights</h3>
        </div>
        <p className="text-slate-300 text-sm leading-relaxed whitespace-pre-wrap">{insights}</p>
      </div>

      {/* Key patterns */}
      {patterns && patterns.length > 0 && (
        <div className="card">
          <div className="flex items-center gap-2 mb-3">
            <TrendingUp className="w-4 h-4 text-amber-400" />
            <h3 className="font-semibold text-slate-200">Key Patterns Detected</h3>
          </div>
          <ul className="space-y-2">
            {patterns.map((p, i) => (
              <li key={i} className="flex items-start gap-2 text-sm text-slate-300">
                <span className="mt-1.5 w-1.5 h-1.5 rounded-full bg-amber-400 flex-shrink-0" />
                {p}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
