import React, { createContext, useContext, useState, useEffect, useCallback } from "react";
import axios from "axios";
import { authApi } from "../services/api";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  const authAxios = axios.create({
    baseURL: process.env.REACT_APP_API_URL || "http://localhost:8000",
  });

  const logout = () => {
    localStorage.removeItem("token");
    setUser(null);
    setLoading(false);
  };

  const fetchUser = useCallback(async () => {
    const token = localStorage.getItem("token");
    if (token) {
      try {
        authAxios.defaults.headers.Authorization = `Bearer ${token}`;
        const res = await authAxios.get("/api/auth/me");
        setUser(res.data);
      } catch (error) {
        logout();
      }
    }
    setLoading(false);
  }, [authAxios]);

  useEffect(() => {
    fetchUser();
  }, [fetchUser]);

  authAxios.interceptors.response.use(
    (r) => r,
    (err) => {
      if (err.response?.status === 401) {
        logout();
      }
      return Promise.reject(err);
    }
  );

  const login = async (email, password) => {
    const res = await authApi.login({ email, password });
    localStorage.setItem("token", res.data.access_token);
    await fetchUser();
  };

  const register = async (email, username, password) => {
    await authApi.register({ email, username, password });
  };

  return (
    <AuthContext.Provider value={{ user, loading, login, logout, register, authAxios }}>
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => useContext(AuthContext);