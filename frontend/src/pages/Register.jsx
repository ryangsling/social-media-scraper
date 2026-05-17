import React, { useState, useEffect } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import toast from "react-hot-toast";
import { Zap, Mail, Lock, User, ArrowRight } from "lucide-react";

export default function Register() {
  const { user, register } = useAuth();
  const navigate = useNavigate();
  const [form, setForm] = useState({ email: "", username: "", password: "" });
  const [errors, setErrors] = useState({});
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (user) {
      navigate("/");
    }
  }, [user, navigate]);

  const validateForm = () => {
    const newErrors = {};
    if (form.username.length < 3) {
      newErrors.username = "Username must be at least 3 characters long.";
    }
    if (form.password.length < 8) {
      newErrors.password = "Password must be at least 8 characters long.";
    }
    // Basic email regex validation
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.email)) {
      newErrors.email = "Please enter a valid email address.";
    }
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!validateForm()) {
      toast.error("Please correct the errors below.");
      return;
    }
    setLoading(true);
    setErrors({});
    try {
      await register(form.email, form.username, form.password);
      toast.success("Account created! Please sign in.");
      navigate("/login");
    } catch (err) {
      if (err.response?.status === 422 && err.response?.data?.detail) {
        // Handle FastAPI validation errors
        const newErrors = {};
        err.response.data.detail.forEach(error => {
          const field = error.loc[1];
          const message = error.msg;
          newErrors[field] = message.charAt(0).toUpperCase() + message.slice(1);
        });
        setErrors(newErrors);
        toast.error("Please correct the validation errors.");
      } else if (err.response?.data?.detail) {
        toast.error(err.response.data.detail);
      } else {
        toast.error("Registration failed. An unknown error occurred.");
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col justify-center items-center p-4" style={{ fontFamily: "'Plus Jakarta Sans', sans-serif" }}>
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <div className="w-14 h-14 bg-blue-600 rounded-2xl flex items-center justify-center mx-auto mb-4">
            <Zap size={28} className="text-white" />
          </div>
          <h1 className="text-2xl font-bold text-blue-900">Create Account</h1>
          <p className="text-gray-500 text-sm mt-1">Start scraping social media</p>
        </div>
        <div className="bg-white border border-gray-200 rounded-lg shadow-sm p-8">
          <form onSubmit={handleSubmit} className="space-y-5">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1.5">Username</label>
              <div className="relative">
                <User size={16} className="absolute left-3.5 top-1/2 -translate-y-1/2 text-gray-400" />
                <input type="text" required
                  className={`w-full pl-10 pr-3 py-2.5 border rounded-lg focus:ring-blue-500 focus:border-blue-500 ${errors.username ? 'border-red-500' : 'border-gray-300'}`}
                  placeholder="johndoe"
                  value={form.username} onChange={(e) => setForm({ ...form, username: e.target.value })} />
              </div>
              {errors.username && <p className="text-red-500 text-xs mt-1">{errors.username}</p>}
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1.5">Email</label>
              <div className="relative">
                <Mail size={16} className="absolute left-3.5 top-1/2 -translate-y-1/2 text-gray-400" />
                <input type="email" required
                  className={`w-full pl-10 pr-3 py-2.5 border rounded-lg focus:ring-blue-500 focus:border-blue-500 ${errors.email ? 'border-red-500' : 'border-gray-300'}`}
                  placeholder="you@example.com"
                  value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} />
              </div>
              {errors.email && <p className="text-red-500 text-xs mt-1">{errors.email}</p>}
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1.5">Password</label>
              <div className="relative">
                <Lock size={16} className="absolute left-3.5 top-1/2 -translate-y-1/2 text-gray-400" />
                <input type="password" required
                  className={`w-full pl-10 pr-3 py-2.5 border rounded-lg focus:ring-blue-500 focus:border-blue-500 ${errors.password ? 'border-red-500' : 'border-gray-300'}`}
                  placeholder="••••••••"
                  value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })} />
              </div>
              {errors.password && <p className="text-red-500 text-xs mt-1">{errors.password}</p>}
            </div>
            <button type="submit" disabled={loading}
              className="bg-amber-500 hover:bg-amber-600 text-white font-bold w-full flex items-center justify-center gap-2 py-2.5 rounded-lg transition-all">
              {loading
                ? <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                : <><span>Create Account</span><ArrowRight size={16} /></>
              }
            </button>
          </form>
          <p className="text-center text-sm text-gray-500 mt-6">
            Already have an account?{" "}
            <Link to="/login" className="text-blue-600 hover:text-blue-800 font-medium">Sign in</Link>
          </p>
        </div>
      </div>
    </div>
  );
}