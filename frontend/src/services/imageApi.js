import axios from "axios";

const api = axios.create({ baseURL: process.env.REACT_APP_API_URL || "http://localhost:8000" });

export const getOperations = () => api.get("/api/v1/operations");

export const processImage = (formData) =>
  api.post("/api/v1/process", formData, { headers: { "Content-Type": "multipart/form-data" } });
