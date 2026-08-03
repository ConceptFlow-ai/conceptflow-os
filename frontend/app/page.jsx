'use client';

import { useCallback, useRef, useState } from "react";
import { Upload, FileText, Loader2, CheckCircle2, X, AlertCircle, ArrowRight } from "lucide-react";

/**
 * ConceptFlow.ai — document upload
 * Flow: choose PDF -> upload -> POST /api/documents/upload -> loading -> success
 *
 * Signature element: a small node network sits behind the dropzone. It's inert
 * while idle, then "assembles" in step with real upload progress — nodes light
 * up and edges draw in as bytes go out, so the one moving part in the UI is
 * literally a preview of the concept graph the upload is about to produce.
 */

const NODES = [
  { x: 40, y: 20 }, { x: 110, y: 12 }, { x: 175, y: 34 },
  { x: 25, y: 70 }, { x: 95, y: 66 }, { x: 160, y: 78 },
  { x: 60, y: 108 }, { x: 130, y: 112 },
];

const EDGES = [
  [0, 1], [1, 2], [0, 3], [1, 4], [2, 5],
  [3, 4], [4, 5], [3, 6], [4, 7], [6, 7], [5, 7],
];

function GraphGlyph({ progress, done }) {
  const active = done ? EDGES.length : Math.floor((progress / 100) * EDGES.length);
  const activeNodes = done
    ? NODES.length
    : Math.min(NODES.length, Math.ceil((progress / 100) * NODES.length) + 1);

  return (
    <svg viewBox="0 0 200 130" className="h-28 w-full" aria-hidden="true">
      {EDGES.map(([a, b], i) => {
        const on = i < active;
        return (
          <line
            key={i}
            x1={NODES[a].x} y1={NODES[a].y}
            x2={NODES[b].x} y2={NODES[b].y}
            stroke={on ? "#22D3AA" : "#232B35"}
            strokeWidth={on ? 1.4 : 1}
            className="transition-all duration-500 ease-out"
            style={{ opacity: on ? 0.9 : 0.5 }}
          />
        );
      })}
      {NODES.map((n, i) => {
        const on = i < activeNodes;
        return (
          <circle
            key={i}
            cx={n.x} cy={n.y}
            r={on ? 5 : 3.5}
            fill={on ? "#6E56CF" : "#1B2229"}
            stroke={on ? "#B7A9F2" : "#2C3542"}
            strokeWidth="1"
            className="transition-all duration-500 ease-out"
          />
        );
      })}
    </svg>
  );
}

function formatSize(bytes) {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(0)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

export default function DocumentUpload() {
  const [stage, setStage] = useState("idle"); // idle | selected | uploading | success | error
  const [file, setFile] = useState(null);
  const [progress, setProgress] = useState(0);
  const [errorMsg, setErrorMsg] = useState("");
  const [dragOver, setDragOver] = useState(false);
  const inputRef = useRef(null);
  const xhrRef = useRef(null);

  const pickFile = useCallback((f) => {
    if (!f) return;
    if (f.type !== "application/pdf") {
      setStage("error");
      setErrorMsg("Only PDF files are supported right now.");
      return;
    }
    setFile(f);
    setStage("selected");
    setErrorMsg("");
  }, []);

  const reset = () => {
    setStage("idle");
    setFile(null);
    setProgress(0);
    setErrorMsg("");
  };

  const upload = () => {
    if (!file) return;
    setStage("uploading");
    setProgress(0);

    const form = new FormData();
    form.append("file", file);

    const xhr = new XMLHttpRequest();
    xhrRef.current = xhr;
    xhr.open("POST", "/api/documents/upload");

    xhr.upload.onprogress = (e) => {
      if (e.lengthComputable) {
        setProgress(Math.round((e.loaded / e.total) * 100));
      }
    };
    xhr.onload = () => {
      if (xhr.status >= 200 && xhr.status < 300) {
        setProgress(100);
        setStage("success");
      } else {
        setErrorMsg(`Upload failed (${xhr.status}). Try again.`);
        setStage("error");
      }
    };
    xhr.onerror = () => {
      setErrorMsg("Couldn't reach the server. Check your connection.");
      setStage("error");
    };
    xhr.send(form);
  };

  const cancelUpload = () => {
    xhrRef.current?.abort();
    reset();
  };

  return (
    <div
      className="mx-auto w-full max-w-md rounded-2xl border p-6"
      style={{ background: "#12181F", borderColor: "#232B35" }}
    >
      <div className="mb-5 flex items-center justify-between">
        <div>
          <p
            className="text-[15px] font-medium tracking-tight"
            style={{ color: "#E7ECF2", fontFamily: "'Space Grotesk', sans-serif" }}
          >
            Add a source
          </p>
          <p className="text-[13px]" style={{ color: "#8B95A1" }}>
            ConceptFlow turns this PDF into a concept graph
          </p>
        </div>
        {stage !== "idle" && (
          <button
            onClick={reset}
            aria-label="Start over"
            className="rounded-lg p-1.5 transition-colors hover:bg-white/5"
          >
            <X className="h-4 w-4" style={{ color: "#8B95A1" }} />
          </button>
        )}
      </div>

      <div
        className="relative overflow-hidden rounded-xl border"
        style={{
          borderColor: dragOver ? "#6E56CF" : "#232B35",
          borderStyle: stage === "idle" ? "dashed" : "solid",
          background: "#0B0F14",
        }}
      >
        <div className="px-5 pt-5">
          <GraphGlyph progress={progress} done={stage === "success"} />
        </div>

        <div className="px-5 pb-5 pt-1">
          {stage === "idle" && (
            <div
              onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
              onDragLeave={() => setDragOver(false)}
              onDrop={(e) => {
                e.preventDefault();
                setDragOver(false);
                pickFile(e.dataTransfer.files?.[0]);
              }}
              className="flex flex-col items-center gap-3 py-2 text-center"
            >
              <p className="text-[13px]" style={{ color: "#8B95A1" }}>
                Drop a PDF here, or
              </p>
              <button
                onClick={() => inputRef.current?.click()}
                className="inline-flex items-center gap-2 rounded-lg px-4 py-2 text-[13px] font-medium transition-colors"
                style={{ background: "#1B2229", color: "#E7ECF2", border: "1px solid #2C3542" }}
              >
                <Upload className="h-3.5 w-3.5" />
                Choose PDF
              </button>
              <input
                ref={inputRef}
                type="file"
                accept="application/pdf"
                className="hidden"
                onChange={(e) => pickFile(e.target.files?.[0])}
              />
            </div>
          )}

          {(stage === "selected" || stage === "uploading" || stage === "success") && file && (
            <div className="flex items-center gap-3 py-2">
              <div
                className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg"
                style={{ background: "#1B2229" }}
              >
                <FileText className="h-4 w-4" style={{ color: "#6E56CF" }} />
              </div>
              <div className="min-w-0 flex-1">
                <p className="truncate text-[13px] font-medium" style={{ color: "#E7ECF2" }}>
                  {file.name}
                </p>
                <p className="text-[12px]" style={{ color: "#8B95A1" }}>
                  {formatSize(file.size)}
                  {stage === "uploading" && ` · ${progress}%`}
                  {stage === "success" && " · uploaded"}
                </p>
              </div>
              {stage === "success" && (
                <CheckCircle2 className="h-5 w-5 shrink-0" style={{ color: "#22D3AA" }} />
              )}
            </div>
          )}

          {stage === "error" && (
            <div className="flex items-start gap-3 py-2">
              <AlertCircle className="h-5 w-5 shrink-0" style={{ color: "#E2725B" }} />
              <p className="text-[13px]" style={{ color: "#E7ECF2" }}>{errorMsg}</p>
            </div>
          )}

          {stage === "uploading" && (
            <div className="mt-1 h-1 w-full overflow-hidden rounded-full" style={{ background: "#1B2229" }}>
              <div
                className="h-full rounded-full transition-all duration-200 ease-out"
                style={{ width: `${progress}%`, background: "linear-gradient(90deg, #6E56CF, #22D3AA)" }}
              />
            </div>
          )}
        </div>
      </div>

      <div className="mt-4 flex justify-end gap-2">
        {stage === "selected" && (
          <>
            <button
              onClick={reset}
              className="rounded-lg px-4 py-2 text-[13px] font-medium transition-colors hover:bg-white/5"
              style={{ color: "#8B95A1" }}
            >
              Cancel
            </button>
            <button
              onClick={upload}
              className="inline-flex items-center gap-1.5 rounded-lg px-4 py-2 text-[13px] font-medium text-white transition-opacity hover:opacity-90"
              style={{ background: "#6E56CF" }}
            >
              Upload
            </button>
          </>
        )}

        {stage === "uploading" && (
          <button
            onClick={cancelUpload}
            className="inline-flex items-center gap-1.5 rounded-lg px-4 py-2 text-[13px] font-medium transition-colors hover:bg-white/5"
            style={{ color: "#8B95A1" }}
          >
            <Loader2 className="h-3.5 w-3.5 animate-spin" />
            Cancel
          </button>
        )}

        {stage === "error" && (
          <button
            onClick={reset}
            className="rounded-lg px-4 py-2 text-[13px] font-medium text-white transition-opacity hover:opacity-90"
            style={{ background: "#6E56CF" }}
          >
            Try again
          </button>
        )}

        {stage === "success" && (
          <button
            className="inline-flex items-center gap-1.5 rounded-lg px-4 py-2 text-[13px] font-medium text-white transition-opacity hover:opacity-90"
            style={{ background: "#6E56CF" }}
          >
            View graph
            <ArrowRight className="h-3.5 w-3.5" />
          </button>
        )}
      </div>
    </div>
  );
}
