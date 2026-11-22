import React, { useState, useEffect, useRef } from "react";
import defaultProfileImg from "../assets/profile.jpg";

const DEFAULT_SOCIALS = [
  {
    name: "GitHub",
    href: "https://github.com/oOo-SaMRaT-oOo",
    icon: (
      <svg className="w-4 h-4 fill-current" viewBox="0 0 24 24">
        <path d="M12 .297c-6.63 0-12 5.373-12 12 0 5.303 3.438 9.8 8.205 11.385.6.113.82-.258.82-.577 0-.285-.01-1.04-.015-2.04-3.338.724-4.042-1.61-4.042-1.61C4.422 18.07 3.633 17.7 3.633 17.7c-1.087-.744.084-.729.084-.729 1.205.084 1.838 1.236 1.838 1.236 1.07 1.835 2.809 1.305 3.495.998.108-.776.417-1.305.76-1.605-2.665-.3-5.466-1.332-5.466-5.93 0-1.31.465-2.38 1.235-3.22-.135-.303-.54-1.523.105-3.176 0 0 1.005-.322 3.3 1.23.96-.267 1.98-.399 3-.405 1.02.006 2.04.138 3 .405 2.28-1.552 3.285-1.23 3.285-1.23.645 1.653.24 2.873.12 3.176.765.84 1.23 1.91 1.23 3.22 0 4.61-2.805 5.625-5.475 5.92.42.36.81 1.096.81 2.22 0 1.606-.015 2.896-.015 3.286 0 .315.21.69.825.57C20.565 22.092 24 17.592 24 12.297c0-6.627-5.373-12-12-12" />
      </svg>
    ),
  },
  {
    name: "LinkedIn",
    href: "https://www.linkedin.com/in/samrat-malla-13a661364",
    icon: (
      <svg className="w-4 h-4 fill-current" viewBox="0 0 24 24">
        <path d="M19 3a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h14m-.5 15.5v-5.3a3.26 3.26 0 0 0-3.26-3.26c-.85 0-1.84.52-2.28 1.3v-1.11h-2.79v8.37h2.79v-4.93c0-.77.62-1.4 1.39-1.4a1.4 1.4 0 0 1 1.4 1.4v4.93h2.75M6.88 8.56a1.68 1.68 0 0 0 1.68-1.68c0-.93-.75-1.69-1.68-1.69a1.69 1.69 0 0 0-1.69 1.69c0 .93.76 1.68 1.69 1.68m1.39 9.94v-8.37H5.5v8.37h2.77z" />
      </svg>
    ),
  },
  {
    name: "YouTube",
    href: "https://www.youtube.com/@TheElectroCoder",
    icon: (
      <svg className="w-4 h-4 fill-current" viewBox="0 0 24 24">
        <path d="M23.498 6.186a3.016 3.016 0 0 0-2.122-2.136C19.505 3.545 12 3.545 12 3.545s-7.505 0-9.377.505A3.017 3.017 0 0 0 .502 6.186C0 8.07 0 12 0 12s0 3.93.502 5.814a3.016 3.016 0 0 0 2.122 2.136c1.871.505 9.376.505 9.376.505s7.505 0 9.377-.505a3.015 3.015 0 0 0 2.122-2.136C24 15.93 24 12 24 12s0-3.93-.502-5.814zM9.545 15.568V8.432L15.818 12l-6.273 3.568z" />
      </svg>
    ),
  },
];

export default function Footer({
  theme = "dark",
  heading = "Meet SaMRaT ...",
  subtext = "Creating practical technology with thoughtful engineering.",
  status = "Currently a Student",
  ctaLabel = "Get in Touch",
  modalHeading = "Let's Connect ...",
  modalSubtext = "Always open to discussing interesting ideas.",
  portfolioLabel = "PORTFOLIO",
  portfolioHref = "https://heysammy.framer.wiki",
  email = "samratmalla2062@gmail.com",
  phone = "+977 9861194754",
  watermark = "SaMRaT",
  profileImage = defaultProfileImg,
  profileAlt = "SaMRaT",
  socials = DEFAULT_SOCIALS,
}) {
  const isDark = theme === "dark";

  // Two-step modal state for 200ms fade + scale(0.95 -> 1.00)
  const [isRendered, setIsRendered] = useState(false);
  const [isVisible, setIsVisible] = useState(false);

  // Bottom-right toast state
  const [copiedToast, setCopiedToast] = useState(false);
  const toastTimerRef = useRef(null);

  const openModal = () => {
    setIsRendered(true);
    requestAnimationFrame(() => {
      requestAnimationFrame(() => setIsVisible(true));
    });
  };

  const closeModal = () => {
    setIsVisible(false);
    setTimeout(() => {
      setIsRendered(false);
    }, 200);
  };

  useEffect(() => {
    if (!isRendered) return;

    const handleKeyDown = (e) => {
      if (e.key === "Escape") closeModal();
    };

    document.addEventListener("keydown", handleKeyDown);
    document.body.style.overflow = "hidden";

    return () => {
      document.removeEventListener("keydown", handleKeyDown);
      document.body.style.overflow = "";
    };
  }, [isRendered]);

  useEffect(() => {
    return () => {
      if (toastTimerRef.current) clearTimeout(toastTimerRef.current);
    };
  }, []);

  const handleCopyEmail = async () => {
    try {
      await navigator.clipboard.writeText(email);
    } catch {
      const input = document.createElement("input");
      input.value = email;
      document.body.appendChild(input);
      input.select();
      document.execCommand("copy");
      document.body.removeChild(input);
    }

    setCopiedToast(true);
    if (toastTimerRef.current) clearTimeout(toastTimerRef.current);
    toastTimerRef.current = setTimeout(() => {
      setCopiedToast(false);
    }, 2200);
  };

  const tooltipStyles = `pointer-events-none absolute -top-9 left-1/2 -translate-x-1/2 translate-y-1 opacity-0 delay-0 group-hover:delay-150 group-hover:translate-y-0 group-hover:opacity-100 rounded-md px-2.5 py-1 text-[11px] font-medium whitespace-nowrap transition-all duration-200 shadow-lg border ${
    isDark
      ? "bg-zinc-900 text-zinc-100 border-white/15"
      : "bg-zinc-900 text-white border-black/10"
  }`;

  return (
    <>
      <footer
        className={`overflow-hidden border-t pt-20 px-[6%] transition-colors ${
          isDark
            ? "bg-[#0b0b0c] text-white border-white/10"
            : "bg-[#f4f4f5] text-[#111111] border-black/10"
        }`}
      >
        {/* Self-contained clockwise border spin animation */}
        <style>{`
          @keyframes samrat-clockwise-spin {
            from { transform: rotate(0deg); }
            to { transform: rotate(360deg); }
          }
          .samrat-glow-beam {
            animation: samrat-clockwise-spin 3.2s linear infinite;
          }
        `}</style>

        {/* Top 3-Column Grid */}
        <div className="max-w-6xl mx-auto grid grid-cols-1 md:grid-cols-12 items-center gap-12">
          {/* Left CTA & Contact Column */}
          <div className="md:col-span-6 max-w-lg">
            <h2 className="text-3xl sm:text-5xl font-semibold tracking-tight leading-tight mb-3">
              {heading}
            </h2>
            <p
              className={`text-base leading-relaxed mb-7 ${
                isDark ? "text-zinc-400" : "text-zinc-600"
              }`}
            >
              {subtext}
            </p>

            {/* Button + Live Status */}
            <div className="flex flex-wrap items-center gap-5 mb-8">
              <button
                type="button"
                onClick={openModal}
                className={`px-7 py-3.5 rounded-md font-medium text-sm transition-transform hover:-translate-y-0.5 cursor-pointer ${
                  isDark
                    ? "bg-white text-black hover:bg-zinc-200"
                    : "bg-black text-white hover:bg-zinc-800"
                }`}
              >
                {ctaLabel}
              </button>

              {status && (
                <div className="inline-flex items-center gap-2.5 text-sm">
                  <span className="relative flex h-2.5 w-2.5">
                    <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75" />
                    <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-emerald-500 shadow-[0_0_12px_#10b981]" />
                  </span>
                  <span>{status}</span>
                </div>
              )}
            </div>

            {/* Social Pills */}
            <div className="flex items-center gap-3 mb-5">
              {socials.map((item) => (
                <a
                  key={item.name}
                  href={item.href}
                  target="_blank"
                  rel="noreferrer"
                  aria-label={item.name}
                  className={`w-9 h-9 rounded-full flex items-center justify-center transition-all hover:-translate-y-0.5 ${
                    isDark
                      ? "bg-zinc-900 text-white hover:bg-white hover:text-black"
                      : "bg-zinc-200 text-black hover:bg-black hover:text-white"
                  }`}
                >
                  {item.icon}
                </a>
              ))}
            </div>

            {/* Direct Contact: Floating Top Tooltip (150ms delay) + No Underline */}
            <div className="flex flex-col gap-1.5 text-sm">
              <button
                type="button"
                onClick={handleCopyEmail}
                className="group relative inline-flex items-center gap-2 opacity-85 hover:opacity-100 transition-colors w-fit cursor-pointer text-left"
              >
                <span>{email}</span>
                <span className={tooltipStyles}>
                  Click to copy
                  <span className="absolute left-1/2 -bottom-1 -translate-x-1/2 w-2 h-2 rotate-45 bg-zinc-900 border-r border-b border-white/15" />
                </span>
              </button>

              <a
                href={`tel:${phone.replace(/\s+/g, "")}`}
                className="group relative inline-flex items-center gap-2 opacity-85 hover:opacity-100 transition-colors w-fit cursor-pointer"
              >
                <span>{phone}</span>
                <span className={tooltipStyles}>
                  Click to call
                  <span className="absolute left-1/2 -bottom-1 -translate-x-1/2 w-2 h-2 rotate-45 bg-zinc-900 border-r border-b border-white/15" />
                </span>
              </a>
            </div>
          </div>

          {/* Center-Left Circular Profile Picture + Clockwise Glowing Portfolio Button */}
          <div className="md:col-span-4 flex flex-col items-center justify-center shrink-0">
            <div
              className={`w-44 h-44 sm:w-52 sm:h-52 rounded-full overflow-hidden border-2 p-1.5 ${
                isDark
                  ? "bg-zinc-900/60 border-white/15 shadow-2xl"
                  : "bg-white border-black/10 shadow-lg"
              }`}
            >
              <img
                src={profileImage}
                alt={profileAlt}
                className="w-full h-full rounded-full object-cover object-center"
              />
            </div>

            {/* Portfolio Pill Button with Clockwise Glowing Border */}
            <a
              href={portfolioHref}
              target="_blank"
              rel="noreferrer"
              className="group relative mt-6 inline-flex items-center justify-center rounded-full p-[1.5px] overflow-hidden transition-all duration-300 hover:scale-105 hover:-translate-y-0.5 hover:shadow-[0_0_24px_rgba(216,180,254,0.35)] active:scale-95"
            >
              <span
                aria-hidden="true"
                className="samrat-glow-beam absolute inset-[-180%] blur-sm opacity-80 group-hover:opacity-100 transition-opacity"
                style={{
                  background:
                    "conic-gradient(from 0deg, transparent 0deg, transparent 220deg, #a855f7 290deg, #f5d0fe 335deg, #ffffff 355deg, transparent 360deg)",
                }}
              />
              <span
                aria-hidden="true"
                className="samrat-glow-beam absolute inset-[-180%]"
                style={{
                  background:
                    "conic-gradient(from 0deg, transparent 0deg, transparent 230deg, #a855f7 295deg, #f5d0fe 338deg, #ffffff 356deg, transparent 360deg)",
                }}
              />
              <span
                className={`relative z-10 px-8 py-2.5 rounded-full text-xs font-medium tracking-[0.22em] uppercase transition-colors ${
                  isDark
                    ? "bg-[#0d0d0f] text-white group-hover:bg-[#131317]"
                    : "bg-white text-black group-hover:bg-zinc-50"
                }`}
              >
                {portfolioLabel}
              </span>
            </a>
          </div>

          {/* Right Column (Intentionally kept vacant for future content) */}
          <div className="hidden md:block md:col-span-2" aria-hidden="true" />
        </div>

        {/* Bottom Credits Bar */}
        <div
          className={`max-w-6xl mx-auto mt-16 pt-6 border-t flex flex-wrap justify-between gap-4 text-xs ${
            isDark
              ? "border-white/10 text-zinc-500"
              : "border-black/10 text-zinc-500"
          }`}
        >
          <span>Design &amp; Developed By SaMRaT</span>
          <span>Sehr Nett :)</span>
        </div>

        {/* Oversized Watermark */}
        <div
          aria-hidden="true"
          className={`text-center font-extrabold tracking-tighter leading-[0.82] select-none pointer-events-none mt-8 text-[clamp(4.5rem,17vw,15rem)] ${
            isDark ? "text-white/25" : "text-black/15"
          }`}
        >
          {watermark}
        </div>
      </footer>

      {/* Frosted Glass Contact Modal */}
      {isRendered && (
        <div
          role="dialog"
          aria-modal="true"
          aria-labelledby="connect-modal-title"
          onClick={closeModal}
          className={`fixed inset-0 z-50 flex items-center justify-center p-4 backdrop-blur-md transition-opacity duration-200 ease-out ${
            isDark ? "bg-black/65" : "bg-black/35"
          } ${isVisible ? "opacity-100" : "opacity-0"}`}
        >
          <div
            onClick={(e) => e.stopPropagation()}
            className={`w-full max-w-md rounded-2xl border p-7 sm:p-8 backdrop-blur-xl shadow-2xl transition-all duration-200 ease-out ${
              isDark
                ? "bg-zinc-900/75 border-white/15 text-white"
                : "bg-white/80 border-black/10 text-zinc-900"
            } ${isVisible ? "opacity-100 scale-100" : "opacity-0 scale-95"}`}
          >
            <h3
              id="connect-modal-title"
              className="text-2xl sm:text-3xl font-semibold tracking-tight mb-2.5"
            >
              {modalHeading}
            </h3>
            <p
              className={`text-sm leading-relaxed mb-6 ${
                isDark ? "text-zinc-300" : "text-zinc-600"
              }`}
            >
              {modalSubtext}
            </p>

            {/* Direct Contact Rows */}
            <div className="space-y-3 mb-6 text-sm">
              <button
                type="button"
                onClick={handleCopyEmail}
                className={`group relative flex items-center gap-3 w-fit opacity-85 hover:opacity-100 transition-colors cursor-pointer text-left ${
                  isDark ? "text-zinc-200" : "text-zinc-800"
                }`}
              >
                <svg
                  className="w-4 h-4 shrink-0 opacity-75"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="2"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                >
                  <rect width="20" height="16" x="2" y="4" rx="2" />
                  <path d="m22 7-8.97 5.7a1.94 1.94 0 0 1-2.06 0L2 7" />
                </svg>
                <span className="truncate">{email}</span>
                <span className={tooltipStyles}>
                  Click to copy
                  <span className="absolute left-1/2 -bottom-1 -translate-x-1/2 w-2 h-2 rotate-45 bg-zinc-900 border-r border-b border-white/15" />
                </span>
              </button>

              <a
                href={`tel:${phone.replace(/\s+/g, "")}`}
                className={`group relative flex items-center gap-3 w-fit opacity-85 hover:opacity-100 transition-colors cursor-pointer ${
                  isDark ? "text-zinc-200" : "text-zinc-800"
                }`}
              >
                <svg
                  className="w-4 h-4 shrink-0 opacity-75"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="2"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                >
                  <path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z" />
                </svg>
                <span>{phone}</span>
                <span className={tooltipStyles}>
                  Click to call
                  <span className="absolute left-1/2 -bottom-1 -translate-x-1/2 w-2 h-2 rotate-45 bg-zinc-900 border-r border-b border-white/15" />
                </span>
              </a>
            </div>

            {/* Social Links List */}
            <div
              className={`border-t border-b py-4 mb-6 space-y-2.5 ${
                isDark ? "border-white/10" : "border-black/10"
              }`}
            >
              {socials.map((item) => (
                <a
                  key={item.name}
                  href={item.href}
                  target="_blank"
                  rel="noreferrer"
                  className={`group flex items-center justify-between text-sm py-1 transition-colors ${
                    isDark
                      ? "text-zinc-300 hover:text-white"
                      : "text-zinc-700 hover:text-black"
                  }`}
                >
                  <span className="flex items-center gap-3">
                    <span
                      className={`w-6 h-6 rounded-full flex items-center justify-center ${
                        isDark ? "bg-white/10" : "bg-black/5"
                      }`}
                    >
                      {item.icon}
                    </span>
                    <span className="font-medium">{item.name}</span>
                  </span>
                  <span className="text-xs opacity-40 group-hover:opacity-100 group-hover:translate-x-0.5 transition-all">
                    ↗
                  </span>
                </a>
              ))}
            </div>

            {/* Bottom Action Buttons */}
            <div className="flex items-center gap-3">
              <button
                type="button"
                onClick={handleCopyEmail}
                className={`flex-1 py-2.5 px-4 rounded-lg text-sm font-medium transition-colors cursor-pointer ${
                  isDark
                    ? "bg-white text-black hover:bg-zinc-200"
                    : "bg-black text-white hover:bg-zinc-800"
                }`}
              >
                Copy Email
              </button>

              <button
                type="button"
                onClick={closeModal}
                className={`flex-1 py-2.5 px-4 rounded-lg text-sm font-medium border transition-colors cursor-pointer ${
                  isDark
                    ? "border-white/15 bg-white/5 text-white hover:bg-white/10"
                    : "border-black/15 bg-black/5 text-black hover:bg-black/10"
                }`}
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Bottom-Right Copy Toast */}
      <div
        role="status"
        aria-live="polite"
        className={`pointer-events-none fixed bottom-6 right-6 z-[60] flex items-center gap-2 rounded-lg border px-4 py-2.5 text-xs font-medium backdrop-blur-xl shadow-2xl transition-all duration-200 ${
          isDark
            ? "bg-zinc-900/90 border-white/15 text-white"
            : "bg-zinc-900/95 border-black/10 text-white"
        } ${
          copiedToast
            ? "opacity-100 translate-y-0 scale-100"
            : "opacity-0 translate-y-2 scale-95"
        }`}
      >
        <svg
          className="w-3.5 h-3.5 text-emerald-400 shrink-0"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth="2.5"
          strokeLinecap="round"
          strokeLinejoin="round"
        >
          <polyline points="20 6 9 17 4 12" />
        </svg>
        <span>Email copied</span>
      </div>
    </>
  );
}