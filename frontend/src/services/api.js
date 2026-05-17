import axios from "axios";

const API = axios.create({ baseURL: process.env.REACT_APP_API_URL || "http://localhost:8000" });

API.interceptors.request.use((config) => {
  const token = localStorage.getItem("token");
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

API.interceptors.response.use(
  (r) => r,
  (err) => {
    if (err.response?.status === 401) {
      localStorage.removeItem("token");
      window.location.href = "/login";
    }
    return Promise.reject(err);
  }
);

export const authApi = {
  login: (data) => API.post("/api/auth/login", data),
  register: (data) => API.post("/api/auth/register", data),
  me: () => API.get("/api/auth/me"),
};

export const scrapingApi = {
  start: (data) => API.post("/api/scraping/start", data),
  listJobs: (params) => API.get("/api/scraping/jobs", { params }),
  getJob: (id) => API.get(`/api/scraping/jobs/${id}`),
  deleteJob: (id) => API.delete(`/api/scraping/jobs/${id}`),
  getResults: (id, params) => API.get(`/api/scraping/jobs/${id}/results`, { params }),
  getPlatforms: () => API.get("/api/scraping/platforms"),
};

export const dashboardApi = {
  stats: () => API.get("/api/dashboard/stats"),
};

export default API;
