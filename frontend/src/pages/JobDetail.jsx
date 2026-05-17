import React, { useState, useEffect, useCallback } from "react";
import { useParams, Link } from "react-router-dom";
import { scrapingApi } from "../services/api";
import { ArrowLeft, RefreshCw, ExternalLink, Heart, MessageCircle, Share2, Eye, Twitter, Instagram, Linkedin, Facebook, Rss, Youtube, Sparkles, BookUser, Database } from "lucide-react";
import { formatDistanceToNow, format } from "date-fns";

const STATUS_STYLE = {
  completed: "bg-green-100 text-green-700",
  failed: "bg-red-100 text-red-700",
  running: "bg-yellow-100 text-yellow-700",
  pending: "bg-blue-100 text-blue-700",
};

const PLATFORM_ICONS = {
  twitter: Twitter, instagram: Instagram, linkedin: Linkedin,
  facebook: Facebook, reddit: Rss, youtube: Youtube,
  tiktok: Sparkles, quora: BookUser
};

function ResultCard({ result }) {
  const raw = result.raw_data || {};
  const displayContent = result.content || raw.fullText || raw.text || raw.caption || raw.title || raw.description || raw.message || raw.story || raw.postText || "";
  const displayUrl = result.url || raw.url || raw.tweetUrl || raw.twitterUrl || raw.postUrl || raw.link || raw.webVideoUrl || raw.videoUrl || raw.shareUrl || raw.permalink || raw.canonicalUrl || "";
  const displayAuthor = result.author || raw.author?.userName || raw.ownerUsername || raw.pageName || raw.channel || raw.authorMeta?.name || raw.fullName || "";
  const Wrapper = displayUrl ? "a" : "div";
  const PlatformIcon = PLATFORM_ICONS[result.platform] || Database;

  return (
    <Wrapper
      {...(displayUrl ? { href: displayUrl, target: "_blank", rel: "noopener noreferrer" } : {})}
      className="bg-white border border-gray-200 p-5 rounded-lg hover:border-gray-300 hover:bg-gray-50 transition-colors block"
    >
      <div className="flex items-start justify-between gap-3 mb-3">
        <div className="flex items-center gap-2">
          <PlatformIcon size={18} className="text-gray-500" />
          <span className="text-sm font-medium text-gray-800">
            @{displayAuthor || "unknown"}
          </span>
          <span className="text-xs text-gray-500 bg-gray-100 px-2 py-0.5 rounded-full">
            {result.content_type}
          </span>
        </div>
        {displayUrl && (
          <span className="text-gray-400 hover:text-blue-600 transition-colors shrink-0">
            <ExternalLink size={14} />
          </span>
        )}
      </div>
      {displayContent && (
        <p className="text-sm text-gray-600 leading-relaxed line-clamp-4 mb-4">
          {displayContent}
        </p>
      )}
      <div className="flex items-center gap-5 text-xs text-gray-500">
        {result.likes > 0 && <span className="flex items-center gap-1.5"><Heart size={13} />{result.likes.toLocaleString()}</span>}
        {result.comments > 0 && <span className="flex items-center gap-1.5"><MessageCircle size={13} />{result.comments.toLocaleString()}</span>}
        {result.shares > 0 && <span className="flex items-center gap-1.5"><Share2 size={13} />{result.shares.toLocaleString()}</span>}
        {result.views > 0 && <span className="flex items-center gap-1.5"><Eye size={13} />{result.views.toLocaleString()}</span>}
        {result.published_at && <span className="ml-auto" title={format(new Date(result.published_at), "PPP p")}>{format(new Date(result.published_at), "MMM d, yyyy")}</span>}
      </div>
    </Wrapper>
  );
}

export default function JobDetail() {
  const { id } = useParams();
  const [job, setJob] = useState(null);
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");

  const fetchJob = useCallback(() => {
    Promise.all([
      scrapingApi.getJob(id),
      scrapingApi.getResults(id, { limit: 200 }),
    ])
      .then(([j, r]) => { setJob(j.data); setResults(r.data); })
      .finally(() => setLoading(false));
  }, [id]);

  useEffect(() => {
    fetchJob();
    let iv;
    if (job?.status === "running" || job?.status === "pending") {
      iv = setInterval(fetchJob, 3000);
    }
    return () => clearInterval(iv);
  }, [fetchJob, job?.status]);

  const filtered = results.filter((r) => {
    const raw = r.raw_data || {};
    const content = r.content || raw.fullText || raw.text || raw.caption || raw.title || raw.description || raw.message || raw.story || raw.postText || "";
    const author = r.author || raw.author?.userName || raw.ownerUsername || raw.pageName || raw.channel || raw.authorMeta?.name || raw.fullName || "";
    if (!search) return true;
    const needle = search.toLowerCase();
    return (
      content.toLowerCase().includes(needle) ||
      author.toLowerCase().includes(needle)
    );
  });

  if (loading) return <div className="flex items-center justify-center h-64"><div className="w-8 h-8 border-2 border-blue-600 border-t-transparent rounded-full animate-spin" /></div>;

  if (!job) return (
    <div className="text-center py-20">
      <p className="text-gray-500">Job not found</p>
      <Link to="/history" className="text-blue-600 hover:underline text-sm mt-2 block">← Back to history</Link>
    </div>
  );

  const PlatformIcon = PLATFORM_ICONS[job.platform] || Database;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-start justify-between gap-4">
        <div className="flex items-center gap-4">
          <Link to="/history" className="text-gray-400 hover:text-gray-600 transition-colors"><ArrowLeft size={20} /></Link>
          <div className="flex items-center gap-3">
            <PlatformIcon size={28} className="text-blue-800" />
            <div>
              <h1 className="text-2xl font-bold text-blue-900">@{job.target}</h1>
              <p className="text-gray-500 text-sm mt-0.5">
                {job.platform} • {job.job_type} • {job.method} • <span title={format(new Date(job.created_at), "PPP p")}>{formatDistanceToNow(new Date(job.created_at), { addSuffix: true })}</span>
              </p>
            </div>
          </div>
        </div>
        <div className="flex items-center gap-3">
          <span className={`text-xs font-semibold px-3 py-1.5 rounded-full ${STATUS_STYLE[job.status]}`}>{job.status}</span>
          <button onClick={fetchJob} className="bg-white border border-gray-300 text-gray-700 font-semibold py-2 px-3 rounded-lg flex items-center gap-2 transition-all hover:bg-gray-50"><RefreshCw size={14} /> Refresh</button>
        </div>
      </div>

      {/* Stats bar */}
      <div className="grid grid-cols-3 gap-4">
        <div className="bg-white border border-gray-200 rounded-lg p-4 text-center">
          <p className="text-2xl font-bold text-blue-900">{job.result_count}</p>
          <p className="text-xs text-gray-500 mt-0.5">Results</p>
        </div>
        <div className="bg-white border border-gray-200 rounded-lg p-4 text-center">
          <p className="text-sm font-semibold text-gray-700 capitalize">{job.method}</p>
          <p className="text-xs text-gray-500 mt-0.5">Method</p>
        </div>
        <div className="bg-white border border-gray-200 rounded-lg p-4 text-center">
          <p className="text-sm font-semibold text-gray-700 capitalize">{job.job_type}</p>
          <p className="text-xs text-gray-500 mt-0.5">Type</p>
        </div>
      </div>

      {job.error_message && <div className="bg-red-50 border border-red-200 rounded-lg p-4"><p className="text-sm font-semibold text-red-700 mb-1">Error</p><p className="text-sm text-red-600">{job.error_message}</p></div>}
      {(job.status === "running" || job.status === "pending") && <div className="bg-yellow-50 border border-yellow-200 p-4 rounded-lg flex items-center gap-3"><div className="w-4 h-4 border-2 border-yellow-500 border-t-transparent rounded-full animate-spin" /><p className="text-sm text-yellow-800">Scraping in progress... This page auto-refreshes.</p></div>}

      {/* Results */}
      {results.length > 0 && (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-base font-semibold text-blue-900">{results.length} Results</h2>
            <input className="w-64 pl-3 pr-3 py-2 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500 text-sm" placeholder="Search results..." value={search} onChange={(e) => setSearch(e.target.value)} />
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {filtered.map((r) => <ResultCard key={r.id} result={r} />)}
          </div>
          {filtered.length === 0 && search && <p className="text-center text-gray-500 text-sm py-8">No results match "{search}"</p>}
        </div>
      )}
    </div>
  );
}
