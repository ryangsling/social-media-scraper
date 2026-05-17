import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { scrapingApi } from "../services/api";
import toast from "react-hot-toast";
import { Search, Zap, Info, Twitter, Instagram, Linkedin, Facebook, Rss, Youtube, Sparkles, BookUser, Database } from "lucide-react";

const PLATFORM_ICONS = {
  twitter: Twitter, instagram: Instagram, linkedin: Linkedin,
  facebook: Facebook, reddit: Rss, youtube: Youtube,
  tiktok: Sparkles, quora: BookUser
};

const JOB_TYPES = [
  { id: "profile", label: "Profile Posts" },
  { id: "posts", label: "Recent Posts" },
  { id: "hashtag", label: "Hashtag" },
  { id: "keyword", label: "Keyword Search" },
];

export default function NewScrape() {
  const navigate = useNavigate();
  const [platforms, setPlatforms] = useState([]);
  const [form, setForm] = useState({
    platform: "twitter",
    job_type: "profile",
    target: "",
    use_apify: false,
    max_results: 50,
  });
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    scrapingApi.getPlatforms().then((r) => setPlatforms(r.data.platforms));
  }, []);

  const selectedPlatform = platforms.find((p) => p.id === form.platform);
  const canUseApify = selectedPlatform?.paid;
  const canUseFree = selectedPlatform?.free;
  const unsupportedPlatform = !canUseApify && !canUseFree;

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!form.target.trim()) return toast.error("Enter a target username or keyword");
    if (unsupportedPlatform) {
      toast.error("This platform is not supported yet.");
      return;
    }
    if (!canUseFree && !form.use_apify) {
      toast.error("This platform requires Apify (paid). Enable it below.");
      return;
    }
    setLoading(true);
    try {
      const res = await scrapingApi.start(form);
      toast.success("Scraping job started!");
      navigate(`/jobs/${res.data.id}`);
    } catch (err) {
      toast.error(err.response?.data?.detail || "Failed to start job");
    } finally {
      setLoading(false);
    }
  };

  const PlatformIcon = PLATFORM_ICONS[form.platform] || Database;

  return (
    <div className="max-w-4xl mx-auto">
      <div className="text-center mb-10">
        <h1 className="text-3xl font-bold text-blue-900">New Scrape Job</h1>
        <p className="text-gray-500 text-sm mt-1">Configure and launch a scraping task</p>
      </div>

      <form onSubmit={handleSubmit} className="grid lg:grid-cols-3 gap-8">
        <div className="lg:col-span-2 space-y-6">
          {/* Platform */}
          <div className="bg-white p-6 border border-gray-200 rounded-lg">
            <h2 className="text-base font-semibold text-blue-900 mb-4">1. Select Platform</h2>
            <div className="grid grid-cols-3 sm:grid-cols-5 gap-3">
              {platforms.map((p) => {
                const Icon = PLATFORM_ICONS[p.id] || Database;
                return (
                <button key={p.id} type="button"
                  disabled={!p.free && !p.paid}
                  onClick={() => setForm({ ...form, platform: p.id, use_apify: !p.free && p.paid ? true : form.use_apify })}
                  className={`flex flex-col items-center gap-2 p-3 rounded-lg border text-sm font-medium transition-all
                    ${!p.free && !p.paid ? "opacity-40 cursor-not-allowed" : ""}
                    ${form.platform === p.id
                      ? "border-blue-500 bg-blue-50 text-blue-700"
                      : "border-gray-200 bg-white text-gray-600 hover:border-gray-300 hover:bg-gray-50"
                    }`}>
                  <Icon size={24} />
                  <span className="text-xs leading-tight text-center">{p.name.split("/")[0]}</span>
                </button>
              )})}
            </div>
          </div>

          {/* Job Config */}
          <div className="bg-white p-6 border border-gray-200 rounded-lg space-y-5">
            <h2 className="text-base font-semibold text-blue-900">2. Job Configuration</h2>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1.5">Job Type</label>
              <div className="flex flex-wrap gap-2">
                {JOB_TYPES.map((jt) => (
                  <button key={jt.id} type="button"
                    onClick={() => setForm({ ...form, job_type: jt.id })}
                    className={`px-3 py-1.5 rounded-full text-sm border transition-all
                      ${form.job_type === jt.id
                        ? "border-blue-500 bg-blue-500 text-white"
                        : "border-gray-300 text-gray-600 hover:border-gray-400"
                      }`}>
                    {jt.label}
                  </button>
                ))}
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1.5">
                {form.job_type === "hashtag" ? "Hashtag" :
                 form.job_type === "keyword" ? "Keyword" : "Username / Profile URL"}
              </label>
              <div className="relative">
                <PlatformIcon size={16} className="absolute left-3.5 top-1/2 -translate-y-1/2 text-gray-400" />
                <input type="text" required className="w-full pl-10 pr-3 py-2.5 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500"
                  placeholder={
                    form.job_type === "hashtag" ? "#marketing" :
                    form.job_type === "keyword" ? "growth hacking tips" : "elonmusk"
                  }
                  value={form.target}
                  onChange={(e) => setForm({ ...form, target: e.target.value })}
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1.5">
                Max Results: <span className="text-blue-900 font-semibold">{form.max_results}</span>
              </label>
              <input type="range" min={10} max={500} step={10}
                value={form.max_results}
                onChange={(e) => setForm({ ...form, max_results: parseInt(e.target.value) })}
                className="w-full accent-blue-600"
              />
              <div className="flex justify-between text-xs text-gray-500 mt-1">
                <span>10</span><span>500</span>
              </div>
            </div>
          </div>
        </div>

        <div className="space-y-6">
           {/* Method */}
          <div className="bg-white p-6 border border-gray-200 rounded-lg">
            <h2 className="text-base font-semibold text-blue-900 mb-4">3. Scraping Method</h2>
            <div className="space-y-3">
              <button type="button"
                disabled={!canUseFree}
                onClick={() => setForm({ ...form, use_apify: false })}
                className={`p-4 w-full rounded-lg border text-left transition-all
                  ${!canUseFree ? "opacity-40 cursor-not-allowed" : ""}
                  ${!form.use_apify
                    ? "border-green-500 bg-green-50"
                    : "border-gray-200 hover:border-gray-300"
                  }`}>
                <p className="text-sm font-semibold text-gray-800">🆓 Free</p>
                <p className="text-xs text-gray-500 mt-1">Open-source libraries. Rate limited.</p>
                {!canUseFree && <p className="text-xs text-red-500 mt-1">Not available for this platform</p>}
              </button>
              <button type="button"
                disabled={!canUseApify}
                onClick={() => setForm({ ...form, use_apify: true })}
                className={`p-4 w-full rounded-lg border text-left transition-all
                  ${!canUseApify ? "opacity-40 cursor-not-allowed" : ""}
                  ${form.use_apify
                    ? "border-purple-500 bg-purple-50"
                    : "border-gray-200 hover:border-gray-300"
                  }`}>
                <div className="flex items-center gap-1.5">
                  <Zap size={14} className="text-purple-600" />
                  <p className="text-sm font-semibold text-gray-800">Apify (Paid)</p>
                </div>
                <p className="text-xs text-gray-500 mt-1">Reliable. Requires APIFY_API_TOKEN.</p>
              </button>
            </div>
            {form.use_apify && (
              <div className="mt-4 p-3 bg-purple-50 border border-purple-200 rounded-lg flex gap-2">
                <Info size={14} className="text-purple-600 mt-0.5 shrink-0" />
                <p className="text-xs text-purple-800">Make sure APIFY_API_TOKEN is set in your .env file. Apify starts at $49/month.</p>
              </div>
            )}
             {unsupportedPlatform && (
              <div className="mt-4 p-3 bg-gray-100 border border-gray-200 rounded-lg flex gap-2">
                <Info size={14} className="text-gray-500 mt-0.5 shrink-0" />
                <p className="text-xs text-gray-600">This platform is not yet supported.</p>
              </div>
            )}
          </div>

          <button type="submit" disabled={loading || unsupportedPlatform}
            className="bg-amber-500 hover:bg-amber-600 text-white w-full flex items-center justify-center gap-2 py-3 text-base font-bold rounded-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed">
            {loading
              ? <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
              : <><Search size={18} /><span>Start Scraping</span></>
            }
          </button>
        </div>
      </form>
    </div>
  );
}
