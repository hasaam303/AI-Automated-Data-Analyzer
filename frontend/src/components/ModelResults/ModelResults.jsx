import { Trophy, Cpu, Sparkles, Clock } from "lucide-react";
import clsx from "clsx";

const METRIC_LABELS = {
  accuracy: "Accuracy",
  f1_weighted: "F1 (weighted)",
  roc_auc: "ROC-AUC",
  rmse: "RMSE",
  mae: "MAE",
  r2: "R²",
};

function MetricBadge({ name, value }) {
  const isGood = (name === "accuracy" || name === "roc_auc" || name === "f1_weighted" || name === "r2") && value >= 0.7;
  const isBad = (name === "accuracy" || name === "roc_auc" || name === "f1_weighted" || name === "r2") && value < 0.5;
  return (
    <div className={clsx(
      "rounded-lg p-3 text-center border",
      isGood ? "bg-emerald-500/5 border-emerald-500/20" : isBad ? "bg-red-500/5 border-red-500/20" : "bg-surface border-surface-border"
    )}>
      <p className="text-xs text-slate-500 mb-1">{METRIC_LABELS[name] || name}</p>
      <p className={clsx("font-bold text-lg", isGood ? "text-emerald-400" : isBad ? "text-red-400" : "text-slate-200")}>
        {typeof value === "number" ? value.toFixed(4) : value}
      </p>
    </div>
  );
}

export default function ModelResults({ mlResults }) {
  if (!mlResults) return null;
  const { task_type, target_column, models, best_model, best_metrics, preprocessing_steps, explanation, feature_importance } = mlResults;

  return (
    <div className="space-y-5">
      <h2 className="section-title flex items-center gap-2">
        <Cpu className="w-5 h-5 text-brand" />
        Modeling Results
        <span className="badge bg-brand/10 text-brand-light border border-brand/20 font-normal ml-1">
          {task_type}
        </span>
      </h2>

      {/* Best model highlight */}
      <div className="card border border-brand/30 bg-brand/5">
        <div className="flex items-center gap-2 mb-4">
          <Trophy className="w-5 h-5 text-amber-400" />
          <div>
            <h3 className="font-semibold text-slate-100">Best Model: {best_model}</h3>
            <p className="text-slate-500 text-sm">Target: {target_column}</p>
          </div>
        </div>
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-3">
          {Object.entries(best_metrics).map(([k, v]) => (
            <MetricBadge key={k} name={k} value={v} />
          ))}
        </div>
      </div>

      {/* All models comparison */}
      <div className="card">
        <h3 className="font-medium text-slate-300 mb-3">Model Comparison</h3>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="text-left text-slate-500 border-b border-surface-border">
                <th className="pb-2 pr-4 font-medium">Model</th>
                {Object.keys(models[0]?.metrics || {}).map((k) => (
                  <th key={k} className="pb-2 pr-4 font-medium">{METRIC_LABELS[k] || k}</th>
                ))}
                <th className="pb-2 font-medium">
                  <Clock className="w-3.5 h-3.5 inline mr-1" />Time (s)
                </th>
              </tr>
            </thead>
            <tbody>
              {models.map((m) => (
                <tr
                  key={m.name}
                  className={clsx(
                    "border-b border-surface-border/50",
                    m.name === best_model && "bg-brand/5"
                  )}
                >
                  <td className="py-2.5 pr-4 font-medium text-slate-200 flex items-center gap-2">
                    {m.name === best_model && <Trophy className="w-3.5 h-3.5 text-amber-400" />}
                    {m.name}
                  </td>
                  {Object.entries(m.metrics).map(([k, v]) => (
                    <td key={k} className="py-2.5 pr-4 text-slate-300 font-mono">
                      {v.toFixed(4)}
                    </td>
                  ))}
                  <td className="py-2.5 text-slate-500 font-mono">{m.train_time_seconds}s</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Preprocessing steps */}
      {preprocessing_steps.length > 0 && (
        <div className="card">
          <h3 className="font-medium text-slate-300 mb-3">Preprocessing Applied</h3>
          <ul className="space-y-1.5">
            {preprocessing_steps.map((s, i) => (
              <li key={i} className="flex items-start gap-2 text-sm text-slate-400">
                <span className="mt-1.5 w-1.5 h-1.5 rounded-full bg-brand/60 flex-shrink-0" />
                {s}
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* AI Explanation */}
      <div className="card border-l-2 border-brand">
        <div className="flex items-center gap-2 mb-3">
          <Sparkles className="w-4 h-4 text-brand" />
          <h3 className="font-semibold text-slate-200">AI Explanation</h3>
        </div>
        <p className="text-slate-300 text-sm leading-relaxed">{explanation}</p>
      </div>
    </div>
  );
}
