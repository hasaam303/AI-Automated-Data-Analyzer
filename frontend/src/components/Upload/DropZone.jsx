import { useCallback, useState } from "react";
import { useDropzone } from "react-dropzone";
import { Upload, FileText, AlertCircle } from "lucide-react";
import clsx from "clsx";

export default function DropZone({ onFile, loading, progress }) {
  const [error, setError] = useState(null);

  const onDrop = useCallback(
    (accepted, rejected) => {
      setError(null);
      if (rejected.length > 0) {
        setError("Only CSV files are accepted.");
        return;
      }
      if (accepted[0]) onFile(accepted[0]);
    },
    [onFile]
  );

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: { "text/csv": [".csv"], "application/vnd.ms-excel": [".csv"] },
    maxFiles: 1,
    disabled: loading,
  });

  return (
    <div className="w-full max-w-2xl mx-auto">
      <div
        {...getRootProps()}
        className={clsx(
          "border-2 border-dashed rounded-2xl p-12 text-center cursor-pointer transition-all",
          isDragActive
            ? "border-brand bg-brand/5 scale-[1.01]"
            : "border-surface-border hover:border-brand/50 hover:bg-surface-hover/30",
          loading && "opacity-60 cursor-not-allowed"
        )}
      >
        <input {...getInputProps()} />

        <div className="flex flex-col items-center gap-4">
          {loading ? (
            <>
              <div className="w-12 h-12 rounded-full border-4 border-brand border-t-transparent animate-spin" />
              <p className="text-slate-300 font-medium">Uploading… {progress}%</p>
              <div className="w-48 h-1.5 bg-surface-border rounded-full overflow-hidden">
                <div
                  className="h-full bg-brand rounded-full transition-all duration-300"
                  style={{ width: `${progress}%` }}
                />
              </div>
            </>
          ) : (
            <>
              <div className="w-14 h-14 rounded-2xl bg-brand/10 flex items-center justify-center">
                <Upload className="w-7 h-7 text-brand" />
              </div>
              <div>
                <p className="text-slate-200 font-semibold text-lg">
                  {isDragActive ? "Drop your CSV here" : "Upload a CSV dataset"}
                </p>
                <p className="text-slate-500 text-sm mt-1">
                  Drag & drop or click to browse · Max 50 MB
                </p>
              </div>
              <div className="flex items-center gap-2 text-xs text-slate-600">
                <FileText className="w-3.5 h-3.5" />
                <span>CSV format only</span>
              </div>
            </>
          )}
        </div>
      </div>

      {error && (
        <div className="mt-3 flex items-center gap-2 text-red-400 text-sm">
          <AlertCircle className="w-4 h-4 flex-shrink-0" />
          {error}
        </div>
      )}
    </div>
  );
}
