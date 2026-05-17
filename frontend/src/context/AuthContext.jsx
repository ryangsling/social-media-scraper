import React, { createContext, useContext, useState, useEffect, useMemo } from "react";
import { authApi } from "../services/api";
import API from "../services/api";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [token, setToken] = useState(localStorage.getItem("token"));
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchUser = async () => {
      if (token) {
        localStorage.setItem("token", token);
        API.defaults.headers.Authorization = `Bearer ${token}`;
        try {
          const res = await authApi.me();
          setUser(res.data);
        } catch (error) {
          setToken(null); // Token is invalid
        }
      } else {
        localStorage.removeItem("token");
        delete API.defaults.headers.Authorization;
        setUser(null);
      }
      setLoading(false);
    };
    fetchUser();
  }, [token]);

  const login = async (email, password) => {
    const res = await authApi.login({ email, password });
    setToken(res.data.access_token);
  };

  const logout = () => {
    setToken(null);
  };

  const register = async (email, username, password) => {
    await authApi.register({ email, username, password });
  };

  const value = useMemo(
    () => ({ token, user, loading, login, logout, register }),
    [token, user, loading]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export const useAuth = () => useContext(AuthContext);