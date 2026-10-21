import React from 'react';

export function Header_text({ text, fontSize = "clamp(32px, 5vw, 56px)" }) {
  return (
    <div className="relative w-full text-center py-2">
      <style>{`
        .cyber-title {
          position: relative;
          font-size: ${fontSize} !important; 
          font-weight: 800;
          line-height: 1.1;
          margin: 0;
          letter-spacing: 2px;
          text-transform: uppercase;
          display: inline-block;
          
          /* High-Contrast Cyber Matrix Gradient */
          background: linear-gradient(90deg, #00f0ff, #38b6ff, #ffffff, #38b6ff, #00f0ff);
          background-size: 200% auto;
          -webkit-background-clip: text;
          -webkit-text-fill-color: transparent;
          
          /* Glow Core */
          filter: drop-shadow(0 0 8px rgba(0, 240, 255, 0.6)) 
                  drop-shadow(0 0 20px rgba(0, 114, 255, 0.4));
          
          animation: 
              cyberBoot 1.2s cubic-bezier(0.15, 0.85, 0.45, 1) forwards,
              laserSurge 5s linear infinite,
              electricShock 4s linear infinite; 
        }

        /* Lightning Shock Sparks */
        .cyber-title::before, .cyber-title::after {
          content: "⚡";
          position: absolute;
          top: 50%;
          transform: translateY(-50%) scale(0);
          font-size: 0.8em;
          opacity: 0;
          filter: drop-shadow(0 0 10px #ffea00) drop-shadow(0 0 20px #ff9900);
          pointer-events: none;
          transition: all 0.1s ease;
          animation: lightningBurst 4s linear infinite;
        }
        
        .cyber-title::before { left: -40px; }
        .cyber-title::after { right: -40px; }

        @keyframes cyberBoot {
          0% { opacity: 0; transform: translateY(-20px) scale(0.95); filter: blur(5px); }
          100% { opacity: 1; transform: translateY(0) scale(1); filter: blur(0); }
        }

        @keyframes laserSurge {
          to { background-position: 200% center; }
        }

        @keyframes electricShock {
          0%, 90%, 94%, 98%, 100% {
            transform: skew(0deg) scale(1);
            filter: drop-shadow(0 0 8px rgba(0, 240, 255, 0.7)) drop-shadow(0 0 20px rgba(0, 114, 255, 0.4));
            -webkit-text-fill-color: transparent;
            opacity: 1;
          }
          91% {
            transform: skew(4deg) translateX(-2px);
            filter: drop-shadow(-3px 0 #ffffff) drop-shadow(0 0 25px #00f0ff) drop-shadow(0 0 50px #0072ff);
            -webkit-text-fill-color: #ffffff; 
            opacity: 1;
          }
          92% {
            transform: skew(-6deg) translateX(3px);
            filter: drop-shadow(3px 0 #00f0ff) drop-shadow(0 0 35px #00f0ff);
            -webkit-text-fill-color: transparent;
            opacity: 0.95;
          }
          93% { opacity: 0.85; transform: skew(0deg); }
          95% { transform: skew(8deg) scaleY(1.05); opacity: 1; }
          96% { opacity: 0.90; transform: skew(-1deg); }
        }

        @keyframes lightningBurst {
          0%, 90%, 97%, 100% { transform: translateY(-50%) scale(0); opacity: 0; }
          91% { transform: translateY(-50%) scale(1.3) rotate(-10deg); opacity: 1; }
          93% { transform: translateY(-52%) scale(1.1) rotate(15deg); opacity: 0.9; }
          95% { transform: translateY(-48%) scale(1.4) rotate(-5deg); opacity: 1; }
        }
      `}</style>

      <h1 className="cyber-title font-sans">
        {text}
      </h1>
    </div>
  );
}


export function GlowingLine({ colorVibe = "nominal" }) {
  let primaryColor, secondaryColor, glowColor, farGlow;

  if (colorVibe === "warning") {
    primaryColor = "#ff9900";
    secondaryColor = "#ff5500";
    glowColor = "rgba(255, 153, 0, 0.6)";
    farGlow = "rgba(255, 85, 0, 0.3)";
  } else if (colorVibe === "critical") {
    primaryColor = "#ff0055";
    secondaryColor = "#990033";
    glowColor = "rgba(255, 0, 85, 0.7)";
    farGlow = "rgba(153, 0, 51, 0.4)";
  } else {
    // Nominal state (cyan/blue)
    primaryColor = "#00f0ff";
    secondaryColor = "#0072ff";
    glowColor = "rgba(0, 240, 255, 0.6)";
    farGlow = "rgba(0, 114, 255, 0.3)";
  }

  return (
    <div className="w-full flex justify-center items-center py-2.5">
      <style>{`
        .laser-line-${colorVibe} {
          height: 2px;
          width: 100%;
          border-radius: 99px;
          
          background: linear-gradient(90deg, 
            transparent 0%, 
            ${primaryColor} 15%, 
            #ffffff 50%, 
            ${secondaryColor} 85%, 
            transparent 100%
          );
          background-size: 200% auto;
          
          box-shadow: 
            0 0 6px #ffffff,
            0 0 12px ${glowColor},
            0 0 25px ${farGlow};
            
          animation: currentFlow 4s linear infinite;
        }

        @keyframes currentFlow {
          0% { background-position: 0% center; }
          100% { background-position: 200% center; }
        }
      `}</style>

      <div className={`laser-line-${colorVibe}`} />
    </div>
  );
}


export function GlowingLineSub() {
  return (
    <div className="w-full flex justify-start my-1 mb-3">
      <style>{`
        .laser-sub-line {
          height: 1px;
          width: 0%;
          background: linear-gradient(90deg, #00f0ff, rgba(0, 240, 255, 0.3) 60%, transparent 100%);
          box-shadow: 0 0 8px rgba(0, 240, 255, 0.8);
          animation: subScannerDeploy 1.4s cubic-bezier(0.2, 0.8, 0.2, 1) forwards;
        }

        @keyframes subScannerDeploy {
          to { width: 45%; }
        }
      `}</style>

      <div className="laser-sub-line" />
    </div>
  );
}


export function FooterSignature({
  name = "Samrat Malla",
  title = "Electrical Engineering Student",
}) {
  return (
    <footer className="w-full mt-12 mb-6 flex justify-center font-mono select-none">
      <style>{`
        .signature-card{
          position:relative;
          overflow:hidden;
          transition:all .35s ease;
          cursor:pointer;
          text-decoration:none;
        }

        .signature-card::before{
          content:"";
          position:absolute;
          left:0;
          top:0;
          width:100%;
          height:2px;
          background:linear-gradient(
            90deg,
            transparent,
            #00f0ff,
            #ffffff,
            #00f0ff,
            transparent
          );
          box-shadow:
            0 0 12px #00f0ff,
            0 0 28px rgba(0,240,255,.5);
        }

        .signature-card:hover{
          transform:translateY(-2px);
          box-shadow:
            0 0 20px rgba(0,240,255,.12),
            0 0 45px rgba(0,114,255,.10);
        }

        .author-name{
          color:white;
          letter-spacing:.18em;
          text-shadow:
            0 0 8px rgba(0,240,255,.8),
            0 0 18px rgba(0,240,255,.45);
          transition:all .35s ease;
        }

        .signature-card:hover .author-name{
          letter-spacing:.28em;
          text-shadow:
            0 0 12px white,
            0 0 24px #00f0ff,
            0 0 42px #0072ff;
        }

        .pulse-dot{
          box-shadow:0 0 12px #00f0ff;
        }

        .portfolio-hint{
          position:absolute;
          bottom:8px;
          right:14px;
          font-size:10px;
          letter-spacing:.15em;
          color:#22d3ee;
          opacity:0;
          transform:translateY(6px);
          transition:all .25s ease;
          pointer-events:none;
          text-transform:uppercase;
        }

        .signature-card:hover .portfolio-hint{
          opacity:1;
          transform:translateY(0);
        }
      `}</style>

      <a
        href="https://heysammy.framer.wiki"
        target="_blank"
        rel="noopener noreferrer"
        className="
          signature-card
          bg-slate-950/90
          border border-slate-800
          rounded-2xl
          px-10
          py-5
          flex
          items-center
          gap-5
        "
      >
        {/* Status Dot */}
        <span className="relative flex h-3 w-3">
          <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-cyan-400 opacity-75"></span>
          <span className="pulse-dot relative inline-flex h-3 w-3 rounded-full bg-cyan-400"></span>
        </span>

        {/* Left Label */}
        <div className="text-right">
          <p className="text-[11px] tracking-[0.35em] text-slate-500 uppercase">
            Engineered By
          </p>

          <h3 className="author-name text-2xl font-black uppercase">
            {name}
          </h3>

          <p className="text-cyan-400 text-sm mt-1 tracking-wide">
            {title}
          </p>
        </div>

        {/* Divider */}
        <div className="h-12 w-px bg-slate-700"></div>

        {/* Build Info */}
        <div className="text-xs leading-6">
          <div className="text-slate-400">
            Project :
            <span className="text-white ml-2">
              StabilityAtlas
            </span>
          </div>

          <div className="text-slate-400">
            Stack :
            <span className="text-cyan-400 ml-2">
              React • FastAPI • Python
            </span>
          </div>

          <div className="text-slate-400">
            Version :
            <span className="text-emerald-400 ml-2">
              v1.0
            </span>
          </div>
        </div>

        {/* Hover Hint */}
        <span className="portfolio-hint">
          ↗ Click to visit portfolio
        </span>

      </a>
    </footer>
  );
}
