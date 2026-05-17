import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { dashboardApi } from "../services/api";
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from "recharts";
import {
  Search, CheckCircle, XCircle, Clock, Database, Plus, ArrowRight,
  Twitter, Instagram, Linkedin, Facebook, Rss, Youtube, Sparkles, BookUser
} from "lucide-react";
import { formatDistanceToNow } from "date-fns";

const PLATFORM_ICONS = {
  twitter: Twitter, instagram: Instagram, linkedin: Linkedin,
  facebook: Facebook, reddit: Rss, youtube: Youtube,
  tiktok: Sparkles, quora: BookUser
};

const STATUS_STYLE = {
  completed: "bg-green-100 text-green-700 border-green-200",
  failed: "bg-red-100 text-red-700 border-red-200",
  running: "bg-yellow-100 text-yellow-700 border-yellow-200",
  pending: "bg-gray-100 text-gray-600 border-gray-200",
};

function StatCard({ icon: Icon, label, value, color }) {
  return (
    <div className="bg-white border border-gray-200 rounded-lg p-5">
      <div className="flex items-center justify-between mb-3">
        <p className="text-sm text-gray-500">{label}</p>
        <div className={`w-9 h-9 rounded-lg flex items-center justify-center ${color}`}>
          <Icon size={18} />
        </div>
      </div>
      <p className="text-3xl font-bold text-blue-900">{value?.toLocaleString()}</p>
    </div>
  );
}

export default function Dashboard() {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    dashboardApi.stats()
      .then((r) => setStats(r.data))
      .finally(() => setLoading(false));
    const iv = setInterval(() => {
      dashboardApi.stats().then((r) => setStats(r.data));
    }, 10000);
    return () => clearInterval(iv);
  }, []);

  if (loading) return (
    <div className="flex items-center justify-center h-64">
      <div className="w-8 h-8 border-2 border-blue-600 border-t-transparent rounded-full animate-spin" />
    </div>
  );

  const chartData = stats?.platforms_used?.map((p) => ({
    name: p.charAt(0).toUpperCase() + p.slice(1),
    jobs: stats.recent_jobs?.filter((j) => j.platform === p).length || 0,
  })) || [];

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-blue-900">Dashboard</h1>
          <p className="text-gray-500 text-sm mt-1">Monitor your scraping activity</p>
        </div>
        <Link to="/scrape" className="bg-amber-500 hover:bg-amber-600 text-white font-bold py-2.5 px-5 rounded-lg flex items-center gap-2 transition-all">
          <Plus size={16} />
          New Scrape
        </Link>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard icon={Search} label="Total Jobs" value={stats?.total_jobs} color="bg-blue-100 text-blue-600" />
        <StatCard icon={CheckCircle} label="Completed" value={stats?.completed_jobs} color="bg-green-100 text-green-600" />
        <StatCard icon={XCircle} label="Failed" value={stats?.failed_jobs} color="bg-red-100 text-red-600" />
        <StatCard icon={Database} label="Total Results" value={stats?.total_results} color="bg-indigo-100 text-indigo-600" />
      </div>

      {/* Chart + Recent */}
      <div className="grid lg:grid-cols-5 gap-6">
        {/* Chart */}
        <div className="bg-white border border-gray-200 rounded-lg p-5 lg:col-span-2">
          <h2 className="text-base font-semibold text-blue-900 mb-4">Platform Usage</h2>
          {chartData.length > 0 ? (
            <ResponsiveContainer width="100%" height={200}>
              <BarChart data={chartData} barSize={28}>
                <XAxis dataKey="name" tick={{ fill: "#475569", fontSize: 12 }} axisLine={false} tickLine={false} />
                <YAxis hide />
                <Tooltip
                  contentStyle={{ background: "#ffffff", border: "1px solid #e5e7eb", borderRadius: 8 }}
                  labelStyle={{ color: "#1e3a8a" }}
                  cursor={{fill: '#f1f5f9'}}
                />
                <Bar dataKey="jobs" radius={[4, 4, 0, 0]}>
                  {chartData.map((_, i) => (
                    <Cell key={i} fill={'#3B82F6'} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <div className="h-48 flex items-center justify-center text-gray-500 text-sm">No data yet</div>
          )}
        </div>

        {/* Recent Jobs */}
        <div className="bg-white border border-gray-200 rounded-lg p-5 lg:col-span-3">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-base font-semibold text-blue-900">Recent Jobs</h2>
            <Link to="/history" className="text-xs text-blue-600 hover:text-blue-800 flex items-center gap-1">
              View all <ArrowRight size={12} />
            </Link>
          </div>
          {stats?.recent_jobs?.length === 0 ? (
            <div className="text-center py-12 text-gray-500 text-sm">
              No jobs yet. <Link to="/scrape" className="text-blue-600 hover:underline font-semibold">Start scraping!</Link>
            </div>
          ) : (
            <div className="space-y-3">
              {stats?.recent_jobs?.map((job) => {
                const PlatformIcon = PLATFORM_ICONS[job.platform] || Database;
                return(
                <Link key={job.id} to={`/jobs/${job.id}`}
                  className="flex items-center gap-4 p-3 rounded-lg bg-gray-50 hover:bg-gray-100 transition-colors group">
                  <PlatformIcon size={20} className="text-gray-500" />
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-gray-800 truncate">@{job.target}</p>
                    <p className="text-xs text-gray-500">
                      {formatDistanceToNow(new Date(job.created_at), { addSuffix: true })}
                    </p>
                  </div>
                  <span className={`text-xs font-medium px-2.5 py-1 rounded-full border ${STATUS_STYLE[job.status]}`}>
                    {job.status}
                  </span>
                  <ArrowRight size={16} className="text-gray-400 group-hover:text-gray-600 transition-colors" />
                </Link>
              )})}
            </div>
          )}
        </div>
      </div>

      {/* Pending badge */}
      {stats?.pending_jobs > 0 && (
        <div className="bg-yellow-50 border-yellow-200 rounded-lg p-4 flex items-center gap-3">
          <Clock size={18} className="text-yellow-600" />
          <p className="text-sm text-yellow-800">
            <span className="font-semibold">{stats.pending_jobs}</span> job{stats.pending_jobs !== 1 ? "s" : ""} currently running or queued
          </p>
        </div>
      )}
    </div>
  );
}
