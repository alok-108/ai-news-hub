import React, { useState } from "react";

const BADGE_STYLES = {
  politics: "badge-politics",
  sports: "badge-sports",
  entertainment: "badge-entertainment",
  local: "badge-local",
  jobs: "badge-jobs",
};

const CATEGORY_ICONS = {
  politics: "🏛️",
  sports: "🏏",
  entertainment: "🎬",
  local: "📍",
  jobs: "💼",
};

function timeAgo(dateStr) {
  if (!dateStr) return "";
  const diff = Date.now() - new Date(dateStr).getTime();
  const mins = Math.floor(diff / 60000);
  if (mins < 1) return "just now";
  if (mins < 60) return `${mins}m ago`;
  const hrs = Math.floor(mins / 60);
  if (hrs < 24) return `${hrs}h ago`;
  const days = Math.floor(hrs / 24);
  return `${days}d ago`;
}

export default function NewsCard({ article, lang }) {
  const [expanded, setExpanded] = useState(false);

  const content = article.content?.[lang] || article.content?.en || {};
  const title = content.title || "Untitled";
  const body = content.body || "";
  const cat = article.category || "general";
  const published = article.published || article.created_at;

  const preview = body.length > 150 && !expanded ? body.slice(0, 150) + "…" : body;

  return (
    <article
      className="glass-card flex flex-col h-full cursor-pointer"
      onClick={() => setExpanded(!expanded)}
      id={`article-${article.id || article._id}`}
    >
      {/* Top accent bar */}
      <div
        className={`h-1 w-full rounded-t-2xl ${
          cat === "politics"
            ? "bg-gradient-to-r from-red-500 to-rose-400"
            : cat === "sports"
            ? "bg-gradient-to-r from-emerald-500 to-teal-400"
            : cat === "entertainment"
            ? "bg-gradient-to-r from-purple-500 to-fuchsia-400"
            : cat === "local"
            ? "bg-gradient-to-r from-cyan-500 to-sky-400"
            : cat === "jobs"
            ? "bg-gradient-to-r from-amber-500 to-yellow-400"
            : "bg-gradient-to-r from-brand-500 to-brand-400"
        }`}
      />

      <div className="flex flex-col flex-1 p-5 pt-4 space-y-3">
        {/* Badge + time */}
        <div className="flex items-center justify-between">
          <span className={`badge ${BADGE_STYLES[cat] || ""}`}>
            {CATEGORY_ICONS[cat] || "📄"}{" "}
            {cat}
          </span>
          <time className="text-xs text-white/30 tabular-nums">
            {timeAgo(published)}
          </time>
        </div>

        {/* Title */}
        <h2 className="text-base font-semibold leading-snug text-white/90 line-clamp-3">
          {title}
        </h2>

        {/* Body preview */}
        <p className="text-sm leading-relaxed text-white/50 flex-1">
          {preview}
        </p>

        {/* Read more hint */}
        {body.length > 150 && (
          <span className="text-xs font-medium text-brand-400 hover:text-brand-300 transition-colors">
            {expanded
              ? lang === "hi"
                ? "▲ कम पढ़ें"
                : lang === "mr"
                ? "▲ कमी वाचा"
                : "▲ Read less"
              : lang === "hi"
              ? "▼ और पढ़ें"
              : lang === "mr"
              ? "▼ अधिक वाचा"
              : "▼ Read more"}
          </span>
        )}
      </div>
    </article>
  );
}
