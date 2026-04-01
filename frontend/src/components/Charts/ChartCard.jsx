import { useState, lazy, Suspense } from "react";
import { Maximize2, X } from "lucide-react";

// Lazy-load plotly to keep initial bundle smaller
const Plot = lazy(() => import("react-plotly.js"));

const PLOTLY_CONFIG = {
  displayModeBar: true,
  modeBarButtonsToRemove: ["select2d", "lasso2d", "autoScale2d"],
  displaylogo: false,
  responsive: true,
};

export default function ChartCard({ chart }) {
  const [expanded, setExpanded] = useState(false);
  const data = JSON.parse(chart.plotly_json);

  const renderPlot = (height = 320) => (
    <Suspense fallback={<div className="h-64 flex items-center justify-center text-slate-500">Loading chart…</div>}>
      <Plot
        data={data.data}
        layout={{ ...data.layout, autosize: true, height }}
        config={PLOTLY_CONFIG}
        style={{ width: "100%" }}
        useResizeHandler
      />
    </Suspense>
  );

  return (
    <>
      <div className="card flex flex-col gap-3">
        <div className="flex items-start justify-between gap-2">
          <div>
            <h4 className="font-medium text-slate-200 text-sm">{chart.title}</h4>
            <p className="text-slate-500 text-xs mt-0.5">{chart.description}</p>
          </div>
          <button
            onClick={() => setExpanded(true)}
            className="btn-ghost p-1 flex-shrink-0"
            title="Expand"
          >
            <Maximize2 className="w-3.5 h-3.5" />
          </button>
        </div>
        {renderPlot(280)}
      </div>

      {/* Fullscreen modal */}
      {expanded && (
        <div
          className="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 flex items-center justify-center p-6"
          onClick={() => setExpanded(false)}
        >
          <div
            className="bg-surface-card border border-surface-border rounded-2xl p-6 w-full max-w-4xl"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="flex items-center justify-between mb-4">
              <div>
                <h3 className="font-semibold text-slate-100">{chart.title}</h3>
                <p className="text-slate-400 text-sm">{chart.description}</p>
              </div>
              <button className="btn-ghost" onClick={() => setExpanded(false)}>
                <X className="w-4 h-4" />
              </button>
            </div>
            {renderPlot(500)}
          </div>
        </div>
      )}
    </>
  );
}
