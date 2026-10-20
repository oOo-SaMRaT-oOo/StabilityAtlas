import React from "react";
import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  ReferenceLine,
} from "recharts";
import { Activity } from "lucide-react";

export default function FrequencyChart({
  nadirHz = 50.0,
  rocof = 0.0,
}) {
  // Generate a synthetic transient frequency response
  const generateTrajectoryData = () => {
    const data = [];

    // Nepal / European Grid Nominal Frequency
    const nominal = 50.0;

    // Frequency drop from nominal
    const dropDepth = nominal - nadirHz;

    // Larger RoCoF -> steeper transient
    const recoverySpeed = Math.max(0.8, 3.0 - rocof * 0.5);

    for (let t = 0; t <= 5.0; t += 0.2) {
      const freqDelta =
        dropDepth *
        Math.exp(-recoverySpeed * t) *
        Math.cos(2.5 * t);

      const currentFreq = nominal - freqDelta;

      data.push({
        time: `${t.toFixed(1)}s`,
        frequency: parseFloat(currentFreq.toFixed(3)),
      });
    }

    return data;
  };

  const chartData = generateTrajectoryData();

  // Nepal under-frequency threshold
  const isCritical = nadirHz < 49.5;

  return (
    <div className="bg-slate-950 p-4 rounded-lg border border-slate-800 mt-3">

      {/* Header */}
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <Activity
            size={16}
            className={
              isCritical ? "text-rose-400" : "text-cyan-400"
            }
          />

          <span className="text-xs font-semibold uppercase tracking-wider text-slate-300">
            Transient Frequency Trajectory
          </span>
        </div>

        {/* Legend */}
        <div className="flex items-center gap-3 text-[10px] font-mono">
          <span className="flex items-center gap-1 text-slate-400">
            <span className="w-2 h-0.5 bg-cyan-400 inline-block"></span>
            Frequency
          </span>

          <span className="flex items-center gap-1 text-rose-500">
            <span className="w-2 h-0.5 bg-rose-500 inline-block"></span>
            Trip Limit (49.5 Hz)
          </span>
        </div>
      </div>

      {/* Chart */}
      <div className="h-36 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart
            data={chartData}
            margin={{
              top: 10,
              right: 20,
              left: 0,
              bottom: 5,
            }}
          >
            <XAxis
              dataKey="time"
              stroke="#64748b"
              tickLine={false}
              fontSize={10}
            />

            <YAxis
              domain={[48.5, 50.2]}
              stroke="#64748b"
              tickLine={false}
              fontSize={10}
            />

            <Tooltip
              contentStyle={{
                backgroundColor: "#0f172a",
                borderColor: "#334155",
                borderRadius: "6px",
                color: "#38b6ff",
                fontSize: "11px",
                fontFamily: "monospace",
              }}
              itemStyle={{
                color: "#94a3b8",
              }}
              labelStyle={{
                color: "#ffffff",
              }}
            />

            {/* Under-frequency protection limit */}
            <ReferenceLine
              y={49.5}
              stroke="#f43f5e"
              strokeDasharray="3 3"
            />

            <Line
              type="monotone"
              dataKey="frequency"
              stroke={isCritical ? "#f43f5e" : "#00f0ff"}
              strokeWidth={2}
              dot={false}
              activeDot={{
                r: 4,
                fill: "#ffffff",
                stroke: isCritical ? "#f43f5e" : "#00f0ff",
              }}
            />
            
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>

  );
}