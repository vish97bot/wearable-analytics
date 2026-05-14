import { useState, useEffect, useRef, useCallback } from "react";
import { LineChart, Line, AreaChart, Area, BarChart, Bar, RadarChart, Radar, PolarGrid, PolarAngleAxis, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, ReferenceLine } from "recharts";

// ── SAMPLE DATA ────────────────────────────────────────────────────────────────
const generateWeekData = () => {
  const days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"];
  return days.map((day, i) => ({
    day,
    hrv: 42 + Math.round(Math.sin(i * 0.8) * 12 + Math.random() * 8),
    sleep: +(6.2 + Math.sin(i * 0.6) * 1.1 + Math.random() * 0.5).toFixed(1),
    deepSleep: +(1.1 + Math.random() * 0.6).toFixed(1),
    remSleep: +(1.4 + Math.random() * 0.7).toFixed(1),
    steps: Math.round(7200 + Math.random() * 5000),
    calories: Math.round(420 + Math.random() * 280),
    readiness: Math.round(62 + Math.sin(i * 0.9) * 15 + Math.random() * 10),
    rhr: Math.round(52 + Math.random() * 8),
    spo2: +(97.1 + Math.random() * 1.8).toFixed(1),
    stress: Math.round(28 + Math.random() * 35),
    activeMinutes: Math.round(35 + Math.random() * 55),
  }));
};

const generate30Days = () => {
  return Array.from({ length: 30 }, (_, i) => {
    const d = new Date(); d.setDate(d.getDate() - (29 - i));
    return {
      date: d.toLocaleDateString("en", { month: "short", day: "numeric" }),
      hrv: 38 + Math.round(Math.sin(i * 0.4) * 14 + Math.random() * 10),
      readiness: Math.round(58 + Math.sin(i * 0.3) * 18 + Math.random() * 12),
      sleep: +(6.0 + Math.sin(i * 0.5) * 1.3 + Math.random() * 0.6).toFixed(1),
    };
  });
};

const workouts = [
  { id: 1, name: "Morning Run", type: "run", date: "Today", duration: "42 min", distance: "6.2 km", hr: 158, calories: 387, load: 78 },
  { id: 2, name: "Weight Training", type: "strength", date: "Yesterday", duration: "58 min", distance: null, hr: 134, calories: 312, load: 64 },
  { id: 3, name: "HIIT Session", type: "hiit", date: "2d ago", duration: "28 min", distance: null, hr: 174, calories: 298, load: 92 },
  { id: 4, name: "Evening Walk", type: "walk", date: "3d ago", duration: "35 min", distance: "3.1 km", hr: 98, calories: 142, load: 22 },
  { id: 5, name: "Cycling", type: "cycle", date: "4d ago", duration: "68 min", distance: "24.3 km", hr: 148, calories: 524, load: 85 },
];

const sleepStages = [
  { stage: "Awake", duration: 18, color: "#e74c3c" },
  { stage: "Light", duration: 142, color: "#3498db" },
  { stage: "Deep", duration: 74, color: "#8b5cf6" },
  { stage: "REM", duration: 98, color: "#06b6d4" },
];

const weekData = generateWeekData();
const monthData = generate30Days();

// ── ICONS ──────────────────────────────────────────────────────────────────────
const Icon = ({ name, size = 16 }) => {
  const icons = {
    heart: <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"/></svg>,
    activity: <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/></svg>,
    moon: <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></svg>,
    zap: <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg>,
    trending: <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><polyline points="23 6 13.5 15.5 8.5 10.5 1 18"/><polyline points="17 6 23 6 23 12"/></svg>,
    upload: <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><polyline points="16 16 12 12 8 16"/><line x1="12" y1="12" x2="12" y2="21"/><path d="M20.39 18.39A5 5 0 0 0 18 9h-1.26A8 8 0 1 0 3 16.3"/></svg>,
    run: <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><circle cx="13" cy="4" r="2"/><path d="m14.5 10.5-2 4.5-3.5 2-1.5 3"/><path d="m8.5 14.5 2-2 2-1 3-4"/></svg>,
    settings: <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><circle cx="12" cy="12" r="3"/><path d="M19.07 4.93a10 10 0 0 1 0 14.14M4.93 4.93a10 10 0 0 0 0 14.14"/></svg>,
    droplet: <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M12 2.69l5.66 5.66a8 8 0 1 1-11.31 0z"/></svg>,
    award: <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><circle cx="12" cy="8" r="7"/><polyline points="8.21 13.89 7 23 12 20 17 23 15.79 13.88"/></svg>,
    close: <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>,
  };
  return icons[name] || null;
};

// ── SCORE RING ─────────────────────────────────────────────────────────────────
const ScoreRing = ({ value, max = 100, size = 120, strokeWidth = 8, color, label, sublabel }) => {
  const r = (size - strokeWidth * 2) / 2;
  const circ = 2 * Math.PI * r;
  const pct = value / max;
  const dash = circ * pct;
  return (
    <div style={{ position: "relative", width: size, height: size, flexShrink: 0 }}>
      <svg width={size} height={size} style={{ transform: "rotate(-90deg)" }}>
        <circle cx={size/2} cy={size/2} r={r} fill="none" stroke="#1a1d24" strokeWidth={strokeWidth} />
        <circle cx={size/2} cy={size/2} r={r} fill="none" stroke={color} strokeWidth={strokeWidth}
          strokeDasharray={`${dash} ${circ}`} strokeLinecap="round"
          style={{ filter: `drop-shadow(0 0 6px ${color}88)`, transition: "stroke-dasharray 1s ease" }} />
      </svg>
      <div style={{ position: "absolute", inset: 0, display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center" }}>
        <span style={{ fontSize: size > 100 ? 28 : 20, fontWeight: 700, color: "#f0f0f0", fontFamily: "'DM Mono', monospace", lineHeight: 1 }}>{value}</span>
        {label && <span style={{ fontSize: 10, color: "#888", textTransform: "uppercase", letterSpacing: "0.08em", marginTop: 2 }}>{label}</span>}
        {sublabel && <span style={{ fontSize: 9, color: color, marginTop: 1 }}>{sublabel}</span>}
      </div>
    </div>
  );
};

// ── METRIC CARD ────────────────────────────────────────────────────────────────
const MetricCard = ({ label, value, unit, icon, color, trend, onClick, active }) => (
  <div onClick={onClick} style={{
    background: active ? `${color}12` : "#10121a",
    border: `1px solid ${active ? color : "#1e2130"}`,
    borderRadius: 12, padding: "16px 18px", cursor: "pointer",
    transition: "all 0.2s", position: "relative", overflow: "hidden",
  }}>
    <div style={{ position: "absolute", top: 0, right: 0, width: 80, height: 80,
      background: `radial-gradient(circle at top right, ${color}18, transparent 70%)` }} />
    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 10 }}>
      <span style={{ color: color, opacity: 0.85 }}><Icon name={icon} size={14} /></span>
      {trend !== undefined && (
        <span style={{ fontSize: 10, color: trend >= 0 ? "#22d3a5" : "#e74c3c", display: "flex", alignItems: "center", gap: 2 }}>
          {trend >= 0 ? "▲" : "▼"} {Math.abs(trend)}%
        </span>
      )}
    </div>
    <div style={{ fontSize: 24, fontWeight: 700, color: "#f0f0f0", fontFamily: "'DM Mono', monospace", lineHeight: 1 }}>
      {value}<span style={{ fontSize: 12, color: "#666", fontWeight: 400, marginLeft: 3 }}>{unit}</span>
    </div>
    <div style={{ fontSize: 11, color: "#666", marginTop: 4, textTransform: "uppercase", letterSpacing: "0.06em" }}>{label}</div>
  </div>
);

// ── UPLOAD MODAL ───────────────────────────────────────────────────────────────
const UploadModal = ({ onClose }) => {
  const [dragging, setDragging] = useState(false);
  const [files, setFiles] = useState([]);
  const [source, setSource] = useState("ultrahuman");

  const handleDrop = (e) => {
    e.preventDefault(); setDragging(false);
    const dropped = Array.from(e.dataTransfer.files);
    setFiles(prev => [...prev, ...dropped.map(f => ({ name: f.name, size: (f.size/1024).toFixed(0) + " KB", status: "ready" }))]);
  };

  return (
    <div style={{ position: "fixed", inset: 0, background: "rgba(0,0,0,0.85)", zIndex: 1000, display: "flex", alignItems: "center", justifyContent: "center", backdropFilter: "blur(4px)" }}>
      <div style={{ background: "#10121a", border: "1px solid #1e2130", borderRadius: 16, padding: 32, width: 500, maxWidth: "90vw" }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 24 }}>
          <h2 style={{ color: "#f0f0f0", fontSize: 18, fontWeight: 700, margin: 0 }}>Import Health Data</h2>
          <button onClick={onClose} style={{ background: "none", border: "none", color: "#666", cursor: "pointer" }}><Icon name="close" size={18} /></button>
        </div>

        <div style={{ display: "flex", gap: 8, marginBottom: 20 }}>
          {["ultrahuman", "zepp", "health_connect"].map(s => (
            <button key={s} onClick={() => setSource(s)} style={{
              flex: 1, padding: "8px 0", borderRadius: 8, fontSize: 11, fontWeight: 600,
              textTransform: "uppercase", letterSpacing: "0.06em", cursor: "pointer",
              background: source === s ? "#22d3a5" : "#1a1d24",
              border: `1px solid ${source === s ? "#22d3a5" : "#1e2130"}`,
              color: source === s ? "#000" : "#666", transition: "all 0.15s",
            }}>{s.replace("_", " ")}</button>
          ))}
        </div>

        <div style={{ fontSize: 11, color: "#555", marginBottom: 14, lineHeight: 1.6 }}>
          {source === "ultrahuman" && "Export from Ultrahuman app → Profile → Export Data → Select CSV/JSON"}
          {source === "zepp" && "Zepp app → Profile → My Data → Export → Download ZIP"}
          {source === "health_connect" && "Health Connect app → Data & Privacy → Export Data"}
        </div>

        <div onDragOver={e => { e.preventDefault(); setDragging(true); }}
          onDragLeave={() => setDragging(false)} onDrop={handleDrop}
          style={{ border: `2px dashed ${dragging ? "#22d3a5" : "#1e2130"}`, borderRadius: 12, padding: "32px 20px",
            textAlign: "center", background: dragging ? "#22d3a508" : "#0d0f18",
            transition: "all 0.2s", cursor: "pointer" }}>
          <div style={{ color: dragging ? "#22d3a5" : "#444", marginBottom: 8 }}><Icon name="upload" size={28} /></div>
          <div style={{ color: "#666", fontSize: 13 }}>Drop CSV or ZIP files here</div>
          <div style={{ color: "#444", fontSize: 11, marginTop: 4 }}>or click to browse</div>
        </div>

        {files.length > 0 && (
          <div style={{ marginTop: 16, display: "flex", flexDirection: "column", gap: 6 }}>
            {files.map((f, i) => (
              <div key={i} style={{ display: "flex", justifyContent: "space-between", background: "#1a1d24", borderRadius: 8, padding: "8px 12px" }}>
                <span style={{ fontSize: 12, color: "#ccc" }}>{f.name}</span>
                <span style={{ fontSize: 11, color: "#22d3a5" }}>{f.size} · Ready</span>
              </div>
            ))}
            <button style={{ marginTop: 8, background: "#22d3a5", color: "#000", border: "none", borderRadius: 8,
              padding: "10px 0", fontWeight: 700, fontSize: 13, cursor: "pointer", letterSpacing: "0.04em" }}>
              PROCESS & IMPORT
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

// ── CUSTOM TOOLTIP ─────────────────────────────────────────────────────────────
const CustomTooltip = ({ active, payload, label }) => {
  if (!active || !payload?.length) return null;
  return (
    <div style={{ background: "#10121a", border: "1px solid #1e2130", borderRadius: 8, padding: "10px 14px", fontSize: 12 }}>
      <div style={{ color: "#888", marginBottom: 6, textTransform: "uppercase", letterSpacing: "0.06em", fontSize: 10 }}>{label}</div>
      {payload.map((p, i) => (
        <div key={i} style={{ color: p.color, display: "flex", justifyContent: "space-between", gap: 16 }}>
          <span style={{ color: "#888" }}>{p.name}</span>
          <span style={{ fontWeight: 700, fontFamily: "monospace" }}>{p.value}</span>
        </div>
      ))}
    </div>
  );
};

// ── SLEEP BREAKDOWN ────────────────────────────────────────────────────────────
const SleepBreakdown = ({ data }) => {
  const total = data.reduce((s, d) => s + d.duration, 0);
  return (
    <div>
      <div style={{ display: "flex", height: 10, borderRadius: 5, overflow: "hidden", marginBottom: 16, gap: 2 }}>
        {data.map((s, i) => (
          <div key={i} style={{ flex: s.duration, background: s.color, borderRadius: 3,
            boxShadow: `0 0 8px ${s.color}66` }} />
        ))}
      </div>
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 10 }}>
        {data.map((s, i) => (
          <div key={i} style={{ display: "flex", alignItems: "center", gap: 8 }}>
            <div style={{ width: 8, height: 8, borderRadius: 2, background: s.color, flexShrink: 0,
              boxShadow: `0 0 6px ${s.color}88` }} />
            <div>
              <div style={{ fontSize: 11, color: "#f0f0f0", fontWeight: 600 }}>
                {Math.floor(s.duration/60)}h {s.duration%60}m
              </div>
              <div style={{ fontSize: 10, color: "#555" }}>{s.stage} · {Math.round(s.duration/total*100)}%</div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

// ── WORKOUT CARD ───────────────────────────────────────────────────────────────
const typeColors = { run: "#22d3a5", strength: "#8b5cf6", hiit: "#e74c3c", walk: "#3b82f6", cycle: "#f59e0b" };
const WorkoutCard = ({ w }) => (
  <div style={{ display: "flex", alignItems: "center", gap: 14, padding: "14px 0",
    borderBottom: "1px solid #1a1d24" }}>
    <div style={{ width: 40, height: 40, borderRadius: 10, background: `${typeColors[w.type]}18`,
      border: `1px solid ${typeColors[w.type]}44`, display: "flex", alignItems: "center", justifyContent: "center",
      color: typeColors[w.type], flexShrink: 0 }}>
      <Icon name="run" size={16} />
    </div>
    <div style={{ flex: 1 }}>
      <div style={{ fontSize: 13, fontWeight: 600, color: "#f0f0f0" }}>{w.name}</div>
      <div style={{ fontSize: 11, color: "#555", marginTop: 2 }}>{w.date} · {w.duration}{w.distance ? ` · ${w.distance}` : ""}</div>
    </div>
    <div style={{ textAlign: "right" }}>
      <div style={{ fontSize: 12, color: "#888" }}><span style={{ color: "#e74c3c", fontFamily: "monospace", fontWeight: 700 }}>{w.hr}</span> bpm</div>
      <div style={{ fontSize: 11, color: "#555", marginTop: 2 }}>Load <span style={{ color: typeColors[w.type], fontWeight: 700 }}>{w.load}</span></div>
    </div>
  </div>
);

// ── MAIN APP ───────────────────────────────────────────────────────────────────
export default function App() {
  const [tab, setTab] = useState("overview");
  const [range, setRange] = useState("7d");
  const [showUpload, setShowUpload] = useState(false);
  const [activeMetric, setActiveMetric] = useState("hrv");
  const [animIn, setAnimIn] = useState(false);

  useEffect(() => {
    const t = setTimeout(() => setAnimIn(true), 100);
    return () => clearTimeout(t);
  }, []);

  const data = range === "7d" ? weekData : monthData.slice(-14);
  const today = weekData[weekData.length - 1];

  const tabs = [
    { id: "overview", label: "Overview", icon: "zap" },
    { id: "recovery", label: "Recovery", icon: "heart" },
    { id: "sleep", label: "Sleep", icon: "moon" },
    { id: "activity", label: "Activity", icon: "activity" },
    { id: "trends", label: "Trends", icon: "trending" },
  ];

  const metricColors = {
    hrv: "#22d3a5", readiness: "#8b5cf6", sleep: "#3b82f6",
    rhr: "#e74c3c", steps: "#f59e0b", spo2: "#06b6d4",
  };

  return (
    <div style={{
      minHeight: "100vh", background: "#080a10",
      fontFamily: "'Syne', 'DM Sans', system-ui, sans-serif",
      color: "#f0f0f0",
      opacity: animIn ? 1 : 0, transform: animIn ? "none" : "translateY(8px)",
      transition: "opacity 0.5s ease, transform 0.5s ease",
    }}>
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Mono:wght@400;500&family=DM+Sans:wght@400;500;600&display=swap');
        * { box-sizing: border-box; margin: 0; padding: 0; }
        ::-webkit-scrollbar { width: 4px; } ::-webkit-scrollbar-track { background: #080a10; }
        ::-webkit-scrollbar-thumb { background: #1e2130; border-radius: 2px; }
        button { font-family: inherit; }
      `}</style>

      {showUpload && <UploadModal onClose={() => setShowUpload(false)} />}

      {/* HEADER */}
      <div style={{ padding: "20px 24px 0", display: "flex", justifyContent: "space-between", alignItems: "center",
        borderBottom: "1px solid #1a1d24", paddingBottom: 16 }}>
        <div style={{ display: "flex", alignItems: "baseline", gap: 10 }}>
          <span style={{ fontSize: 20, fontWeight: 800, letterSpacing: "-0.02em" }}>
            VITAL<span style={{ color: "#22d3a5" }}>OS</span>
          </span>
          <span style={{ fontSize: 10, color: "#444", letterSpacing: "0.12em", textTransform: "uppercase" }}>Health Intelligence</span>
        </div>
        <div style={{ display: "flex", gap: 8, alignItems: "center" }}>
          <div style={{ display: "flex", gap: 4, background: "#10121a", border: "1px solid #1e2130", borderRadius: 8, padding: 3 }}>
            {["7d", "14d", "30d"].map(r => (
              <button key={r} onClick={() => setRange(r)} style={{
                padding: "4px 10px", borderRadius: 6, fontSize: 11, fontWeight: 600,
                background: range === r ? "#22d3a5" : "transparent",
                color: range === r ? "#000" : "#555", border: "none", cursor: "pointer",
                transition: "all 0.15s", letterSpacing: "0.04em",
              }}>{r.toUpperCase()}</button>
            ))}
          </div>
          <button onClick={() => setShowUpload(true)} style={{
            display: "flex", alignItems: "center", gap: 6, padding: "7px 14px",
            background: "#10121a", border: "1px solid #1e2130", borderRadius: 8,
            color: "#22d3a5", fontSize: 12, fontWeight: 600, cursor: "pointer", letterSpacing: "0.04em",
            transition: "all 0.15s",
          }}>
            <Icon name="upload" size={13} /> IMPORT
          </button>
        </div>
      </div>

      {/* TABS */}
      <div style={{ display: "flex", gap: 0, padding: "0 24px", borderBottom: "1px solid #1a1d24", overflowX: "auto" }}>
        {tabs.map(t => (
          <button key={t.id} onClick={() => setTab(t.id)} style={{
            display: "flex", alignItems: "center", gap: 6, padding: "14px 18px",
            background: "none", border: "none", cursor: "pointer", fontSize: 12, fontWeight: 600,
            color: tab === t.id ? "#f0f0f0" : "#444", letterSpacing: "0.06em", textTransform: "uppercase",
            borderBottom: tab === t.id ? "2px solid #22d3a5" : "2px solid transparent",
            transition: "all 0.15s", whiteSpace: "nowrap",
          }}>
            <span style={{ color: tab === t.id ? "#22d3a5" : "#333" }}><Icon name={t.icon} size={13} /></span>
            {t.label}
          </button>
        ))}
      </div>

      {/* CONTENT */}
      <div style={{ padding: "20px 24px 40px", maxWidth: 1200 }}>

        {/* ── OVERVIEW ── */}
        {tab === "overview" && (
          <div style={{ display: "flex", flexDirection: "column", gap: 20 }}>
            {/* Top row: readiness + key metrics */}
            <div style={{ display: "grid", gridTemplateColumns: "280px 1fr", gap: 16 }}>
              {/* Readiness card */}
              <div style={{ background: "#10121a", border: "1px solid #1e2130", borderRadius: 14, padding: 24 }}>
                <div style={{ fontSize: 10, color: "#555", textTransform: "uppercase", letterSpacing: "0.1em", marginBottom: 16 }}>Today's Readiness</div>
                <div style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 16 }}>
                  <ScoreRing value={today.readiness} size={140} strokeWidth={10} color="#22d3a5" label="Readiness" sublabel={today.readiness >= 70 ? "Optimal" : today.readiness >= 50 ? "Good" : "Rest"} />
                  <div style={{ width: "100%", display: "flex", flexDirection: "column", gap: 8 }}>
                    {[
                      { label: "HRV", value: today.hrv, max: 80, color: "#22d3a5", unit: "ms" },
                      { label: "RHR", value: today.rhr, max: 70, color: "#e74c3c", unit: "bpm" },
                      { label: "SpO₂", value: today.spo2, max: 100, color: "#06b6d4", unit: "%" },
                    ].map(m => (
                      <div key={m.label}>
                        <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 4 }}>
                          <span style={{ fontSize: 10, color: "#555", textTransform: "uppercase", letterSpacing: "0.06em" }}>{m.label}</span>
                          <span style={{ fontSize: 12, color: "#f0f0f0", fontFamily: "DM Mono, monospace", fontWeight: 600 }}>{m.value}{m.unit}</span>
                        </div>
                        <div style={{ height: 3, background: "#1a1d24", borderRadius: 2, overflow: "hidden" }}>
                          <div style={{ height: "100%", width: `${(m.value/m.max)*100}%`, background: m.color,
                            borderRadius: 2, boxShadow: `0 0 8px ${m.color}88`, transition: "width 1s ease" }} />
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>

              {/* Metric grid */}
              <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: 10, alignContent: "start" }}>
                <MetricCard label="HRV" value={today.hrv} unit="ms" icon="heart" color="#22d3a5" trend={4} active={activeMetric === "hrv"} onClick={() => setActiveMetric("hrv")} />
                <MetricCard label="Sleep" value={today.sleep} unit="h" icon="moon" color="#3b82f6" trend={-2} active={activeMetric === "sleep"} onClick={() => setActiveMetric("sleep")} />
                <MetricCard label="Resting HR" value={today.rhr} unit="bpm" icon="heart" color="#e74c3c" trend={-3} active={activeMetric === "rhr"} onClick={() => setActiveMetric("rhr")} />
                <MetricCard label="Steps" value={today.steps.toLocaleString()} unit="" icon="activity" color="#f59e0b" trend={12} active={activeMetric === "steps"} onClick={() => setActiveMetric("steps")} />
                <MetricCard label="Active Min" value={today.activeMinutes} unit="min" icon="zap" color="#8b5cf6" trend={7} active={activeMetric === "activeMinutes"} onClick={() => setActiveMetric("activeMinutes")} />
                <MetricCard label="SpO₂" value={today.spo2} unit="%" icon="droplet" color="#06b6d4" trend={0} active={activeMetric === "spo2"} onClick={() => setActiveMetric("spo2")} />
              </div>
            </div>

            {/* Trend chart */}
            <div style={{ background: "#10121a", border: "1px solid #1e2130", borderRadius: 14, padding: 20 }}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 20 }}>
                <div>
                  <div style={{ fontSize: 13, fontWeight: 700, letterSpacing: "0.04em", textTransform: "uppercase" }}>{activeMetric.toUpperCase()} Trend</div>
                  <div style={{ fontSize: 11, color: "#555", marginTop: 2 }}>Select a metric above to explore</div>
                </div>
                <div style={{ display: "flex", gap: 4 }}>
                  {Object.entries(metricColors).map(([k, c]) => (
                    <button key={k} onClick={() => setActiveMetric(k)} style={{
                      padding: "4px 10px", borderRadius: 6, fontSize: 10, fontWeight: 600,
                      background: activeMetric === k ? c : "transparent",
                      color: activeMetric === k ? "#000" : c, border: `1px solid ${c}44`,
                      cursor: "pointer", letterSpacing: "0.06em", textTransform: "uppercase",
                      transition: "all 0.15s",
                    }}>{k}</button>
                  ))}
                </div>
              </div>
              <ResponsiveContainer width="100%" height={200}>
                <AreaChart data={data} margin={{ top: 5, right: 5, bottom: 0, left: 0 }}>
                  <defs>
                    <linearGradient id="metricGrad" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor={metricColors[activeMetric]} stopOpacity={0.3} />
                      <stop offset="95%" stopColor={metricColors[activeMetric]} stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="#1a1d24" vertical={false} />
                  <XAxis dataKey={range === "7d" ? "day" : "date"} tick={{ fill: "#555", fontSize: 10 }} axisLine={false} tickLine={false} />
                  <YAxis tick={{ fill: "#555", fontSize: 10 }} axisLine={false} tickLine={false} width={35} />
                  <Tooltip content={<CustomTooltip />} />
                  <Area type="monotone" dataKey={activeMetric} name={activeMetric.toUpperCase()} stroke={metricColors[activeMetric]}
                    fill="url(#metricGrad)" strokeWidth={2} dot={false} activeDot={{ r: 4, fill: metricColors[activeMetric] }} />
                </AreaChart>
              </ResponsiveContainer>
            </div>

            {/* Bottom row */}
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16 }}>
              {/* Sleep stages */}
              <div style={{ background: "#10121a", border: "1px solid #1e2130", borderRadius: 14, padding: 20 }}>
                <div style={{ fontSize: 12, fontWeight: 700, textTransform: "uppercase", letterSpacing: "0.06em", marginBottom: 16 }}>Last Night's Sleep</div>
                <div style={{ display: "flex", gap: 12, alignItems: "center", marginBottom: 16 }}>
                  <ScoreRing value={Math.round(today.sleep * 10)} max={100} size={80} strokeWidth={7} color="#3b82f6" />
                  <div>
                    <div style={{ fontSize: 28, fontWeight: 700, fontFamily: "DM Mono, monospace", color: "#f0f0f0" }}>{today.sleep}h</div>
                    <div style={{ fontSize: 11, color: "#555" }}>Total sleep time</div>
                    <div style={{ fontSize: 11, color: "#22d3a5", marginTop: 2 }}>↑ 18min vs avg</div>
                  </div>
                </div>
                <SleepBreakdown data={sleepStages} />
              </div>

              {/* Recent workouts */}
              <div style={{ background: "#10121a", border: "1px solid #1e2130", borderRadius: 14, padding: 20 }}>
                <div style={{ fontSize: 12, fontWeight: 700, textTransform: "uppercase", letterSpacing: "0.06em", marginBottom: 4 }}>Recent Workouts</div>
                {workouts.slice(0, 4).map(w => <WorkoutCard key={w.id} w={w} />)}
              </div>
            </div>
          </div>
        )}

        {/* ── RECOVERY ── */}
        {tab === "recovery" && (
          <div style={{ display: "flex", flexDirection: "column", gap: 20 }}>
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: 14 }}>
              {[
                { label: "HRV Score", value: today.hrv, unit: "ms", color: "#22d3a5", desc: "14-day avg: 44ms" },
                { label: "Resting HR", value: today.rhr, unit: "bpm", color: "#e74c3c", desc: "14-day avg: 55 bpm" },
                { label: "Readiness", value: today.readiness, unit: "", color: "#8b5cf6", desc: "Weekly avg: 71" },
              ].map(m => (
                <div key={m.label} style={{ background: "#10121a", border: "1px solid #1e2130", borderRadius: 14, padding: 20, textAlign: "center" }}>
                  <div style={{ fontSize: 10, color: "#555", textTransform: "uppercase", letterSpacing: "0.1em", marginBottom: 14 }}>{m.label}</div>
                  <ScoreRing value={m.value} size={110} strokeWidth={9} color={m.color} />
                  <div style={{ fontSize: 11, color: "#555", marginTop: 12 }}>{m.desc}</div>
                </div>
              ))}
            </div>

            <div style={{ background: "#10121a", border: "1px solid #1e2130", borderRadius: 14, padding: 20 }}>
              <div style={{ fontSize: 12, fontWeight: 700, textTransform: "uppercase", letterSpacing: "0.06em", marginBottom: 20 }}>HRV vs Readiness — {range}</div>
              <ResponsiveContainer width="100%" height={240}>
                <LineChart data={data} margin={{ top: 5, right: 5, bottom: 0, left: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#1a1d24" vertical={false} />
                  <XAxis dataKey={range === "7d" ? "day" : "date"} tick={{ fill: "#555", fontSize: 10 }} axisLine={false} tickLine={false} />
                  <YAxis tick={{ fill: "#555", fontSize: 10 }} axisLine={false} tickLine={false} width={35} />
                  <Tooltip content={<CustomTooltip />} />
                  <Line type="monotone" dataKey="hrv" name="HRV" stroke="#22d3a5" strokeWidth={2} dot={false} activeDot={{ r: 4 }} />
                  <Line type="monotone" dataKey="readiness" name="Readiness" stroke="#8b5cf6" strokeWidth={2} dot={false} activeDot={{ r: 4 }} />
                  <Line type="monotone" dataKey="rhr" name="RHR" stroke="#e74c3c" strokeWidth={1.5} dot={false} strokeDasharray="4 2" activeDot={{ r: 4 }} />
                </LineChart>
              </ResponsiveContainer>
            </div>

            <div style={{ background: "#10121a", border: "1px solid #1e2130", borderRadius: 14, padding: 20 }}>
              <div style={{ fontSize: 12, fontWeight: 700, textTransform: "uppercase", letterSpacing: "0.06em", marginBottom: 16 }}>Stress Load Distribution</div>
              <ResponsiveContainer width="100%" height={180}>
                <BarChart data={data} margin={{ top: 5, right: 5, bottom: 0, left: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#1a1d24" vertical={false} />
                  <XAxis dataKey={range === "7d" ? "day" : "date"} tick={{ fill: "#555", fontSize: 10 }} axisLine={false} tickLine={false} />
                  <YAxis tick={{ fill: "#555", fontSize: 10 }} axisLine={false} tickLine={false} width={35} />
                  <Tooltip content={<CustomTooltip />} />
                  <Bar dataKey="stress" name="Stress" fill="#8b5cf6" radius={[3, 3, 0, 0]} opacity={0.8} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>
        )}

        {/* ── SLEEP ── */}
        {tab === "sleep" && (
          <div style={{ display: "flex", flexDirection: "column", gap: 20 }}>
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16 }}>
              <div style={{ background: "#10121a", border: "1px solid #1e2130", borderRadius: 14, padding: 24 }}>
                <div style={{ fontSize: 12, fontWeight: 700, textTransform: "uppercase", letterSpacing: "0.06em", marginBottom: 20 }}>Stage Breakdown</div>
                <div style={{ display: "flex", alignItems: "center", gap: 24 }}>
                  <ScoreRing value={Math.round(today.sleep * 10)} max={100} size={130} strokeWidth={10} color="#3b82f6" label="Score" />
                  <div style={{ flex: 1 }}>
                    <SleepBreakdown data={sleepStages} />
                    <div style={{ marginTop: 14, paddingTop: 14, borderTop: "1px solid #1a1d24" }}>
                      <div style={{ fontSize: 11, color: "#555" }}>Sleep efficiency</div>
                      <div style={{ fontSize: 18, fontWeight: 700, fontFamily: "DM Mono, monospace", color: "#3b82f6" }}>94%</div>
                    </div>
                  </div>
                </div>
              </div>
              <div style={{ background: "#10121a", border: "1px solid #1e2130", borderRadius: 14, padding: 24 }}>
                <div style={{ fontSize: 12, fontWeight: 700, textTransform: "uppercase", letterSpacing: "0.06em", marginBottom: 20 }}>Sleep Metrics</div>
                <div style={{ display: "flex", flexDirection: "column", gap: 14 }}>
                  {[
                    { label: "Bedtime", value: "11:14 PM", color: "#3b82f6" },
                    { label: "Wake time", value: "6:58 AM", color: "#22d3a5" },
                    { label: "Latency", value: "8 min", color: "#f59e0b" },
                    { label: "Interruptions", value: "2", color: "#e74c3c" },
                    { label: "Avg HR overnight", value: "52 bpm", color: "#8b5cf6" },
                    { label: "HRV avg", value: `${today.hrv} ms`, color: "#22d3a5" },
                  ].map(m => (
                    <div key={m.label} style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                      <span style={{ fontSize: 12, color: "#666" }}>{m.label}</span>
                      <span style={{ fontSize: 13, fontWeight: 700, color: m.color, fontFamily: "DM Mono, monospace" }}>{m.value}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
            <div style={{ background: "#10121a", border: "1px solid #1e2130", borderRadius: 14, padding: 20 }}>
              <div style={{ fontSize: 12, fontWeight: 700, textTransform: "uppercase", letterSpacing: "0.06em", marginBottom: 20 }}>Sleep Duration Trend</div>
              <ResponsiveContainer width="100%" height={220}>
                <AreaChart data={data} margin={{ top: 5, right: 5, bottom: 0, left: 0 }}>
                  <defs>
                    <linearGradient id="sleepGrad" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.35} />
                      <stop offset="95%" stopColor="#3b82f6" stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="#1a1d24" vertical={false} />
                  <XAxis dataKey={range === "7d" ? "day" : "date"} tick={{ fill: "#555", fontSize: 10 }} axisLine={false} tickLine={false} />
                  <YAxis domain={[4, 9]} tick={{ fill: "#555", fontSize: 10 }} axisLine={false} tickLine={false} width={35} />
                  <Tooltip content={<CustomTooltip />} />
                  <ReferenceLine y={8} stroke="#22d3a5" strokeDasharray="4 2" strokeOpacity={0.4} label={{ value: "Goal", fill: "#22d3a5", fontSize: 10 }} />
                  <Area type="monotone" dataKey="sleep" name="Sleep" stroke="#3b82f6" fill="url(#sleepGrad)" strokeWidth={2} dot={false} activeDot={{ r: 4 }} />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </div>
        )}

        {/* ── ACTIVITY ── */}
        {tab === "activity" && (
          <div style={{ display: "flex", flexDirection: "column", gap: 20 }}>
            <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 12 }}>
              {[
                { label: "Steps Today", value: today.steps.toLocaleString(), color: "#f59e0b", unit: "" },
                { label: "Calories", value: today.calories, color: "#e74c3c", unit: "kcal" },
                { label: "Active Min", value: today.activeMinutes, color: "#22d3a5", unit: "min" },
                { label: "Training Load", value: 78, color: "#8b5cf6", unit: "" },
              ].map(m => (
                <div key={m.label} style={{ background: "#10121a", border: "1px solid #1e2130", borderRadius: 12, padding: 18 }}>
                  <div style={{ fontSize: 10, color: "#555", textTransform: "uppercase", letterSpacing: "0.08em", marginBottom: 8 }}>{m.label}</div>
                  <div style={{ fontSize: 26, fontWeight: 700, fontFamily: "DM Mono, monospace", color: m.color }}>{m.value}</div>
                  <div style={{ fontSize: 11, color: "#444" }}>{m.unit}</div>
                </div>
              ))}
            </div>

            <div style={{ background: "#10121a", border: "1px solid #1e2130", borderRadius: 14, padding: 20 }}>
              <div style={{ fontSize: 12, fontWeight: 700, textTransform: "uppercase", letterSpacing: "0.06em", marginBottom: 20 }}>Daily Steps & Calories</div>
              <ResponsiveContainer width="100%" height={220}>
                <BarChart data={data} margin={{ top: 5, right: 5, bottom: 0, left: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#1a1d24" vertical={false} />
                  <XAxis dataKey={range === "7d" ? "day" : "date"} tick={{ fill: "#555", fontSize: 10 }} axisLine={false} tickLine={false} />
                  <YAxis tick={{ fill: "#555", fontSize: 10 }} axisLine={false} tickLine={false} width={40} />
                  <Tooltip content={<CustomTooltip />} />
                  <Bar dataKey="steps" name="Steps" fill="#f59e0b" radius={[3, 3, 0, 0]} opacity={0.8} />
                  <Bar dataKey="calories" name="Calories" fill="#e74c3c" radius={[3, 3, 0, 0]} opacity={0.7} />
                </BarChart>
              </ResponsiveContainer>
            </div>

            <div style={{ background: "#10121a", border: "1px solid #1e2130", borderRadius: 14, padding: 20 }}>
              <div style={{ fontSize: 12, fontWeight: 700, textTransform: "uppercase", letterSpacing: "0.06em", marginBottom: 4 }}>Workout Log</div>
              <div style={{ fontSize: 11, color: "#444", marginBottom: 12 }}>From Ultrahuman & Zepp</div>
              {workouts.map(w => <WorkoutCard key={w.id} w={w} />)}
            </div>
          </div>
        )}

        {/* ── TRENDS ── */}
        {tab === "trends" && (
          <div style={{ display: "flex", flexDirection: "column", gap: 20 }}>
            <div style={{ background: "#10121a", border: "1px solid #1e2130", borderRadius: 14, padding: 20 }}>
              <div style={{ fontSize: 12, fontWeight: 700, textTransform: "uppercase", letterSpacing: "0.06em", marginBottom: 4 }}>30-Day Overview</div>
              <div style={{ fontSize: 11, color: "#444", marginBottom: 20 }}>HRV · Readiness · Sleep</div>
              <ResponsiveContainer width="100%" height={260}>
                <LineChart data={monthData} margin={{ top: 5, right: 5, bottom: 0, left: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#1a1d24" vertical={false} />
                  <XAxis dataKey="date" tick={{ fill: "#555", fontSize: 9 }} axisLine={false} tickLine={false} interval={4} />
                  <YAxis tick={{ fill: "#555", fontSize: 10 }} axisLine={false} tickLine={false} width={35} />
                  <Tooltip content={<CustomTooltip />} />
                  <Line type="monotone" dataKey="hrv" name="HRV" stroke="#22d3a5" strokeWidth={2} dot={false} />
                  <Line type="monotone" dataKey="readiness" name="Readiness" stroke="#8b5cf6" strokeWidth={2} dot={false} />
                  <Line type="monotone" dataKey="sleep" name="Sleep(h)" stroke="#3b82f6" strokeWidth={1.5} dot={false} strokeDasharray="5 2" />
                </LineChart>
              </ResponsiveContainer>
            </div>

            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16 }}>
              <div style={{ background: "#10121a", border: "1px solid #1e2130", borderRadius: 14, padding: 20 }}>
                <div style={{ fontSize: 12, fontWeight: 700, textTransform: "uppercase", letterSpacing: "0.06em", marginBottom: 16 }}>Weekly Averages</div>
                {[
                  { label: "Avg HRV", current: 46, prev: 42, unit: "ms", color: "#22d3a5" },
                  { label: "Avg Sleep", current: 7.1, prev: 6.8, unit: "h", color: "#3b82f6" },
                  { label: "Avg Steps", current: 9240, prev: 8100, unit: "", color: "#f59e0b" },
                  { label: "Avg Readiness", current: 72, prev: 68, unit: "", color: "#8b5cf6" },
                ].map(m => (
                  <div key={m.label} style={{ display: "flex", justifyContent: "space-between", alignItems: "center", padding: "10px 0", borderBottom: "1px solid #1a1d24" }}>
                    <span style={{ fontSize: 12, color: "#666" }}>{m.label}</span>
                    <div style={{ textAlign: "right" }}>
                      <span style={{ fontSize: 15, fontWeight: 700, color: m.color, fontFamily: "DM Mono, monospace" }}>{m.current}{m.unit}</span>
                      <span style={{ fontSize: 10, color: m.current > m.prev ? "#22d3a5" : "#e74c3c", marginLeft: 6 }}>
                        {m.current > m.prev ? "▲" : "▼"} {Math.abs(((m.current - m.prev)/m.prev*100)).toFixed(0)}%
                      </span>
                    </div>
                  </div>
                ))}
              </div>

              <div style={{ background: "#10121a", border: "1px solid #1e2130", borderRadius: 14, padding: 20 }}>
                <div style={{ fontSize: 12, fontWeight: 700, textTransform: "uppercase", letterSpacing: "0.06em", marginBottom: 16 }}>Wellness Radar</div>
                <ResponsiveContainer width="100%" height={220}>
                  <RadarChart data={[
                    { metric: "HRV", value: 78 }, { metric: "Sleep", value: 71 },
                    { metric: "Activity", value: 85 }, { metric: "Readiness", value: 72 },
                    { metric: "Recovery", value: 68 }, { metric: "Stress", value: 60 },
                  ]}>
                    <PolarGrid stroke="#1e2130" />
                    <PolarAngleAxis dataKey="metric" tick={{ fill: "#555", fontSize: 10 }} />
                    <Radar dataKey="value" stroke="#22d3a5" fill="#22d3a5" fillOpacity={0.15} strokeWidth={1.5} />
                  </RadarChart>
                </ResponsiveContainer>
              </div>
            </div>

            <div style={{ background: "#10121a", border: "1px solid #1e2130", borderRadius: 14, padding: 20 }}>
              <div style={{ fontSize: 12, fontWeight: 700, textTransform: "uppercase", letterSpacing: "0.06em", marginBottom: 16 }}>Data Sources</div>
              <div style={{ display: "flex", gap: 12 }}>
                {[
                  { name: "Ultrahuman Ring", metrics: "HRV · RHR · Sleep · SpO₂ · Temperature", color: "#22d3a5", connected: true },
                  { name: "Zepp / Amazfit", metrics: "Steps · Workouts · HR · Stress · Calories", color: "#3b82f6", connected: true },
                  { name: "Health Connect", metrics: "Sync hub for all Android sources", color: "#8b5cf6", connected: false },
                ].map(s => (
                  <div key={s.name} style={{ flex: 1, border: `1px solid ${s.connected ? s.color + "44" : "#1e2130"}`,
                    borderRadius: 10, padding: 16, background: s.connected ? `${s.color}08` : "#0d0f18" }}>
                    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 8 }}>
                      <span style={{ fontSize: 13, fontWeight: 700, color: s.connected ? "#f0f0f0" : "#555" }}>{s.name}</span>
                      <span style={{ fontSize: 9, padding: "2px 8px", borderRadius: 20,
                        background: s.connected ? `${s.color}22` : "#1a1d24",
                        color: s.connected ? s.color : "#444", fontWeight: 700, letterSpacing: "0.06em" }}>
                        {s.connected ? "ACTIVE" : "IMPORT"}
                      </span>
                    </div>
                    <div style={{ fontSize: 11, color: "#555", lineHeight: 1.5 }}>{s.metrics}</div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
