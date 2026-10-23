import React, { useEffect, useState } from "react";

const bootSteps = [
  "Initializing Physics Engine...",
  "Loading Random Forest Model...",
  "Building Stability Atlas...",
  "Launching Dashboard..."
];

// Configuration
const DURATION_PER_STEP_MS = 600; // Total run time
const END_HOLD_PAUSE_MS = 300;    // Pause at 100% completion before redirection

export default function BootScreen({ onFinish }) {
  // Start at -1 so no step shows as checked initially
  const [activeStep, setActiveStep] = useState(-1);
  const [progress, setProgress] = useState(0);

  useEffect(() => {
    const totalBootDuration = DURATION_PER_STEP_MS * bootSteps.length;
    const intervalTickMs = 20;
    let elapsedTime = 0;

    const timer = setInterval(() => {
      elapsedTime += intervalTickMs;

      const rawProgress = Math.min(100, Math.floor((elapsedTime / totalBootDuration) * 100));
      setProgress(rawProgress);

      // Calculates step index: stays at -1 for a brief fraction, then hits 0, 1, 2, 3 in front of user
      const currentStepIdx = Math.min(
        bootSteps.length - 1,
        Math.floor((elapsedTime - 100) / DURATION_PER_STEP_MS)
      );
      setActiveStep(currentStepIdx);

      if (elapsedTime >= totalBootDuration) {
        clearInterval(timer);
        setActiveStep(bootSteps.length - 1); // Ensure all items are checked at 100%

        setTimeout(() => {
          if (onFinish) onFinish();
        }, END_HOLD_PAUSE_MS);
      }
    }, intervalTickMs);

    return () => clearInterval(timer);
  }, [onFinish]);

  return (
    <>
      <style>{`
        .boot-screen {
          position: fixed;
          inset: 0;
          background: #020617;
          display: flex;
          justify-content: center;
          align-items: center;
          z-index: 99999;
          animation: fadeIn 0.4s ease-out;
          font-family: monospace;
        }

        .boot-card {
          width: min(700px, 90vw);
          color: white;
        }

        .boot-title {
          font-size: clamp(40px, 5vw, 72px);
          font-weight: 900;
          letter-spacing: 4px;
          text-transform: uppercase;
          background: linear-gradient(
            90deg,
            #00f0ff,
            #38b6ff,
            white,
            #38b6ff,
            #00f0ff
          );
          background-size: 200% auto;
          -webkit-background-clip: text;
          -webkit-text-fill-color: transparent;
          animation: shine 5s linear infinite;
          text-align: center;
        }

        .subtitle {
          color: #94a3b8;
          text-align: center;
          margin-top: 10px;
          letter-spacing: 2px;
          text-transform: uppercase;
        }

        .divider {
          height: 2px;
          margin: 40px 0;
          border-radius: 999px;
          background: linear-gradient(
            90deg,
            transparent,
            #00f0ff,
            white,
            #00f0ff,
            transparent
          );
          box-shadow:
            0 0 12px #00f0ff,
            0 0 30px rgba(0, 240, 255, 0.5);
        }

        .step {
          margin: 16px 0;
          color: #7dd3fc;
          font-size: 18px;
          opacity: 0.35;
          transition:
          opacity .25s ease,
          color .25s ease,
          text-shadow .25s ease;
        }

        .active {
          opacity: 1;
          color: white;
          text-shadow:
            0 0 8px #00f0ff,
            0 0 20px #00f0ff;
        }

        .progress {
          margin-top: 45px;
          width: 100%;
          height: 10px;
          border-radius: 999px;
          overflow: hidden;
          background: #0f172a;
          border: 1px solid #1e293b;
        }

        .progress-fill {
          height: 100%;
          transition: width 0.04s linear;
          background: linear-gradient(
            90deg,
            #00f0ff,
            white,
            #38b6ff
          );
          box-shadow:
            0 0 15px #00f0ff,
            0 0 30px #0072ff;
        }

        .percent {
          text-align: right;
          margin-top: 12px;
          color: #38bdf8;
          font-weight: bold;
        }

        @keyframes shine {
          to {
            background-position: 200%;
          }
        }

        @keyframes fadeIn {
          from { opacity: 0; }
          to { opacity: 1; }
        }
      `}</style>

      <div className="boot-screen">
        <div className="boot-card">
          <div className="boot-title">StabilityAtlas</div>
          <div className="subtitle">AI-Powered Grid Stability Intelligence</div>
          <div className="divider" />

          {bootSteps.map((item, index) => {
            const isCompleted = index <= activeStep;
            return (
              <div
                key={index}
                className={`step ${isCompleted ? "active" : ""}`}
              >
                {isCompleted ? "✔ " : "   "}
                {item}
              </div>
            );
          })}

          <div className="progress">
            <div className="progress-fill" style={{ width: `${progress}%` }} />
          </div>

          <div className="percent">{progress}%</div>
        </div>
      </div>
    </>
  );
}
