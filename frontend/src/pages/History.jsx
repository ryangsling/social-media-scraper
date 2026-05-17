import React, { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { scrapingApi } from "../services/api";
import toast from "react-hot-toast";
import { Trash2, ArrowRight, RefreshCw, Search, Twitter, Instagram, Linkedin, Facebook, Rss, Youtube, Sparkles, BookUser, Database } from "lucide-react";
import { format, formatDistanceToNow } from "date-fns";

const PLATFORM_ICONS = {
  twitter: Twitter, instagram: Instagram, linkedin: Linkedin,
  facebook: Facebook, reddit: Rss, youtube: Youtube,
  tiktok: Sparkles, quora: BookUser
};

const STATUS_STYLE = {
  completed: "bg-green-100 text-green-700",
  failed: "bg-red-100 text-red-700",
  running: "bg-yellow-100 text-yellow-700",
  pending: "bg-blue-100 text-blue-700",
};

export default function History() {
  const [jobs, setJobs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState({ platform: "", status: "" });
  const [search, setSearch] = useState("");

  const fetchJobs = () => {
    setLoading(true);
    scrapingApi.listJobs({ platform: filter.platform || undefined, status: filter.status || undefined, limit: 100 })
      .then((r) => setJobs(r.data))
      .finally(() => setLoading(false));
  };

  useEffect(() => { fetchJobs(); }, [filter]);

  const handleDelete = async (id, e) => {
    e.preventDefault();
    if (!window.confirm("Delete this job and all its results?")) return;
    try {
      await scrapingApi.deleteJob(id);
      toast.success("Job deleted");
      setJobs((prev) => prev.filter((j) => j.id !== id));
    } catch {
      toast.error("Failed to delete");
    }
  };

  const filtered = jobs.filter((j) =>
    !search || j.target.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-blue-900">Scraping History</h1>
          <p className="text-gray-500 text-sm mt-1">{jobs.length} total jobs</p>
        </div>
        <button onClick={fetchJobs} className="bg-white border border-gray-300 text-gray-700 font-semibold py-2 px-4 rounded-lg flex items-center gap-2 transition-all hover:bg-gray-50">
          <RefreshCw size={15} />
          Refresh
        </button>
      </div>

      {/* Filters */}
      <div className="flex flex-wrap gap-3">
        <div className="relative flex-1 min-w-48">
          <Search size={16} className="absolute left-3.5 top-1/2 -translate-y-1/2 text-gray-400" />
          <input className="w-full pl-10 pr-3 py-2 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500 text-sm" placeholder="Search by target..."
            value={search} onChange={(e) => setSearch(e.target.value)} />
        </div>
        <select className="w-auto py-2 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500 text-sm" value={filter.platform}
          onChange={(e) => setFilter({ ...filter, platform: e.target.value })}>
          <option value="">All Platforms</option>
          {Object.keys(PLATFORM_ICONS).map((p) => (
            <option key={p} value={p}>{p.charAt(0).toUpperCase() + p.slice(1)}</option>
          ))}
        </select>
        <select className="w-auto py-2 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500 text-sm" value={filter.status}
          onChange={(e) => setFilter({ ...filter, status: e.target.value })}>
          <option value="">All Status</option>
          {["pending", "running", "completed", "failed"].map((s) => (
            <option key={s} value={s}>{s.charAt(0).toUpperCase() + s.slice(1)}</option>
          ))}
        </select>
      </div>

      {/* Table */}
      <div className="bg-white border border-gray-200 rounded-lg overflow-hidden">
        {loading ? (
          <div className="flex items-center justify-center h-40">
            <div className="w-6 h-6 border-2 border-blue-600 border-t-transparent rounded-full animate-spin" />
          </div>
        ) : filtered.length === 0 ? (
          <div className="text-center py-16 text-gray-500">
            <p className="text-lg font-semibold mb-2">No jobs found</p>
            <Link to="/scrape" className="text-blue-600 text-sm hover:underline">Start your first scrape →</Link>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead className="bg-gray-50">
                <tr className="border-b border-gray-200 text-xs text-gray-500 uppercase tracking-wider">
                  <th className="text-left px-6 py-3 font-semibold">Platform</th>
                  <th className="text-left px-6 py-3 font-semibold">Target</th>
                  <th className="text-left px-6 py-3 font-semibold">Type</th>
                  <th className="text-left px-6 py-3 font-semibold">Method</th>
                  <th className="text-left px-6 py-3 font-semibold">Status</th>
                  <th className="text-left px-6 py-3 font-semibold">Results</th>
                  <th className="text-left px-6 py-3 font-semibold">Created</th>
                  <th className="px-6 py-3" />
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {filtered.map((job) => {
                  const PlatformIcon = PLATFORM_ICONS[job.platform] || Database;
                  return (
                  <tr key={job.id} className="hover:bg-gray-50 transition-colors">
                    <td className="px-6 py-4"><PlatformIcon size={20} className="text-gray-600" /></td>
                    <td className="px-6 py-4 font-medium text-gray-800">@{job.target}</td>
                    <td className="px-6 py-4 text-gray-600">{job.job_type}</td>
                    <td className="px-6 py-4">
                      <span className={`text-xs px-2 py-0.5 rounded-full font-semibold ${
                        job.method === "apify" ? "bg-purple-100 text-purple-700" : "bg-green-100 text-green-700"
                      }`}>{job.method}</span>
                    </td>
                    <td className="px-6 py-4">
                      <span className={`text-xs font-semibold px-2.5 py-1 rounded-full ${STATUS_STYLE[job.status]}`}>
                        {job.status}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-gray-800 font-semibold">{job.result_count}</td>
                    <td className="px-6 py-4 text-gray-500 text-xs" title={format(new Date(job.created_at), "PPP p")}>
                      {formatDistanceToNow(new Date(job.created_at), { addSuffix: true })}
                    </td>
                    <td className="px-6 py-4">
                      <div className="flex items-center gap-2">
                        <Link to={`/jobs/${job.id}`}
                          className="p-1.5 text-gray-500 hover:text-blue-600 transition-colors">
                          <ArrowRight size={15} />
                        </Link>
                        <button onClick={(e) => handleDelete(job.id, e)}
                          className="p-1.5 text-gray-500 hover:text-red-600 transition-colors">
                          <Trash2 size={15} />
                        </button>
                      </div>
                    </td>
                  </tr>
                )})}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
