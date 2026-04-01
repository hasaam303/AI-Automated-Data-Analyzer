import { create } from "zustand";

export const useAnalysisStore = create((set, get) => ({
  // Upload state
  uploadData: null,         // UploadResponse
  uploadProgress: 0,

  // EDA state
  edaResults: null,         // EDAResults
  edaLoading: false,
  edaError: null,

  // ML state
  mlResults: null,          // MLResults
  mlLoading: false,
  mlError: null,

  // Report state
  report: null,
  reportLoading: false,
  reportError: null,

  // Selected target column
  targetColumn: null,

  // Pipeline step tracking
  pipelineSteps: [],        // [{id, label, status: 'pending'|'running'|'done'|'error'}]

  // ── Actions ──────────────────────────────────────────────────────────────────

  setUploadData: (data) => set({ uploadData: data, uploadProgress: 100 }),
  setUploadProgress: (pct) => set({ uploadProgress: pct }),
  setTargetColumn: (col) => set({ targetColumn: col }),

  setEdaResults: (results) => set({ edaResults: results, edaLoading: false, edaError: null }),
  setEdaLoading: (v) => set({ edaLoading: v }),
  setEdaError: (err) => set({ edaError: err, edaLoading: false }),

  setMlResults: (results) => set({ mlResults: results, mlLoading: false, mlError: null }),
  setMlLoading: (v) => set({ mlLoading: v }),
  setMlError: (err) => set({ mlError: err, mlLoading: false }),

  setReport: (report) => set({ report, reportLoading: false, reportError: null }),
  setReportLoading: (v) => set({ reportLoading: v }),
  setReportError: (err) => set({ reportError: err, reportLoading: false }),

  initPipeline: (steps) =>
    set({ pipelineSteps: steps.map((label, i) => ({ id: i, label, status: "pending" })) }),

  setPipelineStep: (label, status) =>
    set((state) => ({
      pipelineSteps: state.pipelineSteps.map((s) =>
        s.label === label ? { ...s, status } : s
      ),
    })),

  reset: () =>
    set({
      uploadData: null,
      uploadProgress: 0,
      edaResults: null,
      edaLoading: false,
      edaError: null,
      mlResults: null,
      mlLoading: false,
      mlError: null,
      report: null,
      reportLoading: false,
      reportError: null,
      targetColumn: null,
      pipelineSteps: [],
    }),
}));
