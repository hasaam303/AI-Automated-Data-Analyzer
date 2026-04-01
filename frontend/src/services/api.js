import axios from "axios";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || "/api",
  timeout: 120_000, // ML can take a while
});

api.interceptors.response.use(
  (res) => res.data,
  (err) => {
    const message = err.response?.data?.detail || err.message || "Unknown error";
    return Promise.reject(new Error(message));
  }
);

export const uploadCSV = (file, onProgress) => {
  const form = new FormData();
  form.append("file", file);
  return api.post("/upload", form, {
    headers: { "Content-Type": "multipart/form-data" },
    onUploadProgress: (e) => onProgress?.(Math.round((e.loaded / e.total) * 100)),
  });
};

export const runAnalysis = (analysisId, targetColumn = null) =>
  api.post(`/analysis/${analysisId}/run`, { target_column: targetColumn });

export const getAnalysis = (analysisId) =>
  api.get(`/analysis/${analysisId}`);

export const runModeling = (analysisId, targetColumn) =>
  api.post(`/modeling/${analysisId}/run`, { target_column: targetColumn });

export const getModeling = (analysisId) =>
  api.get(`/modeling/${analysisId}`);

export const getReport = (analysisId) =>
  api.get(`/report/${analysisId}`);

export const getHistory = () =>
  api.get("/history");

export const deleteAnalysis = (analysisId) =>
  api.delete(`/history/${analysisId}`);
