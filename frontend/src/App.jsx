import React, { useState, useEffect, useCallback } from "react";
import axios from "axios";
import Navbar from "./components/Navbar";
import FilterBar from "./components/FilterBar";
import NewsCard from "./components/NewsCard";

const API_BASE =
  process.env.REACT_APP_API_BASE || "http://localhost:8000";

/* ── Skeleton placeholder while loading ── */
function SkeletonCard() {
  return (
    <div className="glass-card p-5 space-y-4">
      <div className="skeleton h-4 w-24" />
      <div className="skeleton h-6 w-full" />
      <div className="skeleton h-6 w-3/4" />
      <div className="space-y-2 mt-4">
        <div className="skeleton h-3 w-full" />
        <div className="skeleton h-3 w-full" />
        <div className="skeleton h-3 w-5/6" />
      </div>
      <div className="skeleton h-3 w-32 mt-4" />
    </div>
  );
}

export default function App() {
  const [articles, setArticles] = useState([]);
  const [lang, setLang] = useState("hi");
  const [category, setCategory] = useState("all");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchArticles = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const params = {};
      if (category !== "all") params.category = category;
      if (lang) params.lang = lang;

      const { data } = await axios.get(`${API_BASE}/articles`, { params });
      setArticles(data);
    } catch (err) {
      console.error("Failed to fetch articles:", err);
      setError("समाचार लोड करने में विफल। कृपया बाद में पुनः प्रयास करें।");
    } finally {
      setLoading(false);
    }
  }, [category, lang]);

  useEffect(() => {
    fetchArticles();
  }, [fetchArticles]);

  return (
    <div className="min-h-screen flex flex-col">
      <Navbar />

      <main className="flex-1 w-full max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pb-16">
        <FilterBar
          category={category}
          setCategory={setCategory}
          lang={lang}
          setLang={setLang}
        />

        {/* Error state */}
        {error && (
          <div className="mt-8 text-center">
            <div className="inline-flex items-center gap-2 px-5 py-3 rounded-xl bg-red-500/10 border border-red-500/20 text-red-400 text-sm">
              <svg className="w-5 h-5 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              {error}
            </div>
          </div>
        )}

        {/* Loading skeletons */}
        {loading && (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6 mt-8">
            {[...Array(6)].map((_, i) => (
              <SkeletonCard key={i} />
            ))}
          </div>
        )}

        {/* Articles grid */}
        {!loading && !error && articles.length > 0 && (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6 mt-8">
            {articles.map((article, idx) => (
              <div
                key={article.id || article._id || idx}
                className="animate-slide-up"
                style={{ animationDelay: `${idx * 60}ms` }}
              >
                <NewsCard article={article} lang={lang} />
              </div>
            ))}
          </div>
        )}

        {/* Empty state */}
        {!loading && !error && articles.length === 0 && (
          <div className="mt-20 text-center space-y-4">
            <div className="text-6xl">📭</div>
            <h2 className="text-xl font-semibold text-white/80">
              {lang === "hi"
                ? "कोई समाचार नहीं मिला"
                : lang === "mr"
                ? "कोणतीही बातमी सापडली नाही"
                : "No articles found"}
            </h2>
            <p className="text-sm text-white/40">
              {lang === "hi"
                ? "जल्द ही नए समाचार आने वाले हैं।"
                : lang === "mr"
                ? "लवकरच नवीन बातम्या येत आहेत."
                : "New articles are on their way. Check back soon!"}
            </p>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="border-t border-white/5 py-6 text-center text-xs text-white/30">
        © {new Date().getFullYear()} AI News Hub — Powered by Gemini AI &amp;
        Open Data
      </footer>
    </div>
  );
}
