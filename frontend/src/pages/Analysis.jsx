import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { Play, Cpu, FileText, ChevronLeft, Loader2, AlertCircle } from "lucide-react";
import { useAnalysisStore } from "../store/analysisStore";
import { runAnalysis, runModeling, getReport } from "../services/api";
import DataPreview from "../components/DataPreview/DataPreview";
import PipelinePanel from "../components/Pipeline/PipelinePanel";
import ChartGrid from "../components/Charts/ChartGrid";
import InsightCard from "../components/Insights/InsightCard";
import ModelResults from "../components/ModelResults/ModelResults";
import ReportView from "../components/Report/ReportView";

const TABS = ["Overview", "Charts", "Insights", "Modeling", "Report"];

export default function Analysis() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [tab, setTab] = useState("Overview");

  const {
    uploadData, targetColumn, setTargetColumn,
    edaResults, edaLoading, edaError, setEdaResults, setEdaLoading, setEdaError,
    mlResults, mlLoading, mlError, setMlResults, setMlLoading, setMlError,
    report, reportLoading, reportError, setReport, setReportLoading, setReportError,
    pipelineSteps, initPipeline, setPipelineStep,
  } = useAnalysisStore();

  // If user navigated directly (no uploadData in store), we still have the ID
  // We could load from API — for now show a prompt to re-upload
  if (!uploadData) {
    return (
      <div className="max-w-2xl mx-auto px-6 py-20 text-center">
        <p className="text-slate-400 mb-4">No upload data in session. Please upload a CSV to start.</p>
        <button className="btn-primary" onClick={() => navigate("/")}>Go Home</button>
      </div>
    );
  }

  const handleRunAnalysis = async () => {
    if (edaLoading) return;
    setEdaLoading(true);
    setEdaError(null);

    const STEPS = [
      "Detect column types",
      "Compute summary statistics",
      "Analyze missing values",
      "Compute correlations",
      "Detect outliers",
      "Generate visualizations",
      "Build analysis plan",
      "Generate AI insights",
    ];
    initPipeline(STEPS);

    const stepDelay = (label) => {
      setPipelineStep(label, "running");
      return new Promise((res) => setTimeout(res, 100));
    };

    try {
      for (const s of STEPS.slice(0, -1)) {
        await stepDelay(s);
        setPipelineStep(s, "done");
      }
      setPipelineStep("Generate AI insights", "running");

      const results = await runAnalysis(id, targetColumn);
      setPipelineStep("Generate AI insights", "done");
      setEdaResults(results);
      setTab("Charts");
    } catch (err) {
      setEdaError(err.message);
      setEdaLoading(false);
    }
  };

  const handleRunModeling = async () => {
    if (!targetColumn) return;
    setMlLoading(true);
    setMlError(null);
    try {
      const results = await runModeling(id, targetColumn);
      setMlResults(results);
      setTab("Modeling");
    } catch (err) {
      setMlError(err.message);
      setMlLoading(false);
    }
  };

  const handleGetReport = async () => {
    setReportLoading(true);
    setReportError(null);
    try {
      const r = await getReport(id);
      setReport(r);
      setTab("Report");
    } catch (err) {
      setReportError(err.message);
      setReportLoading(false);
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-6 py-8 space-y-6">
      {/* Header */}
      <div className="flex items-center gap-4">
        <button className="btn-ghost flex items-center gap-1.5 text-sm" onClick={() => navigate("/")}>
          <ChevronLeft className="w-4 h-4" /> Back
        </button>
        <div>
          <h1 className="font-bold text-slate-100 text-xl">{uploadData.filename}</h1>
          <p className="text-slate-500 text-sm">
            {uploadData.row_count.toLocaleString()} rows · {uploadData.col_count} columns · ID: {id.slice(0, 8)}
          </p>
        </div>
      </div>

      <div className="flex gap-6">
        {/* Left sidebar */}
        <div className="w-72 flex-shrink-0 space-y-4">
          {/* Action buttons */}
          <div className="space-y-2">
            {!edaResults && (
              <button
                className="btn-primary w-full flex items-center justify-center gap-2"
                onClick={handleRunAnalysis}
                disabled={edaLoading}
              >
                {edaLoading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Play className="w-4 h-4" />}
                {edaLoading ? "Analyzing…" : "Run Analysis"}
              </button>
            )}
            {edaResults && !mlResults && targetColumn && (
              <button
                className="btn-primary w-full flex items-center justify-center gap-2"
                onClick={handleRunModeling}
                disabled={mlLoading}
              >
                {mlLoading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Cpu className="w-4 h-4" />}
                {mlLoading ? "Training models…" : `Run ML on '${targetColumn}'`}
              </button>
            )}
            {edaResults && (
              <button
                className="w-full flex items-center justify-center gap-2 border border-surface-border hover:bg-surface-hover text-slate-300 font-medium px-4 py-2 rounded-lg text-sm"
                onClick={handleGetReport}
                disabled={reportLoading}
              >
                {reportLoading ? <Loader2 className="w-4 h-4 animate-spin" /> : <FileText className="w-4 h-4" />}
                {reportLoading ? "Generating report…" : "Generate Report"}
              </button>
            )}
          </div>

          {/* Errors */}
          {(edaError || mlError || reportError) && (
            <div className="p-3 bg-red-500/10 border border-red-500/20 rounded-xl flex items-start gap-2 text-red-400 text-xs">
              <AlertCircle className="w-4 h-4 flex-shrink-0 mt-0.5" />
              {edaError || mlError || reportError}
            </div>
          )}

          {/* Pipeline panel */}
          {pipelineSteps.length > 0 && (
            <PipelinePanel steps={pipelineSteps} plan={edaResults?.analysis_plan} />
          )}
        </div>

        {/* Main content */}
        <div className="flex-1 min-w-0 space-y-5">
          {/* Tabs */}
          <div className="flex gap-1 border-b border-surface-border pb-0">
            {TABS.map((t) => (
              <button
                key={t}
                onClick={() => setTab(t)}
                className={`px-4 py-2 text-sm font-medium rounded-t-lg border-b-2 -mb-px transition-colors ${
                  tab === t
                    ? "border-brand text-brand-light"
                    : "border-transparent text-slate-500 hover:text-slate-300"
                }`}
                disabled={
                  (t === "Charts" || t === "Insights") && !edaResults ||
                  t === "Modeling" && !mlResults ||
                  t === "Report" && !report
                }
              >
                {t}
              </button>
            ))}
          </div>

          {/* Tab content */}
          {tab === "Overview" && (
            <DataPreview
              uploadData={uploadData}
              onTargetSelect={setTargetColumn}
              selectedTarget={targetColumn}
            />
          )}
          {tab === "Charts" && edaResults && (
            <ChartGrid charts={edaResults.charts} title="Exploratory Visualizations" />
          )}
          {tab === "Insights" && edaResults && (
            <div className="space-y-5">
              {/* Summary stats cards */}
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                {[
                  { label: "Rows", value: edaResults.summary_stats.row_count?.toLocaleString() },
                  { label: "Columns", value: edaResults.summary_stats.col_count },
                  { label: "Missing Cells", value: `${edaResults.summary_stats.total_missing_pct}%` },
                  { label: "Duplicates", value: edaResults.summary_stats.duplicate_rows },
                ].map(({ label, value }) => (
                  <div key={label} className="card text-center">
                    <p className="text-2xl font-bold text-slate-100">{value}</p>
                    <p className="text-xs text-slate-500 mt-1">{label}</p>
                  </div>
                ))}
              </div>
              <InsightCard insights={edaResults.insights} patterns={edaResults.patterns} />
            </div>
          )}
          {tab === "Modeling" && mlResults && (
            <div className="space-y-5">
              <ModelResults mlResults={mlResults} />
              <ChartGrid charts={mlResults.charts} title="Model Visualizations" />
            </div>
          )}
          {tab === "Report" && report && <ReportView report={report} />}
        </div>
      </div>
    </div>
  );
}
