import { useState } from "react";
import { FileText, Download, Sparkles, AlertCircle, CheckCircle2, BarChart2, Cpu } from "lucide-react";

function Section({ icon: Icon, title, content, color = "text-brand" }) {
  if (!content) return null;
  return (
    <div className="card">
      <div className={`flex items-center gap-2 mb-3 ${color}`}>
        <Icon className="w-4 h-4" />
        <h3 className="font-semibold text-slate-200">{title}</h3>
      </div>
      <p className="text-slate-300 text-sm leading-relaxed whitespace-pre-wrap">{content}</p>
    </div>
  );
}

export default function ReportView({ report }) {
  const [downloading, setDownloading] = useState(false);

  const downloadReport = () => {
    const content = [
      `# ${report.title}`,
      `Generated: ${new Date(report.generated_at).toLocaleString()}`,
      "",
      "## Executive Summary",
      report.executive_summary,
      "",
      "## Data Quality",
      report.data_quality?.content,
      "",
      "## Exploratory Insights",
      report.eda_insights?.content,
      report.modeling_results ? "\n## Modeling Results\n" + report.modeling_results.content : "",
      "",
      "## Recommendations",
      report.recommendations,
      "",
      "## Limitations",
      report.limitations,
    ]
      .filter(Boolean)
      .join("\n");

    const blob = new Blob([content], { type: "text/markdown" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `report-${report.analysis_id.slice(0, 8)}.md`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="space-y-5">
      {/* Report header */}
      <div className="card bg-gradient-to-br from-brand/10 to-purple-500/5 border-brand/20">
        <div className="flex items-start justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-brand/20 flex items-center justify-center">
              <FileText className="w-5 h-5 text-brand" />
            </div>
            <div>
              <h2 className="font-bold text-slate-100 text-lg">{report.title}</h2>
              <p className="text-slate-500 text-sm">
                {new Date(report.generated_at).toLocaleString()}
              </p>
            </div>
          </div>
          <button onClick={downloadReport} className="btn-ghost flex items-center gap-1.5 text-sm">
            <Download className="w-4 h-4" />
            Download
          </button>
        </div>

        <div className="mt-4 p-4 bg-surface/50 rounded-xl border border-surface-border/50">
          <div className="flex items-center gap-2 mb-2">
            <Sparkles className="w-4 h-4 text-brand" />
            <span className="font-medium text-slate-200 text-sm">Executive Summary</span>
          </div>
          <p className="text-slate-300 text-sm leading-relaxed">{report.executive_summary}</p>
        </div>
      </div>

      <Section icon={AlertCircle} title="Data Quality" content={report.data_quality?.content} color="text-amber-400" />
      <Section icon={BarChart2} title="Exploratory Insights" content={report.eda_insights?.content} color="text-cyan-400" />
      {report.modeling_results && (
        <Section icon={Cpu} title="Modeling Results" content={report.modeling_results?.content} color="text-violet-400" />
      )}
      <Section icon={CheckCircle2} title="Recommendations" content={report.recommendations} color="text-emerald-400" />
      <Section icon={AlertCircle} title="Limitations" content={report.limitations} color="text-slate-400" />
    </div>
  );
}
