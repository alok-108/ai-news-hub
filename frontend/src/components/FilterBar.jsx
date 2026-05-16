import React from "react";

const CATEGORIES = [
  { value: "all", hi: "सभी", en: "All", mr: "सर्व", icon: "🌐" },
  { value: "politics", hi: "राजनीति", en: "Politics", mr: "राजकारण", icon: "🏛️" },
  { value: "sports", hi: "खेल", en: "Sports", mr: "खेळ", icon: "🏏" },
  {
    value: "entertainment",
    hi: "मनोरंजन",
    en: "Entertainment",
    mr: "मनोरंजन",
    icon: "🎬",
  },
  { value: "local", hi: "लोकल", en: "Local", mr: "स्थानिक", icon: "📍" },
  { value: "jobs", hi: "नौकरी", en: "Jobs", mr: "नोकऱ्या", icon: "💼" },
];

const LANGUAGES = [
  { code: "hi", label: "हिन्दी", flag: "🇮🇳" },
  { code: "en", label: "English", flag: "🇬🇧" },
  { code: "mr", label: "मराठी", flag: "🇮🇳" },
];

export default function FilterBar({ category, setCategory, lang, setLang }) {
  return (
    <div className="mt-6 space-y-4 sm:space-y-0 sm:flex sm:items-center sm:justify-between sm:gap-4">
      {/* ── Category Pills ── */}
      <div className="flex flex-wrap gap-2" id="category-filter">
        {CATEGORIES.map((cat) => {
          const active = category === cat.value;
          return (
            <button
              key={cat.value}
              id={`cat-${cat.value}`}
              onClick={() => setCategory(cat.value)}
              className={`
                flex items-center gap-1.5 px-3.5 py-2 rounded-xl text-sm font-medium
                border transition-all duration-200
                ${
                  active
                    ? "bg-brand-600/80 border-brand-500/50 text-white shadow-md shadow-brand-600/20"
                    : "bg-white/5 border-white/10 text-white/60 hover:bg-white/10 hover:border-white/20 hover:text-white/80"
                }
              `}
            >
              <span className="text-base">{cat.icon}</span>
              <span>{cat[lang] || cat.en}</span>
            </button>
          );
        })}
      </div>

      {/* ── Language Toggle ── */}
      <div className="flex items-center gap-1.5 p-1 rounded-xl bg-white/5 border border-white/10" id="lang-toggle">
        {LANGUAGES.map((l) => (
          <button
            key={l.code}
            id={`lang-${l.code}`}
            onClick={() => setLang(l.code)}
            className={`lang-chip ${lang === l.code ? "lang-chip-active" : ""}`}
          >
            <span className="mr-1">{l.flag}</span>
            {l.label}
          </button>
        ))}
      </div>
    </div>
  );
}
