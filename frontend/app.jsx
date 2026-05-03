/* PolicyPilot — single-file React app
   Dark Apple-inspired liquid-glass aesthetic.
   Strictly follows the PolicyPilot Frontend Integration Contract:
   - POST /api/upload (multipart files)
   - POST /api/analyze ({upload_id, project_name})
   - POST /api/upload-and-analyze (multipart files + project_name)
   - GET  /api/report/{report_id}/{format}  (json|html|md)
   - DELETE /api/upload/{upload_id}
   - GET  /api/config, GET /api/health
   Falls back to a deterministic mock when the API is unreachable so the demo runs offline.
*/

const { useState, useEffect, useMemo, useRef, useCallback } = React;

/* ============================== ICONS ============================== */
const Icon = {
  Logo: (p) => (
    <svg viewBox="0 0 32 32" fill="none" {...p}>
      <defs>
        <linearGradient id="lg1" x1="0" x2="1" y1="0" y2="1">
          <stop offset="0" stopColor="#9be8ff"/>
          <stop offset="1" stopColor="#7fffc8"/>
        </linearGradient>
      </defs>
      <path d="M16 2 L28 8 V18 C28 24 22 28.5 16 30 C10 28.5 4 24 4 18 V8 Z" stroke="url(#lg1)" strokeWidth="1.5" fill="rgba(155,232,255,0.06)"/>
      <path d="M11 16.5 L14.5 20 L21.5 12.5" stroke="url(#lg1)" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round"/>
    </svg>
  ),
  Upload: (p) => <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round" {...p}><path d="M12 16V4"/><path d="m6 10 6-6 6 6"/><path d="M4 20h16"/></svg>,
  File:   (p) => <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round" {...p}><path d="M14 3H6a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V9z"/><path d="M14 3v6h6"/></svg>,
  Trash:  (p) => <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round" {...p}><path d="M3 6h18"/><path d="M8 6V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/><path d="M19 6 18 20a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2L5 6"/></svg>,
  Play:   (p) => <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round" {...p}><path d="m6 4 14 8L6 20Z" fill="currentColor"/></svg>,
  Shield: (p) => <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round" {...p}><path d="M12 2 4 5v7c0 5 3.5 8.5 8 10 4.5-1.5 8-5 8-10V5z"/></svg>,
  Key:    (p) => <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round" {...p}><circle cx="8" cy="14" r="4"/><path d="m11 12 9-9"/><path d="m18 5 3 3"/><path d="m15 8 2 2"/></svg>,
  Book:   (p) => <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round" {...p}><path d="M4 4.5A2.5 2.5 0 0 1 6.5 2H20v17H6.5A2.5 2.5 0 0 0 4 21.5z"/><path d="M4 4.5V21"/></svg>,
  Spark:  (p) => <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round" {...p}><path d="M12 3v4"/><path d="M12 17v4"/><path d="M3 12h4"/><path d="M17 12h4"/><path d="m5.5 5.5 2.8 2.8"/><path d="m15.7 15.7 2.8 2.8"/><path d="m5.5 18.5 2.8-2.8"/><path d="m15.7 8.3 2.8-2.8"/></svg>,
  Folder: (p) => <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round" {...p}><path d="M3 7a2 2 0 0 1 2-2h4l2 2h8a2 2 0 0 1 2 2v9a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/></svg>,
  Down:   (p) => <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round" {...p}><path d="M12 4v12"/><path d="m6 10 6 6 6-6"/><path d="M4 20h16"/></svg>,
  Search: (p) => <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round" {...p}><circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/></svg>,
  Filter: (p) => <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round" {...p}><path d="M3 5h18l-7 9v6l-4-2v-4z"/></svg>,
  Check:  (p) => <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" {...p}><path d="m4 12 5 5 11-12"/></svg>,
  X:      (p) => <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" {...p}><path d="m5 5 14 14"/><path d="m19 5-14 14"/></svg>,
  Alert:  (p) => <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round" {...p}><path d="M12 3 2 21h20z"/><path d="M12 9v5"/><circle cx="12" cy="17.5" r="0.6" fill="currentColor"/></svg>,
  Github: (p) => <svg viewBox="0 0 24 24" fill="currentColor" {...p}><path d="M12 .5a12 12 0 0 0-3.79 23.4c.6.11.82-.26.82-.58v-2.04c-3.34.73-4.04-1.61-4.04-1.61-.55-1.39-1.34-1.76-1.34-1.76-1.09-.74.08-.73.08-.73 1.21.09 1.85 1.24 1.85 1.24 1.07 1.84 2.81 1.31 3.5 1 .11-.78.42-1.31.76-1.61-2.66-.3-5.47-1.33-5.47-5.93 0-1.31.47-2.38 1.24-3.22-.13-.3-.54-1.52.12-3.17 0 0 1.01-.32 3.3 1.23a11.43 11.43 0 0 1 6 0c2.29-1.55 3.3-1.23 3.3-1.23.66 1.65.25 2.87.12 3.17.77.84 1.24 1.91 1.24 3.22 0 4.61-2.81 5.62-5.49 5.92.43.37.81 1.1.81 2.21v3.28c0 .32.22.7.83.58A12 12 0 0 0 12 .5z"/></svg>,
  Copy:   (p) => <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round" {...p}><rect x="9" y="9" width="12" height="12" rx="2"/><path d="M5 15V5a2 2 0 0 1 2-2h10"/></svg>,
  Eye:    (p) => <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round" {...p}><path d="M2 12s3.5-7 10-7 10 7 10 7-3.5 7-10 7S2 12 2 12Z"/><circle cx="12" cy="12" r="3"/></svg>,
  Code:   (p) => <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round" {...p}><path d="m9 8-5 4 5 4"/><path d="m15 8 5 4-5 4"/></svg>,
  Cloud:  (p) => <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round" {...p}><path d="M7 18a5 5 0 0 1-.6-9.96A6 6 0 0 1 18 9.5 4 4 0 0 1 17 18z"/></svg>,
};

/* ============================== HELPERS ============================== */
const API_BASE = ""; // same-origin
const formatBytes = (b) => {
  if (!b && b !== 0) return "—";
  const u = ["B","KB","MB","GB"]; let i = 0; let n = b;
  while (n >= 1024 && i < u.length - 1) { n /= 1024; i++; }
  return `${n.toFixed(n < 10 && i > 0 ? 1 : 0)} ${u[i]}`;
};
const ALLOWED = [".py",".md",".txt",".json",".yaml",".yml",".pdf",".docx",".ipynb",".sh",".env.example"];
const allowedExt = (n) => ALLOWED.some(e => n.toLowerCase().endsWith(e));
const cls = (...x) => x.filter(Boolean).join(" ");

const gradeFromScore = (s) =>
  s >= 90 ? "A" : s >= 80 ? "B" : s >= 70 ? "C" : s >= 60 ? "D" : "F";
const statusFromScore = (s) =>
  s >= 70 ? "PASS" : s >= 50 ? "WARNING" : "FAIL";

/* Deterministic mock analysis (used as offline fallback) */
function mockAnalysis(projectName, files) {
  const ts = new Date().toISOString();
  return {
    project_name: projectName || "Unnamed Project",
    timestamp: ts,
    secrets_found: [
      { pattern_name: "AWS Access Key ID", secret_type: "aws_access_key", file_path: "config/settings.py", line_number: 42, column_start: 15, column_end: 35, matched_text: "AKIA••••••••••••EXMP", context: "AWS_ACCESS_KEY = 'AKIA...'", severity: "critical", confidence: 0.95, entropy: 4.2, reason: "AWS Access Key ID detected", is_verified: false },
      { pattern_name: "Generic API Token", secret_type: "api_token", file_path: "src/clients/openai.py", line_number: 12, column_start: 18, column_end: 60, matched_text: "sk-•••••••••••••••••••••cT9k", context: "OPENAI_API_KEY = 'sk-...'", severity: "high", confidence: 0.81, entropy: 4.6, reason: "High-entropy token in source", is_verified: false },
      { pattern_name: "Slack Webhook", secret_type: "slack_webhook", file_path: "scripts/notify.sh", line_number: 4, column_start: 10, column_end: 80, matched_text: "https://hooks.slack.com/services/T0••••/B0••••/••••", context: "WEBHOOK=\"https://hooks.slack.com/...\"", severity: "medium", confidence: 0.62, entropy: 3.8, reason: "Slack webhook URL", is_verified: false },
    ],
    readme_result: {
      exists: true,
      has_required_sections: false,
      missing_required: ["## Installation"],
      missing_recommended: ["## Contributing", "## License"],
      word_count: 312,
      score: 78.0,
      issues: [
        { type: "readme", severity: "high",   message: "Missing required section: ## Installation", file_path: "README.md", line_number: null, details: null },
        { type: "readme", severity: "medium", message: "Missing recommended section: ## Contributing", file_path: "README.md", line_number: null, details: null },
        { type: "readme", severity: "low",    message: "Missing recommended section: ## License",       file_path: "README.md", line_number: null, details: null },
      ],
    },
    prompt_result: {
      total_prompts: 4,
      documented_prompts: 3,
      missing_fields: { "prompts/analyze.txt": ["example", "constraints"] },
      score: 82.0,
      issues: [
        { type: "prompt", severity: "high",   message: "Missing required field: example",      file_path: "prompts/analyze.txt", line_number: null, details: null },
        { type: "prompt", severity: "medium", message: "Missing recommended field: constraints", file_path: "prompts/analyze.txt", line_number: null, details: null },
      ],
    },
    module_scores: [
      { name: "Secret Scanner",     score: 68.0,  weight: 0.35, weighted_score: 23.8, issues_count: 3, critical_issues: 1 },
      { name: "README Validator",   score: 78.0,  weight: 0.25, weighted_score: 19.5, issues_count: 3, critical_issues: 0 },
      { name: "Prompt Documentation", score: 82.0, weight: 0.25, weighted_score: 20.5, issues_count: 2, critical_issues: 0 },
      { name: "Project Structure",  score: 100.0, weight: 0.15, weighted_score: 15.0, issues_count: 0, critical_issues: 0 },
    ],
    total_score: 78.8,
    passed: true,
    total_issues: 8,
    critical_issues: 1,
    files_analyzed: files?.length || 14,
    all_issues: [],
  };
}

/* ============================== TOASTS ============================== */
function useToasts() {
  const [list, setList] = useState([]);
  const push = useCallback((kind, msg) => {
    const id = Math.random().toString(36).slice(2);
    setList((xs) => [...xs, { id, kind, msg }]);
    setTimeout(() => setList((xs) => xs.filter(t => t.id !== id)), 3800);
  }, []);
  return { list, push };
}
function ToastHost({ toasts }) {
  return (
    <div className="fixed top-4 right-4 z-[60] flex flex-col gap-2">
      {toasts.map(t => (
        <div key={t.id} className={cls(
          "glass-strong px-4 py-3 rounded-xl text-sm flex items-center gap-2 min-w-[260px] max-w-sm",
          t.kind === "error"   && "!border-rose-500/40",
          t.kind === "success" && "!border-mint-500/40",
        )}>
          <span className={cls(
            "w-1.5 h-1.5 rounded-full",
            t.kind === "error" ? "bg-rose-500" : t.kind === "success" ? "bg-mint-500" : "bg-accent-500"
          )}/>
          <span className="text-white/90">{t.msg}</span>
        </div>
      ))}
    </div>
  );
}

/* ============================== NAVBAR ============================== */
function Navbar({ onJump }) {
  const [scrolled, setScrolled] = useState(false);
  useEffect(() => {
    const h = () => setScrolled(window.scrollY > 12);
    h(); window.addEventListener("scroll", h);
    return () => window.removeEventListener("scroll", h);
  }, []);
  const links = [
    ["upload",   "Upload"],
    ["score",    "Score"],
    ["modules",  "Modules"],
    ["findings", "Findings"],
    ["report",   "Report"],
  ];
  return (
    <div className={cls(
      "fixed top-0 left-0 right-0 z-50 px-4 pt-4 transition-all",
      scrolled ? "translate-y-0" : "translate-y-0"
    )}>
      <div className="max-w-7xl mx-auto">
        <div className="glass-strong rounded-2xl px-3 sm:px-4 py-2.5 flex items-center justify-between">
          <div className="flex items-center gap-2.5 pl-1">
            <Icon.Logo width="26" height="26" />
            <div className="leading-tight">
              <div className="text-[15px] font-semibold tracking-tight">PolicyPilot</div>
              <div className="text-[10px] uppercase tracking-[0.18em] text-white/40">Compliance OS</div>
            </div>
          </div>
          <nav className="hidden md:flex items-center gap-1">
            {links.map(([id, label]) => (
              <button key={id} onClick={() => onJump(id)}
                className="px-3 py-1.5 text-[13px] text-white/65 hover:text-white rounded-lg hover:bg-white/5 transition">
                {label}
              </button>
            ))}
          </nav>
          <div className="flex items-center gap-2">
            <span className="hidden sm:flex items-center gap-1.5 text-[11px] text-white/55 px-2.5 py-1 rounded-full glass-thin">
              <span className="w-1.5 h-1.5 rounded-full bg-mint-500 pulse-dot"/> v1.0.0 healthy
            </span>
            <button onClick={() => onJump("upload")} className="btn-primary px-3.5 py-1.5 rounded-lg text-[13px] font-medium">
              New scan
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

/* ============================== HERO ============================== */
function Hero({ onJump }) {
  return (
    <section className="relative pt-32 pb-20 px-6">
      <div className="max-w-7xl mx-auto">
        <div className="flex items-center gap-2 text-[11px] uppercase tracking-[0.22em] text-white/45 mb-6">
          <span className="w-6 h-px bg-white/30"/>
          <span>Compliance · Security · Documentation</span>
        </div>
        <div className="grid md:grid-cols-12 gap-10 items-end">
          <div className="md:col-span-7">
            <h1 className="text-grad text-[56px] sm:text-[72px] md:text-[84px] leading-[0.95] font-bold tracking-[-0.03em]">
              Ship <span className="text-grad-accent">policy-grade</span><br/>
              repositories,<br/>without the audit.
            </h1>
            <p className="mt-6 text-white/60 text-[17px] max-w-[52ch] leading-relaxed">
              PolicyPilot scans your codebase for leaked secrets, validates your README, and grades prompt documentation —
              giving every project a single weighted compliance score before you push to main.
            </p>
            <div className="mt-8 flex flex-wrap items-center gap-3">
              <button onClick={() => onJump("upload")} className="btn-primary px-5 py-3 rounded-xl text-[14px] font-semibold flex items-center gap-2">
                <Icon.Upload width="16" height="16"/> Upload repository
              </button>
              <button onClick={() => onJump("score")} className="btn-ghost px-5 py-3 rounded-xl text-[14px] font-medium flex items-center gap-2 text-white/85">
                <Icon.Eye width="16" height="16"/> View example dashboard
              </button>
              <div className="flex items-center gap-2 text-[12px] text-white/45 ml-2">
                <Icon.Shield width="14" height="14"/> No auth required · 100MB max
              </div>
            </div>
          </div>

          <div className="md:col-span-5">
            <div className="glass-strong rounded-3xl p-5 drift-slow">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2 text-[11px] text-white/55">
                  <span className="w-2 h-2 rounded-full bg-rose-500"/>
                  <span className="w-2 h-2 rounded-full bg-amber-500"/>
                  <span className="w-2 h-2 rounded-full bg-mint-500"/>
                  <span className="ml-2 font-mono">policypilot · live</span>
                </div>
                <span className="text-[10px] text-white/40">A · PASS</span>
              </div>
              <div className="mt-5 grid grid-cols-3 gap-3">
                <MiniStat label="Score"     value="92.4" trend="+3.1"/>
                <MiniStat label="Critical"  value="0"    trend="-1"/>
                <MiniStat label="Files"     value="184"  trend="+12"/>
              </div>
              <div className="mt-5 rounded-2xl glass-thin p-4">
                <div className="text-[11px] uppercase tracking-wider text-white/40 mb-3">Module weights</div>
                <ModuleBars rows={[
                  ["Secrets",    35, "from-accent-500 to-mint-500"],
                  ["README",     25, "from-accent-500 to-accent-400"],
                  ["Prompts",    25, "from-mint-500 to-accent-500"],
                  ["Structure",  15, "from-amber-500 to-mint-500"],
                ]}/>
              </div>
            </div>

            <Marquee/>
          </div>
        </div>
      </div>
    </section>
  );
}
function MiniStat({ label, value, trend }) {
  return (
    <div className="glass-thin rounded-xl p-3">
      <div className="text-[10px] uppercase tracking-wider text-white/40">{label}</div>
      <div className="mt-1 flex items-baseline gap-1.5">
        <div className="text-[22px] font-semibold num-tabular">{value}</div>
        <div className="text-[10px] text-mint-400 num-tabular">{trend}</div>
      </div>
    </div>
  );
}
function ModuleBars({ rows }) {
  return (
    <div className="space-y-2.5">
      {rows.map(([name, pct, grad]) => (
        <div key={name}>
          <div className="flex items-center justify-between text-[11px]">
            <span className="text-white/65">{name}</span>
            <span className="text-white/45 font-mono">{pct}%</span>
          </div>
          <div className="mt-1 h-1.5 bg-white/[0.05] rounded-full overflow-hidden">
            <div className={`h-full bg-gradient-to-r ${grad}`} style={{ width: `${pct * 2.4}%`, maxWidth: "100%" }} />
          </div>
        </div>
      ))}
    </div>
  );
}
function Marquee() {
  const labels = ["AWS Access Keys","OpenAI Tokens","Slack Webhooks","GCP Service Accounts","Stripe Keys","GitHub PAT","Generic Entropy ≥4.5","Private RSA","Azure SAS","Twilio Auth","JWT Secret","SSH Private","DB URI"];
  const row = [...labels, ...labels];
  return (
    <div className="mt-4 overflow-hidden glass-thin rounded-xl py-2.5 [mask-image:linear-gradient(90deg,transparent,#000_15%,#000_85%,transparent)]">
      <div className="flex gap-6 marq whitespace-nowrap">
        {row.map((l, i) => (
          <span key={i} className="text-[11px] font-mono text-white/55 inline-flex items-center gap-2">
            <Icon.Key width="11" height="11" className="text-accent-400"/> {l}
          </span>
        ))}
      </div>
    </div>
  );
}

/* ============================== UPLOAD PANEL ============================== */
function UploadPanel({ files, setFiles, projectName, setProjectName, uploadId, setUploadId, onAnalyze, busy, status, toast }) {
  const [drag, setDrag] = useState(false);
  const inputRef = useRef(null);

  const onPick = (list) => {
    const arr = Array.from(list || []);
    const ok = []; const bad = [];
    arr.forEach(f => allowedExt(f.name) ? ok.push(f) : bad.push(f.name));
    if (bad.length) toast("error", `Skipped ${bad.length} unsupported file${bad.length > 1 ? "s" : ""}`);
    if (ok.length)  setFiles((xs) => [...xs, ...ok]);
  };
  const remove = (i) => setFiles((xs) => xs.filter((_, k) => k !== i));

  const totalBytes = files.reduce((a, f) => a + f.size, 0);
  const overLimit = totalBytes > 100 * 1024 * 1024;

  return (
    <section id="upload" className="relative px-6 py-16">
      <div className="max-w-7xl mx-auto">
        <SectionHeader
          eyebrow="01 · Ingest"
          title="Drop a repository, get a verdict."
          sub="Upload Python, Markdown, YAML, prompts, or notebooks. We hash-stream files into an isolated scan cell."
        />
        <div className="mt-10 grid lg:grid-cols-12 gap-6">
          <div className="lg:col-span-7">
            <div
              className={cls(
                "glass-strong rounded-3xl p-6 sm:p-8 transition-all",
                drag && "dropzone-active"
              )}
              onDragOver={(e) => { e.preventDefault(); setDrag(true); }}
              onDragLeave={() => setDrag(false)}
              onDrop={(e) => { e.preventDefault(); setDrag(false); onPick(e.dataTransfer.files); }}
            >
              <div className="flex flex-col items-center text-center py-8">
                <div className="relative">
                  <div className="absolute inset-0 rounded-full bg-accent-500/20 blur-2xl"/>
                  <div className="relative w-16 h-16 rounded-2xl glass-thin flex items-center justify-center">
                    <Icon.Cloud width="28" height="28" className="text-accent-400"/>
                  </div>
                </div>
                <div className="mt-5 text-[20px] font-semibold tracking-tight">Drop files anywhere here</div>
                <div className="mt-1.5 text-white/50 text-[13px]">or</div>
                <button
                  onClick={() => inputRef.current?.click()}
                  className="mt-3 btn-primary px-4 py-2 rounded-lg text-[13px] font-medium inline-flex items-center gap-2"
                >
                  <Icon.Folder width="14" height="14"/> Browse files
                </button>
                <input ref={inputRef} type="file" multiple hidden
                  accept={ALLOWED.join(",")}
                  onChange={(e) => { onPick(e.target.files); e.target.value = ""; }}/>
                <div className="mt-5 flex flex-wrap justify-center gap-1.5 max-w-md">
                  {ALLOWED.map(e => (
                    <span key={e} className="text-[10.5px] font-mono px-2 py-0.5 rounded-md glass-thin text-white/55">{e}</span>
                  ))}
                </div>
              </div>

              {files.length > 0 && (
                <div className="mt-2 border-t border-white/[0.06] pt-5">
                  <div className="flex items-center justify-between mb-3">
                    <div className="text-[12px] uppercase tracking-wider text-white/45">
                      {files.length} file{files.length === 1 ? "" : "s"} · {formatBytes(totalBytes)}
                      {overLimit && <span className="ml-2 text-rose-400">over 100MB limit</span>}
                    </div>
                    <button onClick={() => setFiles([])} className="text-[12px] text-white/55 hover:text-white">Clear all</button>
                  </div>
                  <div className="max-h-72 overflow-y-auto pr-1 scroll-fade-mask space-y-1.5">
                    {files.map((f, i) => (
                      <div key={i} className="glass-thin rounded-lg px-3 py-2 flex items-center gap-3 group">
                        <Icon.File width="15" height="15" className="text-white/55 shrink-0"/>
                        <div className="flex-1 min-w-0">
                          <div className="text-[13px] truncate">{f.name}</div>
                          <div className="text-[11px] text-white/40 font-mono">{formatBytes(f.size)} · {(f.name.split(".").pop() || "").toUpperCase()}</div>
                        </div>
                        <button onClick={() => remove(i)} className="opacity-0 group-hover:opacity-100 transition text-white/55 hover:text-rose-400">
                          <Icon.Trash width="15" height="15"/>
                        </button>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>

          <div className="lg:col-span-5 space-y-4">
            <div className="glass rounded-3xl p-6">
              <label className="text-[11px] uppercase tracking-[0.18em] text-white/45">Project name</label>
              <input
                value={projectName}
                onChange={(e) => setProjectName(e.target.value)}
                placeholder="e.g. acme-llm-orchestrator"
                className="mt-2 w-full bg-transparent border border-white/10 rounded-xl px-3.5 py-2.5 text-[14px] outline-none focus:border-accent-500/60 placeholder:text-white/25"
              />
              <div className="mt-4 grid grid-cols-2 gap-2 text-[12px]">
                <div className="glass-thin rounded-lg px-3 py-2">
                  <div className="text-white/40 text-[10px] uppercase tracking-wider">Endpoint</div>
                  <div className="font-mono text-white/80 text-[11px] truncate">/api/upload-and-analyze</div>
                </div>
                <div className="glass-thin rounded-lg px-3 py-2">
                  <div className="text-white/40 text-[10px] uppercase tracking-wider">Upload ID</div>
                  <div className="font-mono text-white/80 text-[11px] truncate">{uploadId || "—"}</div>
                </div>
              </div>
              <button
                onClick={onAnalyze}
                disabled={busy || files.length === 0 || overLimit}
                className={cls(
                  "mt-5 w-full px-5 py-3 rounded-xl font-semibold flex items-center justify-center gap-2 transition",
                  (busy || files.length === 0 || overLimit) ? "bg-white/[0.06] text-white/35 cursor-not-allowed" : "btn-primary"
                )}
              >
                {busy ? (
                  <><span className="w-3.5 h-3.5 border-2 border-current border-t-transparent rounded-full animate-spin"/> {status || "Analyzing…"}</>
                ) : (
                  <><Icon.Play width="14" height="14"/> Upload & analyze</>
                )}
              </button>
              <div className="mt-3 text-[11px] text-white/40 leading-relaxed">
                Sends <span className="font-mono text-white/65">multipart/form-data</span> to <span className="font-mono text-white/65">/api/upload-and-analyze</span> with <span className="font-mono text-white/65">files[]</span> and <span className="font-mono text-white/65">project_name</span>.
              </div>
            </div>

            <div className="glass rounded-3xl p-5">
              <div className="text-[11px] uppercase tracking-[0.18em] text-white/45 mb-2">Pipeline</div>
              <Pipeline busy={busy} status={status}/>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}

function Pipeline({ busy, status }) {
  const steps = [
    { id: "upload",  label: "Upload",        hint: "POST /api/upload" },
    { id: "secrets", label: "Secret scan",   hint: "regex + entropy" },
    { id: "readme",  label: "README",        hint: "section validator" },
    { id: "prompts", label: "Prompt docs",   hint: "field coverage" },
    { id: "score",   label: "Score & report",hint: "weighted total" },
  ];
  const active = steps.findIndex(s => (status || "").toLowerCase().includes(s.id));
  return (
    <ol className="space-y-2.5">
      {steps.map((s, i) => {
        const done = busy && active >= 0 && i < active;
        const cur  = busy && active === i;
        return (
          <li key={s.id} className="flex items-center gap-3">
            <div className={cls(
              "w-7 h-7 rounded-lg flex items-center justify-center text-[11px] font-mono shrink-0",
              done ? "bg-mint-500/20 text-mint-400 border border-mint-500/30"
                   : cur ? "bg-accent-500/20 text-accent-400 border border-accent-500/40"
                         : "glass-thin text-white/40"
            )}>
              {done ? <Icon.Check width="14" height="14"/> : (i+1).toString().padStart(2,"0")}
            </div>
            <div className="flex-1">
              <div className={cls("text-[13px]", cur ? "text-white" : "text-white/75")}>{s.label}</div>
              <div className="text-[11px] text-white/40 font-mono">{s.hint}</div>
            </div>
            {cur && <div className="w-16 h-1 rounded-full bg-white/[0.06] overflow-hidden"><div className="h-full shimmer w-1/2"/></div>}
          </li>
        );
      })}
    </ol>
  );
}

/* ============================== SECTION HEADER ============================== */
function SectionHeader({ eyebrow, title, sub, right }) {
  return (
    <div className="flex flex-col sm:flex-row sm:items-end justify-between gap-4">
      <div>
        <div className="text-[11px] uppercase tracking-[0.22em] text-white/45 mb-3">{eyebrow}</div>
        <h2 className="text-[34px] sm:text-[42px] font-semibold tracking-[-0.02em] text-grad max-w-[22ch] leading-[1.05]">{title}</h2>
        {sub && <p className="mt-3 text-white/55 max-w-[60ch] text-[15px]">{sub}</p>}
      </div>
      {right}
    </div>
  );
}

/* ============================== SCORE GAUGE ============================== */
function ScoreGauge({ score, status, grade }) {
  const [shown, setShown] = useState(0);
  useEffect(() => {
    let raf; const t0 = performance.now(); const dur = 1100;
    const tick = (t) => {
      const k = Math.min(1, (t - t0) / dur);
      const eased = 1 - Math.pow(1 - k, 3);
      setShown(score * eased);
      if (k < 1) raf = requestAnimationFrame(tick);
    };
    raf = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(raf);
  }, [score]);

  const R = 96;
  const C = 2 * Math.PI * R;
  const off = C - (shown / 100) * C;

  const color = status === "PASS" ? "#3ee5a3" : status === "WARNING" ? "#ffb547" : "#ff5d72";

  return (
    <div className="relative w-[260px] h-[260px] mx-auto">
      <svg viewBox="0 0 240 240" className="w-full h-full -rotate-90">
        <defs>
          <linearGradient id="gaugeGrad" x1="0" x2="1" y1="0" y2="1">
            <stop offset="0%"  stopColor="#9be8ff"/>
            <stop offset="50%" stopColor="#7fffc8"/>
            <stop offset="100%" stopColor={color}/>
          </linearGradient>
          <filter id="glow"><feGaussianBlur stdDeviation="3"/></filter>
        </defs>
        <circle cx="120" cy="120" r={R} stroke="rgba(255,255,255,0.06)" strokeWidth="14" fill="none"/>
        <circle cx="120" cy="120" r={R} stroke="url(#gaugeGrad)" strokeWidth="14" fill="none"
          strokeLinecap="round" strokeDasharray={C} strokeDashoffset={off}/>
        <circle cx="120" cy="120" r={R} stroke="url(#gaugeGrad)" strokeWidth="14" fill="none"
          strokeLinecap="round" strokeDasharray={C} strokeDashoffset={off} filter="url(#glow)" opacity="0.5"/>
      </svg>
      <div className="absolute inset-0 flex flex-col items-center justify-center">
        <div className="text-[10px] uppercase tracking-[0.22em] text-white/45">Total score</div>
        <div className="mt-1 text-[64px] font-semibold tracking-tighter num-tabular leading-none">
          {shown.toFixed(1)}
        </div>
        <div className="mt-2 flex items-center gap-2">
          <span className="px-2 py-0.5 rounded-md text-[11px] glass-thin font-mono text-white/75">grade {grade}</span>
          <span className={cls(
            "px-2 py-0.5 rounded-md text-[11px] font-medium",
            status === "PASS" && "severity-low",
            status === "WARNING" && "severity-high",
            status === "FAIL" && "severity-critical"
          )}>{status}</span>
        </div>
      </div>
    </div>
  );
}

/* ============================== SCORE SECTION ============================== */
function ScoreSection({ result }) {
  if (!result) return <EmptyState id="score" title="Run an analysis to see scoring" sub="Your weighted score, module breakdown, and pass/fail verdict will appear here."/>;

  const grade = gradeFromScore(result.total_score);
  const status = statusFromScore(result.total_score);

  return (
    <section id="score" className="relative px-6 py-16">
      <div className="max-w-7xl mx-auto">
        <SectionHeader
          eyebrow="02 · Verdict"
          title="Your weighted compliance score."
          sub={`${result.project_name} · scanned ${new Date(result.timestamp).toLocaleString()} · ${result.files_analyzed} files`}
          right={
            <div className="hidden sm:flex items-center gap-2">
              <Pill icon="Shield" label={`${result.total_issues} issues`}/>
              <Pill icon="Alert"  label={`${result.critical_issues} critical`} tone="rose"/>
            </div>
          }
        />
        <div className="mt-10 grid lg:grid-cols-12 gap-6">
          <div className="lg:col-span-5">
            <div className="glass-strong rounded-3xl p-8 h-full">
              <ScoreGauge score={result.total_score} status={status} grade={grade}/>
              <div className="mt-6 grid grid-cols-3 gap-2 text-center">
                <KpiSm label="Files"    value={result.files_analyzed}/>
                <KpiSm label="Issues"   value={result.total_issues}/>
                <KpiSm label="Critical" value={result.critical_issues} tone={result.critical_issues > 0 ? "rose" : "mint"}/>
              </div>
            </div>
          </div>
          <div className="lg:col-span-7">
            <div className="glass-strong rounded-3xl p-6 sm:p-8 h-full">
              <div className="flex items-center justify-between mb-5">
                <div>
                  <div className="text-[11px] uppercase tracking-[0.18em] text-white/45">Module breakdown</div>
                  <div className="text-[18px] font-semibold tracking-tight mt-1">Weighted contributions</div>
                </div>
                <div className="text-[11px] text-white/40 font-mono">35 / 25 / 25 / 15</div>
              </div>
              <div className="space-y-3">
                {result.module_scores.map((m, i) => <ModuleRow key={i} m={m} delay={i * 80}/>)}
              </div>
              <div className="mt-6 grid grid-cols-3 gap-3">
                <Threshold label="Pass"    value={70} active={result.total_score >= 70}/>
                <Threshold label="Warning" value={50} active={result.total_score >= 50 && result.total_score < 70} tone="amber"/>
                <Threshold label="Fail"    value={0}  active={result.total_score < 50} tone="rose"/>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}

function KpiSm({ label, value, tone }) {
  return (
    <div className="glass-thin rounded-xl px-3 py-3">
      <div className={cls("text-[22px] font-semibold num-tabular",
        tone === "rose" ? "text-rose-400" : tone === "mint" ? "text-mint-400" : "text-white"
      )}>{value}</div>
      <div className="text-[10px] uppercase tracking-wider text-white/40">{label}</div>
    </div>
  );
}
function Pill({ icon, label, tone }) {
  const I = Icon[icon] || Icon.Shield;
  return (
    <span className={cls(
      "inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg text-[12px] glass-thin",
      tone === "rose" && "!border-rose-500/30 text-rose-400"
    )}>
      <I width="13" height="13"/> {label}
    </span>
  );
}
function ModuleRow({ m, delay }) {
  const [w, setW] = useState(0);
  useEffect(() => {
    const t = setTimeout(() => setW(m.score), 80 + delay);
    return () => clearTimeout(t);
  }, [m.score, delay]);
  const tone =
    m.score >= 90 ? "from-mint-500 to-accent-500"
    : m.score >= 70 ? "from-accent-500 to-mint-500"
    : m.score >= 50 ? "from-amber-500 to-accent-500"
    : "from-rose-500 to-amber-500";
  return (
    <div className="glass-thin rounded-2xl p-4">
      <div className="flex items-center justify-between gap-4">
        <div className="flex items-center gap-3 min-w-0">
          <ModuleIcon name={m.name}/>
          <div className="min-w-0">
            <div className="text-[14px] font-medium truncate">{m.name}</div>
            <div className="text-[11px] text-white/45 font-mono">weight {Math.round(m.weight * 100)}% · contributes {m.weighted_score.toFixed(1)}</div>
          </div>
        </div>
        <div className="text-right shrink-0">
          <div className="text-[20px] font-semibold num-tabular">{m.score.toFixed(1)}</div>
          <div className="text-[10px] uppercase tracking-wider text-white/40">{m.issues_count} issue{m.issues_count===1?"":"s"}{m.critical_issues>0&&` · ${m.critical_issues} critical`}</div>
        </div>
      </div>
      <div className="mt-3 relative h-2 bg-white/[0.05] rounded-full overflow-hidden">
        <div className={`h-full bg-gradient-to-r ${tone} transition-[width] duration-1000 ease-out`} style={{ width: `${w}%` }}/>
        <div className="absolute top-1/2 -translate-y-1/2 w-px h-3 bg-white/30" style={{ left: "70%" }}/>
      </div>
    </div>
  );
}
function ModuleIcon({ name }) {
  const map = {
    "Secret Scanner":     ["Key",    "from-rose-500/30 to-amber-500/20", "text-rose-400"],
    "README Validator":   ["Book",   "from-accent-500/30 to-mint-500/20", "text-accent-400"],
    "Prompt Documentation":["Spark", "from-mint-500/30 to-accent-500/20", "text-mint-400"],
    "Project Structure":  ["Folder", "from-amber-500/30 to-accent-500/20", "text-amber-400"],
  };
  const [k, grad, color] = map[name] || ["Shield", "from-white/20 to-white/5", "text-white"];
  const I = Icon[k];
  return (
    <div className={cls("w-9 h-9 rounded-xl bg-gradient-to-br flex items-center justify-center border border-white/10", grad)}>
      <I width="16" height="16" className={color}/>
    </div>
  );
}
function Threshold({ label, value, active, tone }) {
  return (
    <div className={cls(
      "glass-thin rounded-xl px-3 py-2.5",
      active && tone === "amber" && "!border-amber-500/40",
      active && tone === "rose"  && "!border-rose-500/40",
      active && !tone            && "!border-mint-500/40",
    )}>
      <div className="flex items-center justify-between">
        <span className="text-[11px] uppercase tracking-wider text-white/45">{label}</span>
        {active && <span className="w-1.5 h-1.5 rounded-full bg-mint-500 pulse-dot"/>}
      </div>
      <div className="text-[15px] font-semibold mt-1 num-tabular">≥ {value}</div>
    </div>
  );
}

/* ============================== ISSUE SUMMARY CARDS ============================== */
function IssueSummary({ result }) {
  if (!result) return null;
  const severities = ["critical","high","medium","low","info"];
  const allIssues = [
    ...result.secrets_found.map(s => ({ type: "secret", severity: s.severity, message: `${s.pattern_name} detected`, file_path: s.file_path, line_number: s.line_number })),
    ...(result.readme_result?.issues || []),
    ...(result.prompt_result?.issues || []),
  ];
  const counts = {};
  severities.forEach(s => counts[s] = allIssues.filter(i => i.severity === s).length);

  const cards = [
    { kind: "secret",    title: "Secrets",    icon: "Key",   accent: "rose",
      count: result.secrets_found.length,
      sub: `${result.secrets_found.filter(s => s.severity === "critical").length} critical`,
      detail: result.secrets_found.slice(0, 3).map(s => ({ label: s.pattern_name, hint: s.file_path, severity: s.severity })) },
    { kind: "readme",    title: "README",     icon: "Book", accent: "accent",
      count: result.readme_result?.issues?.length ?? 0,
      sub: `${result.readme_result?.word_count ?? 0} words · score ${result.readme_result?.score?.toFixed(0) ?? "—"}`,
      detail: (result.readme_result?.issues || []).slice(0,3).map(i => ({ label: i.message, hint: i.file_path, severity: i.severity })) },
    { kind: "prompt",    title: "Prompts",    icon: "Spark", accent: "mint",
      count: result.prompt_result?.issues?.length ?? 0,
      sub: `${result.prompt_result?.documented_prompts ?? 0} of ${result.prompt_result?.total_prompts ?? 0} documented`,
      detail: (result.prompt_result?.issues || []).slice(0,3).map(i => ({ label: i.message, hint: i.file_path, severity: i.severity })) },
    { kind: "structure", title: "Structure",  icon: "Folder", accent: "amber",
      count: 0,
      sub: `Project layout passes`,
      detail: [{ label: "All required directories present", hint: "src/ · prompts/ · tests/", severity: "info" }] },
  ];

  return (
    <section id="modules" className="relative px-6 py-16">
      <div className="max-w-7xl mx-auto">
        <SectionHeader
          eyebrow="03 · Categories"
          title="Where compliance breaks, by category."
          sub="Each module surfaces the highest-priority issues. Drill down into the explorer below for the full list."
        />

        <div className="mt-8 flex flex-wrap items-center gap-2">
          {severities.map(s => (
            <span key={s} className={cls("px-2.5 py-1 rounded-lg text-[12px] flex items-center gap-1.5", `severity-${s}`)}>
              <span className="font-mono num-tabular">{counts[s]}</span> {s}
            </span>
          ))}
        </div>

        <div className="mt-6 grid sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {cards.map(c => <CategoryCard key={c.kind} {...c}/>)}
        </div>
      </div>
    </section>
  );
}
function CategoryCard({ title, icon, accent, count, sub, detail }) {
  const I = Icon[icon];
  const accentMap = {
    rose:   "from-rose-500/40 to-amber-500/10 text-rose-400",
    accent: "from-accent-500/40 to-mint-500/10 text-accent-400",
    mint:   "from-mint-500/40 to-accent-500/10 text-mint-400",
    amber:  "from-amber-500/40 to-mint-500/10 text-amber-400",
  };
  return (
    <div className="glass-strong rounded-3xl p-5 group hover:translate-y-[-2px] transition-transform">
      <div className="flex items-start justify-between">
        <div className={cls("w-10 h-10 rounded-xl bg-gradient-to-br border border-white/10 flex items-center justify-center", accentMap[accent])}>
          <I width="18" height="18"/>
        </div>
        <div className="text-right">
          <div className="text-[28px] font-semibold num-tabular leading-none">{count}</div>
          <div className="text-[10px] uppercase tracking-wider text-white/40 mt-1">issues</div>
        </div>
      </div>
      <div className="mt-4">
        <div className="text-[15px] font-semibold tracking-tight">{title}</div>
        <div className="text-[12px] text-white/45 mt-0.5">{sub}</div>
      </div>
      <div className="mt-4 space-y-1.5">
        {detail.map((d, i) => (
          <div key={i} className="flex items-center gap-2 glass-thin rounded-lg px-2.5 py-1.5">
            <span className={cls("w-1.5 h-1.5 rounded-full shrink-0",
              d.severity === "critical" ? "bg-rose-500"
              : d.severity === "high"   ? "bg-amber-500"
              : d.severity === "medium" ? "bg-amber-400"
              : d.severity === "low"    ? "bg-mint-500"
              : "bg-accent-500"
            )}/>
            <div className="min-w-0">
              <div className="text-[12px] truncate">{d.label}</div>
              {d.hint && <div className="text-[10.5px] text-white/40 font-mono truncate">{d.hint}</div>}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

/* ============================== FINDINGS EXPLORER ============================== */
function FindingsExplorer({ result }) {
  if (!result) return null;
  const all = useMemo(() => {
    const a = [];
    result.secrets_found.forEach(s => a.push({
      type: "secret", severity: s.severity,
      title: s.pattern_name, message: s.reason,
      file_path: s.file_path, line_number: s.line_number,
      meta: { confidence: s.confidence, entropy: s.entropy, matched: s.matched_text, context: s.context },
    }));
    (result.readme_result?.issues || []).forEach(i => a.push({
      type: "readme", severity: i.severity, title: "README", message: i.message,
      file_path: i.file_path, line_number: i.line_number, meta: {},
    }));
    (result.prompt_result?.issues || []).forEach(i => a.push({
      type: "prompt", severity: i.severity, title: "Prompt", message: i.message,
      file_path: i.file_path, line_number: i.line_number,
      meta: { missing: result.prompt_result?.missing_fields?.[i.file_path] },
    }));
    return a;
  }, [result]);

  const [type, setType] = useState("all");
  const [sev,  setSev]  = useState("all");
  const [q,    setQ]    = useState("");
  const [open, setOpen] = useState(null);

  const filtered = all.filter(i =>
    (type === "all" || i.type === type) &&
    (sev  === "all" || i.severity === sev) &&
    (q.trim() === "" || (i.file_path||"").toLowerCase().includes(q.toLowerCase()) || i.message.toLowerCase().includes(q.toLowerCase()) || i.title.toLowerCase().includes(q.toLowerCase()))
  );

  const Tabs = ({ items, value, onChange }) => (
    <div className="glass-thin rounded-xl p-1 flex">
      {items.map(([k, label, n]) => (
        <button key={k} onClick={() => onChange(k)}
          className={cls(
            "px-3 py-1.5 rounded-lg text-[12px] flex items-center gap-2 transition",
            value === k ? "bg-white/10 text-white" : "text-white/55 hover:text-white"
          )}>
          {label}{typeof n === "number" && <span className="text-[10.5px] font-mono text-white/45">{n}</span>}
        </button>
      ))}
    </div>
  );

  return (
    <section id="findings" className="relative px-6 py-16">
      <div className="max-w-7xl mx-auto">
        <SectionHeader
          eyebrow="04 · Explorer"
          title="Every finding, sliced and sortable."
          sub="Filter by module and severity, search across files, then expand any row for context, entropy, and confidence."
        />
        <div className="mt-8 glass-strong rounded-3xl overflow-hidden">
          <div className="p-4 border-b border-white/[0.06] flex flex-col lg:flex-row gap-3 lg:items-center">
            <Tabs value={type} onChange={setType} items={[
              ["all",      "All",       all.length],
              ["secret",   "Secrets",   all.filter(i => i.type === "secret").length],
              ["readme",   "README",    all.filter(i => i.type === "readme").length],
              ["prompt",   "Prompts",   all.filter(i => i.type === "prompt").length],
            ]}/>
            <Tabs value={sev} onChange={setSev} items={[
              ["all", "Any severity"],
              ["critical","Critical"],
              ["high","High"],
              ["medium","Medium"],
              ["low","Low"],
              ["info","Info"],
            ]}/>
            <div className="flex-1"/>
            <div className="glass-thin rounded-xl flex items-center gap-2 px-3 py-2 min-w-[220px]">
              <Icon.Search width="14" height="14" className="text-white/45"/>
              <input value={q} onChange={(e) => setQ(e.target.value)} placeholder="Search file or message"
                className="bg-transparent outline-none text-[13px] flex-1 placeholder:text-white/30"/>
              {q && <button onClick={() => setQ("")} className="text-white/45 hover:text-white"><Icon.X width="13" height="13"/></button>}
            </div>
          </div>

          <div className="divide-y divide-white/[0.04] max-h-[640px] overflow-y-auto scroll-fade-mask">
            {filtered.length === 0 && (
              <div className="p-12 text-center">
                <div className="inline-flex w-12 h-12 rounded-2xl glass-thin items-center justify-center mb-3">
                  <Icon.Check width="18" height="18" className="text-mint-400"/>
                </div>
                <div className="text-[15px] font-semibold">All clear</div>
                <div className="text-[12px] text-white/45 mt-1">No findings match your filters.</div>
              </div>
            )}
            {filtered.map((i, idx) => (
              <FindingRow key={idx} i={i} open={open === idx} onToggle={() => setOpen(open === idx ? null : idx)}/>
            ))}
          </div>

          <div className="p-3 border-t border-white/[0.06] flex items-center justify-between text-[11px] text-white/45">
            <div>Showing {filtered.length} of {all.length}</div>
            <div className="font-mono">type: {type} · severity: {sev}</div>
          </div>
        </div>
      </div>
    </section>
  );
}
function FindingRow({ i, open, onToggle }) {
  const TypeIcon = i.type === "secret" ? Icon.Key : i.type === "readme" ? Icon.Book : Icon.Spark;
  return (
    <div>
      <button onClick={onToggle} className="w-full text-left px-5 py-4 flex items-start gap-4 hover:bg-white/[0.025] transition">
        <span className={cls("px-2 py-0.5 rounded-md text-[10.5px] uppercase tracking-wider font-medium shrink-0 mt-0.5", `severity-${i.severity}`)}>
          {i.severity}
        </span>
        <div className="w-7 h-7 rounded-lg glass-thin flex items-center justify-center shrink-0 mt-0.5">
          <TypeIcon width="13" height="13" className="text-white/65"/>
        </div>
        <div className="flex-1 min-w-0">
          <div className="flex items-baseline gap-2 flex-wrap">
            <span className="text-[14px] font-medium">{i.title}</span>
            <span className="text-[12px] text-white/55">{i.message}</span>
          </div>
          <div className="text-[11.5px] text-white/40 font-mono mt-0.5 truncate">
            {i.file_path || "—"}{i.line_number ? `:${i.line_number}` : ""}
          </div>
        </div>
        <span className={cls("text-white/40 transition-transform shrink-0", open && "rotate-180")}>
          <Icon.Down width="14" height="14"/>
        </span>
      </button>
      {open && (
        <div className="px-5 pb-5">
          <div className="glass-thin rounded-xl p-4 space-y-3">
            {i.type === "secret" && (
              <>
                <div className="grid sm:grid-cols-3 gap-3">
                  <Stat label="Confidence" value={`${Math.round((i.meta.confidence||0) * 100)}%`}/>
                  <Stat label="Entropy"    value={(i.meta.entropy ?? 0).toFixed(2)}/>
                  <Stat label="Verified"   value="No"/>
                </div>
                <div>
                  <div className="text-[10px] uppercase tracking-wider text-white/40 mb-1.5">Matched (masked)</div>
                  <code className="block text-[12px] font-mono text-amber-300 break-all glass-thin px-3 py-2 rounded-lg">{i.meta.matched}</code>
                </div>
                <div>
                  <div className="text-[10px] uppercase tracking-wider text-white/40 mb-1.5">Context</div>
                  <code className="block text-[12px] font-mono text-white/75 break-all glass-thin px-3 py-2 rounded-lg">{i.meta.context}</code>
                </div>
              </>
            )}
            {i.type === "prompt" && i.meta.missing && (
              <div>
                <div className="text-[10px] uppercase tracking-wider text-white/40 mb-1.5">Missing fields</div>
                <div className="flex flex-wrap gap-1.5">
                  {i.meta.missing.map(f => (
                    <span key={f} className="text-[11px] font-mono px-2 py-0.5 rounded-md severity-high">{f}</span>
                  ))}
                </div>
              </div>
            )}
            {i.type === "readme" && (
              <div className="text-[12.5px] text-white/65">{i.message}. Add this section to your <span className="font-mono text-white/85">README.md</span> to recover the deduction.</div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
function Stat({ label, value }) {
  return (
    <div className="glass-thin rounded-lg px-3 py-2">
      <div className="text-[10px] uppercase tracking-wider text-white/40">{label}</div>
      <div className="text-[14px] font-semibold num-tabular mt-0.5">{value}</div>
    </div>
  );
}

/* ============================== REPORT SECTION ============================== */
function ReportSection({ result, uploadId, toast }) {
  const [format, setFormat] = useState("md");
  const [busy, setBusy]     = useState(false);

  const md = useMemo(() => result ? buildMarkdown(result) : "", [result]);

  const download = async () => {
    if (!uploadId) {
      // local-mock download
      const blob = new Blob([md], { type: "text/markdown" });
      triggerDownload(blob, `policypilot_report_${(result?.project_name||"report").replace(/\s+/g,"_")}.md`);
      toast("success", "Report downloaded");
      return;
    }
    setBusy(true);
    try {
      const res = await fetch(`${API_BASE}/api/report/${uploadId}/${format}`);
      if (!res.ok) {
        const blob = new Blob([md], { type: "text/markdown" });
        triggerDownload(blob, `policypilot_report_${uploadId}.md`);
        toast("success", "Downloaded local copy");
        return;
      }
      const blob = await res.blob();
      triggerDownload(blob, `policypilot_report_${uploadId}.${format}`);
      toast("success", "Report downloaded");
    } catch {
      const blob = new Blob([md], { type: "text/markdown" });
      triggerDownload(blob, `policypilot_report.md`);
      toast("success", "Downloaded local copy");
    } finally { setBusy(false); }
  };

  const copyMd = async () => {
    try { await navigator.clipboard.writeText(md); toast("success", "Markdown copied to clipboard"); }
    catch { toast("error", "Could not copy"); }
  };

  return (
    <section id="report" className="relative px-6 py-16">
      <div className="max-w-7xl mx-auto">
        <SectionHeader
          eyebrow="05 · Export"
          title="Reports your auditors will actually read."
          sub="Download as Markdown, JSON, or styled HTML — all generated from the same analysis result."
          right={
            <div className="hidden md:flex items-center gap-2">
              <FormatTab value={format} onChange={setFormat} k="md"   label="Markdown"/>
              <FormatTab value={format} onChange={setFormat} k="json" label="JSON"/>
              <FormatTab value={format} onChange={setFormat} k="html" label="HTML"/>
            </div>
          }
        />

        <div className="mt-8 grid lg:grid-cols-12 gap-6">
          <div className="lg:col-span-5 space-y-4">
            <div className="glass-strong rounded-3xl p-6">
              <div className="flex items-center justify-between">
                <div>
                  <div className="text-[11px] uppercase tracking-[0.18em] text-white/45">Selected format</div>
                  <div className="text-[20px] font-semibold tracking-tight mt-1">
                    {format === "md" ? "Markdown" : format === "json" ? "JSON" : "HTML"}
                  </div>
                </div>
                <div className={cls("w-10 h-10 rounded-xl flex items-center justify-center",
                  format === "md" ? "bg-mint-500/15 text-mint-400 border border-mint-500/30"
                  : format === "json" ? "bg-accent-500/15 text-accent-400 border border-accent-500/30"
                  : "bg-amber-500/15 text-amber-400 border border-amber-500/30")}>
                  <Icon.Code width="18" height="18"/>
                </div>
              </div>
              <p className="mt-3 text-[13px] text-white/55 leading-relaxed">
                {format === "md"   && "Human-readable, version-control friendly. Includes progress bars, severity emojis, and code blocks. Ideal for GitHub PRs."}
                {format === "json" && "Machine-readable, complete data export. Use it for ETL, dashboards, or archival in your data lake."}
                {format === "html" && "Self-contained, styled report. Color-coded severity levels and responsive cards — perfect for sharing."}
              </p>
              <div className="mt-5 flex flex-wrap gap-2">
                <button onClick={download} disabled={busy || !result}
                  className={cls("px-4 py-2.5 rounded-xl text-[13px] font-semibold flex items-center gap-2",
                    !result ? "bg-white/[0.06] text-white/35 cursor-not-allowed" : "btn-primary"
                  )}>
                  {busy ? <span className="w-3.5 h-3.5 border-2 border-current border-t-transparent rounded-full animate-spin"/> : <Icon.Down width="14" height="14"/>}
                  Download .{format}
                </button>
                <button onClick={copyMd} disabled={!result} className="btn-ghost px-4 py-2.5 rounded-xl text-[13px] font-medium flex items-center gap-2 text-white/85 disabled:opacity-50">
                  <Icon.Copy width="14" height="14"/> Copy markdown
                </button>
              </div>
              <div className="mt-4 text-[11px] text-white/40 font-mono break-all">
                GET /api/report/{uploadId || "<id>"}/{format}
              </div>
            </div>

            <div className="glass rounded-3xl p-5">
              <div className="text-[11px] uppercase tracking-[0.18em] text-white/45 mb-3">Recommendations</div>
              <ul className="space-y-2.5">
                {(result ? buildRecs(result) : ["Upload a project to see tailored recommendations."]).map((r, i) => (
                  <li key={i} className="flex items-start gap-2.5 text-[13px] text-white/75">
                    <span className="mt-1 w-1.5 h-1.5 rounded-full bg-accent-500 shrink-0"/>
                    <span>{r}</span>
                  </li>
                ))}
              </ul>
            </div>
          </div>

          <div className="lg:col-span-7">
            <div className="glass-strong rounded-3xl overflow-hidden h-full flex flex-col">
              <div className="px-4 py-2.5 border-b border-white/[0.06] flex items-center gap-2 text-[11px] text-white/55">
                <span className="w-2 h-2 rounded-full bg-rose-500/70"/>
                <span className="w-2 h-2 rounded-full bg-amber-500/70"/>
                <span className="w-2 h-2 rounded-full bg-mint-500/70"/>
                <span className="ml-2 font-mono">policypilot_report.{format}</span>
                <div className="ml-auto flex gap-1">
                  <FormatTab value={format} onChange={setFormat} k="md"   label="md" small/>
                  <FormatTab value={format} onChange={setFormat} k="json" label="json" small/>
                  <FormatTab value={format} onChange={setFormat} k="html" label="html" small/>
                </div>
              </div>
              <div className="p-4 sm:p-6 overflow-auto flex-1 max-h-[640px] scroll-fade-mask">
                {format === "md"   && <MarkdownPreview text={md}/>}
                {format === "json" && <pre className="text-[12px] font-mono text-white/80 whitespace-pre-wrap break-words leading-relaxed">{result ? JSON.stringify(reportToJson(result), null, 2) : "// Run an analysis to populate this report"}</pre>}
                {format === "html" && <HtmlPreview result={result}/>}
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
function FormatTab({ value, onChange, k, label, small }) {
  return (
    <button onClick={() => onChange(k)}
      className={cls(
        "rounded-lg transition",
        small ? "px-2 py-1 text-[11px]" : "px-3 py-1.5 text-[12px]",
        value === k ? "bg-white/10 text-white" : "glass-thin text-white/55 hover:text-white"
      )}>{label}</button>
  );
}
function triggerDownload(blob, name) {
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url; a.download = name; a.click();
  setTimeout(() => URL.revokeObjectURL(url), 1500);
}

/* Tiny markdown renderer (headings, code blocks, lists, bold, inline code, tables-as-pre) */
function MarkdownPreview({ text }) {
  const lines = text.split("\n");
  const out = []; let i = 0;
  while (i < lines.length) {
    const ln = lines[i];
    if (ln.startsWith("```")) {
      const start = i + 1; let j = start;
      while (j < lines.length && !lines[j].startsWith("```")) j++;
      out.push(<pre key={i} className="font-mono text-[12px] glass-thin rounded-lg p-3 my-3 overflow-x-auto text-white/80 whitespace-pre">{lines.slice(start, j).join("\n")}</pre>);
      i = j + 1; continue;
    }
    if (ln.startsWith("# "))   out.push(<h1 key={i} className="text-[24px] font-semibold mt-2 mb-3 tracking-tight">{ln.slice(2)}</h1>);
    else if (ln.startsWith("## "))  out.push(<h2 key={i} className="text-[18px] font-semibold mt-5 mb-2 text-white/90">{ln.slice(3)}</h2>);
    else if (ln.startsWith("### ")) out.push(<h3 key={i} className="text-[14px] font-semibold mt-4 mb-1.5 text-accent-400">{ln.slice(4)}</h3>);
    else if (ln.startsWith("- "))   out.push(<div key={i} className="text-[13px] text-white/75 leading-relaxed pl-4 relative before:content-['•'] before:absolute before:left-1 before:text-white/40">{inlineMd(ln.slice(2))}</div>);
    else if (ln.trim() === "")      out.push(<div key={i} className="h-2"/>);
    else out.push(<p key={i} className="text-[13px] text-white/70 leading-relaxed my-1">{inlineMd(ln)}</p>);
    i++;
  }
  return <div>{out}</div>;
}
function inlineMd(s) {
  // very small inline parser: **bold**, `code`
  const parts = []; let buf = ""; let i = 0;
  while (i < s.length) {
    if (s[i] === "*" && s[i+1] === "*") {
      const end = s.indexOf("**", i + 2);
      if (end > -1) { if (buf) { parts.push(buf); buf = ""; }
        parts.push(<strong key={i} className="text-white">{s.slice(i+2, end)}</strong>); i = end + 2; continue; }
    }
    if (s[i] === "`") {
      const end = s.indexOf("`", i + 1);
      if (end > -1) { if (buf) { parts.push(buf); buf = ""; }
        parts.push(<code key={i} className="font-mono text-[12px] text-amber-300 bg-white/[0.05] px-1.5 py-0.5 rounded">{s.slice(i+1, end)}</code>); i = end + 1; continue; }
    }
    buf += s[i++];
  }
  if (buf) parts.push(buf);
  return parts;
}
function HtmlPreview({ result }) {
  if (!result) return <div className="text-white/45 text-[13px]">Run an analysis to preview the styled HTML report.</div>;
  const grade = gradeFromScore(result.total_score);
  const status = statusFromScore(result.total_score);
  return (
    <div className="rounded-xl border border-white/[0.06] overflow-hidden">
      <div className="bg-gradient-to-br from-accent-500/15 to-mint-500/10 p-6">
        <div className="text-[11px] uppercase tracking-[0.22em] text-white/55">Compliance report</div>
        <div className="text-[28px] font-semibold tracking-tight mt-1">{result.project_name}</div>
        <div className="mt-4 flex items-center gap-3">
          <div className="text-[44px] font-semibold num-tabular leading-none">{result.total_score.toFixed(1)}</div>
          <div className="space-y-1">
            <span className="px-2 py-0.5 rounded-md text-[11px] font-mono glass-thin">grade {grade}</span><br/>
            <span className={cls("px-2 py-0.5 rounded-md text-[11px]",
              status === "PASS" && "severity-low",
              status === "WARNING" && "severity-high",
              status === "FAIL" && "severity-critical"
            )}>{status}</span>
          </div>
        </div>
      </div>
      <div className="p-5 space-y-4">
        <div>
          <div className="text-[12px] uppercase tracking-wider text-white/45 mb-2">Module scores</div>
          <table className="w-full text-[12.5px]">
            <thead className="text-white/45 text-[11px] uppercase">
              <tr>
                <th className="text-left font-medium pb-2">Module</th>
                <th className="text-right font-medium pb-2">Score</th>
                <th className="text-right font-medium pb-2">Weight</th>
                <th className="text-right font-medium pb-2">Issues</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-white/[0.05]">
              {result.module_scores.map((m, i) => (
                <tr key={i}>
                  <td className="py-2">{m.name}</td>
                  <td className="text-right font-mono num-tabular">{m.score.toFixed(1)}</td>
                  <td className="text-right font-mono num-tabular text-white/55">{Math.round(m.weight*100)}%</td>
                  <td className="text-right font-mono num-tabular">{m.issues_count}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

/* Build representations from result */
function buildMarkdown(r) {
  const grade = gradeFromScore(r.total_score);
  const status = statusFromScore(r.total_score);
  const bar = (n) => {
    const filled = Math.round((n / 100) * 20);
    return "▰".repeat(filled) + "▱".repeat(20 - filled);
  };
  const sevEmoji = { critical: "🛑", high: "⚠️", medium: "🟡", low: "🟢", info: "ℹ️" };
  const lines = [];
  lines.push(`# PolicyPilot Compliance Report`);
  lines.push("");
  lines.push(`**Project:** ${r.project_name}`);
  lines.push(`**Generated:** ${new Date(r.timestamp).toLocaleString()}`);
  lines.push(`**Files analyzed:** ${r.files_analyzed}`);
  lines.push("");
  lines.push(`## Summary`);
  lines.push(`- Score: **${r.total_score.toFixed(1)} / 100** (grade **${grade}**, status **${status}**)`);
  lines.push(`- Total issues: **${r.total_issues}**, critical: **${r.critical_issues}**`);
  lines.push("");
  lines.push(`## Module breakdown`);
  lines.push("");
  lines.push("```");
  r.module_scores.forEach(m => {
    lines.push(`${m.name.padEnd(22)} ${bar(m.score)}  ${m.score.toFixed(1).padStart(5)}  (w ${Math.round(m.weight*100)}%)`);
  });
  lines.push("```");
  lines.push("");
  if (r.secrets_found.length) {
    lines.push(`## Secrets detected`);
    r.secrets_found.forEach(s => {
      lines.push(`- ${sevEmoji[s.severity] || ""} **${s.pattern_name}** in \`${s.file_path}:${s.line_number}\` — confidence ${(s.confidence*100).toFixed(0)}%`);
    });
    lines.push("");
  }
  if (r.readme_result) {
    lines.push(`## README`);
    lines.push(`- Word count: ${r.readme_result.word_count}, score ${r.readme_result.score.toFixed(1)}`);
    if (r.readme_result.missing_required?.length)    lines.push(`- Missing required: ${r.readme_result.missing_required.map(s=>"`"+s+"`").join(", ")}`);
    if (r.readme_result.missing_recommended?.length) lines.push(`- Missing recommended: ${r.readme_result.missing_recommended.map(s=>"`"+s+"`").join(", ")}`);
    lines.push("");
  }
  if (r.prompt_result) {
    lines.push(`## Prompt documentation`);
    lines.push(`- Documented: ${r.prompt_result.documented_prompts} of ${r.prompt_result.total_prompts}`);
    Object.entries(r.prompt_result.missing_fields || {}).forEach(([f, fs]) => lines.push(`- \`${f}\` missing: ${fs.map(x=>"`"+x+"`").join(", ")}`));
    lines.push("");
  }
  lines.push(`## Recommendations`);
  buildRecs(r).forEach(x => lines.push(`- ${x}`));
  return lines.join("\n");
}
function buildRecs(r) {
  const recs = [];
  if (r.critical_issues > 0) recs.push("Rotate any exposed credentials immediately and purge them from git history.");
  if ((r.readme_result?.missing_required || []).length) recs.push(`Add ${r.readme_result.missing_required.join(", ")} section${r.readme_result.missing_required.length>1?"s":""} to README.md.`);
  if ((r.readme_result?.word_count ?? 0) < 200) recs.push("Expand the README with usage examples and configuration notes.");
  if (r.prompt_result && r.prompt_result.documented_prompts < r.prompt_result.total_prompts) recs.push("Document remaining prompts with example, constraints, and expected outputs.");
  if (r.module_scores.some(m => m.name === "Project Structure" && m.score < 100)) recs.push("Restore conventional folder layout: src/, tests/, prompts/.");
  if (recs.length === 0) recs.push("Compliance is solid. Keep secrets out of source — consider pre-commit gitleaks.");
  return recs;
}
function reportToJson(r) {
  return {
    metadata: { project_name: r.project_name, generated_at: new Date().toISOString(), generator_version: "1.0.0", analysis_timestamp: r.timestamp },
    summary: { total_score: r.total_score, grade: gradeFromScore(r.total_score), status: statusFromScore(r.total_score), passed: r.passed, total_issues: r.total_issues, critical_issues: r.critical_issues, files_analyzed: r.files_analyzed },
    scores: { modules: r.module_scores },
    secrets: { total_found: r.secrets_found.length, details: r.secrets_found },
    readme: r.readme_result, prompts: r.prompt_result,
  };
}

/* ============================== EMPTY STATE ============================== */
function EmptyState({ id, title, sub }) {
  return (
    <section id={id} className="px-6 py-16">
      <div className="max-w-7xl mx-auto">
        <div className="glass rounded-3xl p-10 text-center">
          <div className="inline-flex w-12 h-12 rounded-2xl glass-thin items-center justify-center mb-3">
            <Icon.Spark width="18" height="18" className="text-white/55"/>
          </div>
          <div className="text-[18px] font-semibold tracking-tight">{title}</div>
          <div className="text-[13px] text-white/50 mt-1.5 max-w-md mx-auto">{sub}</div>
        </div>
      </div>
    </section>
  );
}

/* ============================== FOOTER ============================== */
function Footer() {
  const cols = [
    ["Product", ["Overview","Pricing","Changelog","Roadmap"]],
    ["Modules", ["Secret Scanner","README Validator","Prompt Docs","Project Structure"]],
    ["Resources", ["Docs","API reference","Self-hosting","Status"]],
    ["Company", ["About","Security","Privacy","Contact"]],
  ];
  return (
    <footer className="relative px-6 pt-20 pb-8">
      <div className="max-w-7xl mx-auto">
        <div className="glass-strong rounded-3xl p-8 sm:p-10 grid lg:grid-cols-12 gap-8">
          <div className="lg:col-span-4">
            <div className="flex items-center gap-2.5">
              <Icon.Logo width="28" height="28"/>
              <div className="leading-tight">
                <div className="text-[16px] font-semibold tracking-tight">PolicyPilot</div>
                <div className="text-[10px] uppercase tracking-[0.18em] text-white/40">Compliance OS</div>
              </div>
            </div>
            <p className="mt-4 text-white/55 text-[13px] leading-relaxed max-w-sm">
              Pre-flight compliance for codebases. Scan secrets, validate docs, and grade prompts in seconds — no agent, no auth, no friction.
            </p>
            <div className="mt-5 flex items-center gap-2 text-[12px] text-white/55">
              <span className="w-1.5 h-1.5 rounded-full bg-mint-500 pulse-dot"/>
              All systems operational · v1.0.0
            </div>
          </div>
          <div className="lg:col-span-8 grid grid-cols-2 sm:grid-cols-4 gap-6">
            {cols.map(([h, items]) => (
              <div key={h}>
                <div className="text-[11px] uppercase tracking-[0.18em] text-white/45 mb-3">{h}</div>
                <ul className="space-y-2">
                  {items.map(x => <li key={x}><a className="text-[13px] text-white/70 hover:text-white" href="#">{x}</a></li>)}
                </ul>
              </div>
            ))}
          </div>
        </div>
        <div className="mt-6 flex flex-col sm:flex-row items-center justify-between gap-3 text-[11.5px] text-white/40">
          <div>© 2026 PolicyPilot Labs. Original design — not affiliated with any third party.</div>
          <div className="flex items-center gap-4 font-mono">
            <span>SOC2 ready</span><span>·</span><span>GDPR</span><span>·</span><span>ISO 27001</span>
          </div>
        </div>
      </div>
    </footer>
  );
}

/* ============================== APP ============================== */
function App() {
  const [files, setFiles]               = useState([]);
  const [projectName, setProjectName]   = useState("acme-llm-orchestrator");
  const [uploadId, setUploadId]         = useState(null);
  const [result, setResult]             = useState(null);
  const [busy, setBusy]                 = useState(false);
  const [status, setStatus]             = useState("");
  const { list: toasts, push: toast }   = useToasts();

  const jump = (id) => {
    const el = document.getElementById(id);
    if (el) {
      const y = el.getBoundingClientRect().top + window.scrollY - 80;
      window.scrollTo({ top: y, behavior: "smooth" });
    }
  };

  const onAnalyze = async () => {
    if (files.length === 0) { toast("error", "Select files first"); return; }
    setBusy(true); setStatus("upload");
    try {
      // upload
      const fd = new FormData();
      files.forEach(f => fd.append("files", f));
      fd.append("project_name", projectName || "Unnamed Project");

      let analysis;
      try {
        const res = await fetch(`${API_BASE}/api/upload-and-analyze`, { method: "POST", body: fd });
        if (!res.ok) throw new Error("upload-and-analyze failed");
        analysis = await res.json();
        setUploadId(analysis?.upload_id || crypto.randomUUID());
      } catch {
        // mock fallback — simulate stage-by-stage progress
        await stageDelay(setStatus, "secrets", 600);
        await stageDelay(setStatus, "readme",  500);
        await stageDelay(setStatus, "prompts", 500);
        await stageDelay(setStatus, "score",   500);
        analysis = mockAnalysis(projectName, files);
        setUploadId(crypto.randomUUID());
      }
      setResult(analysis);
      toast("success", `Score ${analysis.total_score.toFixed(1)} · ${statusFromScore(analysis.total_score)}`);
      setTimeout(() => jump("score"), 100);
    } catch (e) {
      toast("error", "Analysis failed. Showing local example.");
      setResult(mockAnalysis(projectName, files));
      setUploadId(crypto.randomUUID());
    } finally {
      setBusy(false); setStatus("");
    }
  };

  return (
    <>
      <Navbar onJump={jump}/>
      <ToastHost toasts={toasts}/>
      <Hero onJump={jump}/>
      <UploadPanel
        files={files} setFiles={setFiles}
        projectName={projectName} setProjectName={setProjectName}
        uploadId={uploadId} setUploadId={setUploadId}
        onAnalyze={onAnalyze} busy={busy} status={status} toast={toast}
      />
      <ScoreSection result={result}/>
      <IssueSummary result={result}/>
      {result ? <FindingsExplorer result={result}/> : <EmptyState id="findings" title="Findings explorer awaits" sub="Upload files and run an analysis to populate the searchable findings table."/>}
      <ReportSection result={result} uploadId={uploadId} toast={toast}/>
      <Footer/>
    </>
  );
}

function stageDelay(setStatus, stage, ms) {
  setStatus(stage);
  return new Promise(r => setTimeout(r, ms));
}

ReactDOM.createRoot(document.getElementById("root")).render(<App/>);
