import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { Clock, Trash2, ArrowRight, Loader2, Database, CheckCircle2, AlertCircle, Cpu } from "lucide-react";
import { getHistory, deleteAnalysis } from "../services/api";
import clsx from "clsx";

const STATUS_CONFIG = {
  uploaded: { color: "text-slate-400", bg: "bg-slate-500/10", icon: Database },
  analyzing: { color: "text-blue-400", bg: "bg-blue-500/10", icon: Loader2 },
  analyzed: { color: "text-cyan-400", bg: "bg-cyan-500/10", icon: CheckCircle2 },
  modeling: { color: "text-violet-400", bg: "bg-violet-500/10", icon: Cpu },
  completed: { color: "text-emerald-400", bg: "bg-emerald-500/10", icon: CheckCircle2 },
  error: { color: "text-red-400", bg: "bg-red-500/10", icon: AlertCircle },
};

export default function History() {
  const navigate = useNavigate();
  const [analyses, setAnalyses] = useState([]);
  const [loading, setLoading] = useState(true);
  const [deleting, setDeleting] = useState(null);

  useEffect(() => {
    getHistory()
      .then(setAnalyses)
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  const handleDelete = async (id, e) => {
    e.stopPropagation();
    if (!confirm("Delete this analysis?")) return;
    setDeleting(id);
    try {
      await deleteAnalysis(id);
      setAnalyses((prev) => prev.filter((a) => a.id !== id));
    } catch (err) {
      alert(err.message);
    } finally {
      setDeleting(null);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="w-6 h-6 text-brand animate-spin" />
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto px-6 py-10">
      <div className="flex items-center gap-3 mb-8">
        <Clock className="w-5 h-5 text-brand" />
        <h1 className="text-xl font-bold text-slate-100">Analysis History</h1>
        <span className="badge bg-surface-card border border-surface-border text-slate-400 ml-1">
          {analyses.length}
        </span>
      </div>

      {analyses.length === 0 ? (
        <div className="card text-center py-16">
          <Database className="w-10 h-10 text-slate-600 mx-auto mb-3" />
          <p className="text-slate-500">No analyses yet. Upload a CSV to get started.</p>
          <button className="btn-primary mt-4" onClick={() => navigate("/")}>
            Upload Dataset
          </button>
        </div>
      ) : (
        <div className="space-y-3">
          {analyses.map((a) => {
            const sc = STATUS_CONFIG[a.status] || STATUS_CONFIG.uploaded;
            const Icon = sc.icon;
            return (
              <div
                key={a.id}
                className="card hover:border-brand/30 hover:bg-surface-hover/20 cursor-pointer group flex items-center gap-4"
                onClick={() => navigate(`/analysis/${a.id}`)}
              >
                <div className={clsx("w-9 h-9 rounded-lg flex items-center justify-center flex-shrink-0", sc.bg)}>
                  <Icon className={clsx("w-4 h-4", sc.color, a.status === "analyzing" && "animate-spin")} />
                </div>

                <div className="flex-1 min-w-0">
                  <p className="font-medium text-slate-200 truncate">{a.filename}</p>
                  <p className="text-slate-500 text-sm">
                    {a.row_count ? `${a.row_count.toLocaleString()} rows · ${a.col_count} cols · ` : ""}
                    {new Date(a.created_at).toLocaleDateString()} · ID: {a.id.slice(0, 8)}
                  </p>
                </div>

                <div className="flex items-center gap-3">
                  <span className={clsx("badge border", sc.bg, sc.color)}>{a.status}</span>
                  {a.has_ml && (
                    <span className="badge bg-violet-500/10 text-violet-400 border-violet-500/20">ML</span>
                  )}
                  <button
                    className="opacity-0 group-hover:opacity-100 btn-ghost p-1.5 text-red-400 hover:text-red-300"
                    onClick={(e) => handleDelete(a.id, e)}
                    disabled={deleting === a.id}
                  >
                    {deleting === a.id ? (
                      <Loader2 className="w-4 h-4 animate-spin" />
                    ) : (
                      <Trash2 className="w-4 h-4" />
                    )}
                  </button>
                  <ArrowRight className="w-4 h-4 text-slate-600 group-hover:text-slate-400" />
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
