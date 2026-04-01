import { CheckCircle2, Circle, Loader2, XCircle, ChevronRight } from "lucide-react";
import clsx from "clsx";

const STATUS_ICON = {
  pending: <Circle className="w-4 h-4 text-slate-600" />,
  running: <Loader2 className="w-4 h-4 text-brand animate-spin" />,
  done: <CheckCircle2 className="w-4 h-4 text-emerald-500" />,
  error: <XCircle className="w-4 h-4 text-red-400" />,
};

export default function PipelinePanel({ steps, plan }) {
  if (!steps || steps.length === 0) return null;

  return (
    <div className="card">
      <div className="flex items-center gap-2 mb-4">
        <ChevronRight className="w-4 h-4 text-brand" />
        <h3 className="font-semibold text-slate-200">Analysis Pipeline</h3>
      </div>

      {/* Rationale from agent */}
      {plan?.rationale && (
        <p className="text-slate-400 text-sm mb-4 leading-relaxed">{plan.rationale}</p>
      )}

      <div className="space-y-2">
        {steps.map((step) => (
          <div
            key={step.id}
            className={clsx(
              "flex items-center gap-3 p-2.5 rounded-lg text-sm",
              step.status === "running" && "bg-brand/5",
              step.status === "done" && "opacity-70",
              step.status === "error" && "bg-red-500/5"
            )}
          >
            {STATUS_ICON[step.status]}
            <span
              className={clsx(
                step.status === "done" && "text-slate-500",
                step.status === "running" && "text-slate-200 font-medium",
                step.status === "pending" && "text-slate-500",
                step.status === "error" && "text-red-400"
              )}
            >
              {step.label}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}
