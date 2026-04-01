import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { BarChart3, Brain, Zap, FileSearch, ArrowRight } from "lucide-react";
import DropZone from "../components/Upload/DropZone";
import { uploadCSV } from "../services/api";
import { useAnalysisStore } from "../store/analysisStore";

const FEATURES = [
  { icon: FileSearch, label: "Auto EDA", desc: "Column types, stats, correlations, outliers" },
  { icon: BarChart3, label: "Smart Charts", desc: "Interactive Plotly visualizations" },
  { icon: Brain, label: "ML Models", desc: "Classification & regression baselines" },
  { icon: Zap, label: "AI Insights", desc: "GPT-powered business-ready summaries" },
];

export default function Home() {
  const navigate = useNavigate();
  const { setUploadData, setUploadProgress, reset } = useAnalysisStore();
  const [uploading, setUploading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [error, setError] = useState(null);

  const handleFile = async (file) => {
    reset();
    setUploading(true);
    setError(null);
    try {
      const data = await uploadCSV(file, (pct) => {
        setProgress(pct);
        setUploadProgress(pct);
      });
      setUploadData(data);
      navigate(`/analysis/${data.analysis_id}`);
    } catch (err) {
      setError(err.message);
      setUploading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto px-6 py-16 flex flex-col items-center gap-14">
      {/* Hero */}
      <div className="text-center space-y-4">
        <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-brand/10 border border-brand/20 text-brand-light text-sm mb-2">
          <Zap className="w-3.5 h-3.5" />
          Automated Data Analysis
        </div>
        <h1 className="text-4xl font-bold text-slate-100 leading-tight">
          Upload a CSV.
          <br />
          <span className="text-brand">Get a full analysis.</span>
        </h1>
        <p className="text-slate-400 text-lg max-w-xl mx-auto">
          AI-powered EDA, interactive charts, ML modeling, and business insights — generated automatically from your data.
        </p>
      </div>

      {/* Upload zone */}
      <DropZone onFile={handleFile} loading={uploading} progress={progress} />

      {error && (
        <div className="w-full max-w-2xl p-4 bg-red-500/10 border border-red-500/20 rounded-xl text-red-400 text-sm text-center">
          {error}
        </div>
      )}

      {/* Feature grid */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 w-full">
        {FEATURES.map(({ icon: Icon, label, desc }) => (
          <div key={label} className="card text-center hover:border-brand/30 hover:bg-surface-hover/20">
            <div className="w-9 h-9 mx-auto mb-3 rounded-xl bg-brand/10 flex items-center justify-center">
              <Icon className="w-4.5 h-4.5 text-brand" />
            </div>
            <p className="font-medium text-slate-200 text-sm">{label}</p>
            <p className="text-slate-500 text-xs mt-1">{desc}</p>
          </div>
        ))}
      </div>

      {/* Quick link to history */}
      <button
        onClick={() => navigate("/history")}
        className="flex items-center gap-2 text-slate-500 hover:text-slate-300 text-sm"
      >
        View past analyses <ArrowRight className="w-4 h-4" />
      </button>
    </div>
  );
}
