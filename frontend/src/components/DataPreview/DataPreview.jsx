import { useState } from "react";
import { Database, ChevronDown, ChevronUp } from "lucide-react";
import clsx from "clsx";

const TYPE_COLORS = {
  numeric: "bg-blue-500/10 text-blue-400 border-blue-500/20",
  categorical: "bg-purple-500/10 text-purple-400 border-purple-500/20",
  boolean: "bg-emerald-500/10 text-emerald-400 border-emerald-500/20",
  datetime: "bg-amber-500/10 text-amber-400 border-amber-500/20",
  text: "bg-slate-500/10 text-slate-400 border-slate-500/20",
};

export default function DataPreview({ uploadData, onTargetSelect, selectedTarget }) {
  const [schemaExpanded, setSchemaExpanded] = useState(false);
  const { filename, row_count, col_count, preview, columns, detected_schema } = uploadData;

  return (
    <div className="space-y-5">
      {/* Dataset summary */}
      <div className="card">
        <div className="flex items-center gap-3 mb-4">
          <Database className="w-5 h-5 text-brand" />
          <div>
            <h3 className="font-semibold text-slate-100">{filename}</h3>
            <p className="text-slate-500 text-sm">
              {row_count.toLocaleString()} rows · {col_count} columns
            </p>
          </div>
        </div>

        {/* Schema pills */}
        <div className="flex flex-wrap gap-2">
          {columns.map((col) => (
            <button
              key={col.name}
              onClick={() => onTargetSelect(col.name === selectedTarget ? null : col.name)}
              className={clsx(
                "badge border cursor-pointer hover:scale-105 transition-transform",
                TYPE_COLORS[col.dtype] || TYPE_COLORS.text,
                selectedTarget === col.name && "ring-2 ring-brand ring-offset-1 ring-offset-surface-card"
              )}
              title={`${col.missing_pct}% missing · ${col.unique_count} unique`}
            >
              {col.name}
              <span className="ml-1 opacity-60 text-[10px]">{col.dtype}</span>
            </button>
          ))}
        </div>

        {selectedTarget && (
          <p className="mt-3 text-sm text-brand-light">
            Target column selected: <strong>{selectedTarget}</strong>
            {" · "}
            <button className="underline" onClick={() => onTargetSelect(null)}>clear</button>
          </p>
        )}
      </div>

      {/* Schema details toggle */}
      <div className="card">
        <button
          className="w-full flex items-center justify-between text-slate-300 font-medium"
          onClick={() => setSchemaExpanded((v) => !v)}
        >
          <span>Column Details ({col_count})</span>
          {schemaExpanded ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
        </button>

        {schemaExpanded && (
          <div className="mt-4 overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="text-left text-slate-500 border-b border-surface-border">
                  <th className="pb-2 pr-4 font-medium">Column</th>
                  <th className="pb-2 pr-4 font-medium">Type</th>
                  <th className="pb-2 pr-4 font-medium">Missing</th>
                  <th className="pb-2 font-medium">Unique</th>
                </tr>
              </thead>
              <tbody>
                {columns.map((col) => (
                  <tr key={col.name} className="border-b border-surface-border/50">
                    <td className="py-2 pr-4 text-slate-200 font-mono text-xs">{col.name}</td>
                    <td className="py-2 pr-4">
                      <span className={clsx("badge border", TYPE_COLORS[col.dtype])}>{col.dtype}</span>
                    </td>
                    <td className="py-2 pr-4 text-slate-400">
                      {col.missing_count > 0
                        ? `${col.missing_count} (${col.missing_pct}%)`
                        : <span className="text-emerald-500">None</span>}
                    </td>
                    <td className="py-2 text-slate-400">{col.unique_count}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Data preview table */}
      <div className="card">
        <h3 className="text-slate-300 font-medium mb-3">Preview (first 8 rows)</h3>
        <div className="overflow-x-auto">
          <table className="w-full text-xs font-mono">
            <thead>
              <tr className="text-left text-slate-500 border-b border-surface-border">
                {Object.keys(preview[0] || {}).map((h) => (
                  <th key={h} className="pb-2 pr-6 font-medium whitespace-nowrap">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {preview.map((row, i) => (
                <tr key={i} className="border-b border-surface-border/30 hover:bg-surface-hover/30">
                  {Object.values(row).map((val, j) => (
                    <td key={j} className="py-1.5 pr-6 text-slate-300 max-w-[150px] truncate">
                      {String(val)}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
