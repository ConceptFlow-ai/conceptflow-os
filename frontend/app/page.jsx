"use client";

import {
  ArrowUpRight,
  CheckCircle2,
  ChevronDown,
  Command,
  FileText,
  Loader2,
  Mic,
  Paperclip,
  Plus,
  X,
} from "lucide-react";
import { useRef, useState } from "react";

const history = {
  Today: ["Glassmorphism UI Engine", "Procedural Mandelbrot Visualizer", "Cybernetic Landing Frame"],
  Yesterday: ["Dynamic UI Blueprint", "Abstract Glass Vector Pack", "Orthogonal 3D Maze Setup"],
};

function ConceptMark() {
  return (
    <div className="concept-mark" aria-hidden="true">
      <span className="concept-mark-line concept-mark-line-a" />
      <span className="concept-mark-line concept-mark-line-b" />
      <i className="concept-node concept-node-a" />
      <i className="concept-node concept-node-b" />
      <i className="concept-node concept-node-c" />
    </div>
  );
}

function formatSize(bytes) {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(0)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

export default function DocumentUpload() {
  const [active, setActive] = useState(history.Today[0]);
  const [text, setText] = useState("");
  const [messages, setMessages] = useState([]);
  const [model, setModel] = useState("ConceptFlow");
  const [listening, setListening] = useState(false);
  const [file, setFile] = useState(null);
  const [uploadState, setUploadState] = useState("idle");
  const [uploadProgress, setUploadProgress] = useState(0);
  const [uploadError, setUploadError] = useState("");
  const inputRef = useRef(null);
  const xhrRef = useRef(null);

  const selectFile = (selectedFile) => {
    if (!selectedFile) return;
    if (selectedFile.type !== "application/pdf") {
      setUploadError("Only PDF files are supported right now.");
      setUploadState("error");
      return;
    }
    setFile(selectedFile);
    setUploadState("selected");
    setUploadProgress(0);
    setUploadError("");
  };

  const removeFile = () => {
    xhrRef.current?.abort();
    setFile(null);
    setUploadState("idle");
    setUploadProgress(0);
    setUploadError("");
    if (inputRef.current) inputRef.current.value = "";
  };

  const uploadFile = () => {
    if (!file) return;
    const form = new FormData();
    form.append("file", file);
    const xhr = new XMLHttpRequest();
    xhrRef.current = xhr;
    setUploadState("uploading");
    setUploadProgress(0);
    xhr.open("POST", "http://127.0.0.1:8000/api/documents/upload");
    xhr.upload.onprogress = (event) => {
      if (event.lengthComputable) {
        setUploadProgress(Math.round((event.loaded / event.total) * 100));
      }
    };
    xhr.onload = () => {
      if (xhr.status >= 200 && xhr.status < 300) {
        setUploadProgress(100);
        setUploadState("success");
      } else {
        setUploadError(`Upload failed (${xhr.status}). Try again.`);
        setUploadState("error");
      }
    };
    xhr.onerror = () => {
      setUploadError("Could not reach the upload server. Start the backend and try again.");
      setUploadState("error");
    };
    xhr.send(form);
  };

  const submitPrompt = (event) => {
    event.preventDefault();
    const clean = text.trim();
    if (!clean && !file) return;
    if (file && uploadState === "selected") {
      uploadFile();
      return;
    }
    if (clean) {
      setMessages((current) => [
        ...current,
        { role: "user", text: clean },
        { role: "assistant", text: `Let's map out “${clean}” as a clear, interactive concept flow.` },
      ]);
      setText("");
    }
  };

  const startNewChat = () => {
    setMessages([]);
    setActive("");
    setText("");
    removeFile();
  };

  return (
    <main className="flex min-h-screen overflow-hidden bg-background text-foreground md:h-screen">
      <aside className="hidden w-[300px] shrink-0 border-r border-border bg-sidebar px-8 py-8 md:block">
        <div className="flex items-center gap-3 text-[20px] font-semibold">
          <ConceptMark />
          <span>ConceptFlow</span>
        </div>
        <button onClick={startNewChat} className="mt-9 flex h-10 w-full items-center justify-between rounded-md border border-border bg-secondary px-3 text-[15px] hover:bg-accent">
          <span className="flex items-center gap-2.5"><Plus className="size-4" /> New chat</span>
          <span className="flex items-center gap-1 rounded border border-border px-1.5 py-0.5 text-[11px] text-muted-foreground"><Command className="size-3" /> N</span>
        </button>
        <nav className="mt-7" aria-label="Chat history">
          {Object.entries(history).map(([period, chats], groupIndex) => (
            <section key={period} className={groupIndex ? "mt-6" : ""}>
              <h2 className="mb-1.5 text-[12px] font-medium uppercase text-sidebar-muted">{period}</h2>
              <div className="space-y-1">
                {chats.map((chat) => (
                  <button key={chat} onClick={() => setActive(chat)} className={`h-9 w-full truncate rounded-md px-3 text-left text-[14px] ${active === chat ? "bg-sidebar-accent text-sidebar-foreground" : "text-sidebar-muted hover:bg-sidebar-accent hover:text-sidebar-foreground"}`}>
                    {chat}
                  </button>
                ))}
              </div>
            </section>
          ))}
        </nav>
      </aside>

      <section className="relative min-w-0 flex-1 overflow-y-auto">
        {messages.length === 0 ? (
          <div className="flex min-h-screen items-center justify-center px-5 pb-8 pt-6 md:min-h-full md:translate-y-[8vh]">
            <div className="w-full max-w-[750px]">
              <h1 className="mx-auto max-w-[690px] text-balance text-center text-[34px] font-bold leading-[1.18] sm:text-[42px]">What would you like to understand today?</h1>
              <p className="mt-3 text-center text-[16px] text-muted-foreground">ConceptFlow turns your ideas into interactive flows and visuals.</p>
              <form onSubmit={submitPrompt} className="concept-composer mt-7">
                <div className="rounded-3xl border border-border bg-card shadow-2xl">
                  {file && (
                    <div className="mx-4 mt-4 flex items-center gap-3 rounded-xl border border-border bg-secondary px-3 py-2.5 text-sm">
                      <FileText className="size-4 text-brand" />
                      <span className="min-w-0 flex-1 truncate">{file.name} <span className="text-muted-foreground">({formatSize(file.size)})</span></span>
                      {uploadState === "uploading" && <span className="text-xs text-muted-foreground">{uploadProgress}%</span>}
                      {uploadState === "success" && <CheckCircle2 className="size-4 text-emerald-400" />}
                      <button type="button" onClick={removeFile} aria-label="Remove attached PDF" className="text-muted-foreground hover:text-foreground"><X className="size-4" /></button>
                    </div>
                  )}
                  {uploadState === "error" && <p className="px-4 pt-3 text-sm text-red-300">{uploadError}</p>}
                  {uploadState === "uploading" && <div className="mx-4 mt-3 h-1 overflow-hidden rounded-full bg-secondary"><div className="h-full bg-brand transition-all" style={{ width: `${uploadProgress}%` }} /></div>}
                  <textarea value={text} onChange={(event) => setText(event.target.value)} onKeyDown={(event) => { if (event.key === "Enter" && !event.shiftKey) { event.preventDefault(); submitPrompt(event); } }} aria-label="Ask ConceptFlow anything" className="min-h-[90px] w-full resize-none bg-transparent px-4 pb-2 pt-4 text-[16px] leading-6 outline-none placeholder:text-composer-muted" placeholder="Ask anything..." />
                  <div className="flex items-center justify-between px-4 pb-3 pt-0">
                    <div className="flex items-center gap-2">
                      <input ref={inputRef} type="file" accept="application/pdf" className="hidden" onChange={(event) => selectFile(event.target.files?.[0])} />
                      <button type="button" onClick={() => inputRef.current?.click()} title="Attach a PDF" aria-label="Attach a PDF" className="text-composer-muted hover:text-foreground"><Paperclip className="size-[18px]" /></button>
                      <button type="button" onClick={() => setModel(model === "ConceptFlow" ? "ConceptFlow Pro" : "ConceptFlow")} className="flex h-8 items-center gap-2 rounded border border-border bg-secondary px-3 text-[13px] shadow-none">
                        <span className="size-1.5 rounded-full bg-brand" />{model}<ChevronDown className="size-3.5 text-muted-foreground" />
                      </button>
                    </div>
                    <div className="flex items-center gap-2">
                      <button type="button" title={listening ? "Stop listening" : "Voice input"} aria-label={listening ? "Stop listening" : "Voice input"} onClick={() => setListening((value) => !value)} className={listening ? "text-brand" : "text-composer-muted"}><Mic className="size-[18px]" /></button>
                      <button type="submit" aria-label={file && uploadState === "selected" ? "Upload PDF" : "Submit prompt"} className="flex size-9 items-center justify-center rounded-full bg-brand text-primary-foreground hover:bg-brand-hover">
                        {uploadState === "uploading" ? <Loader2 className="size-[18px] animate-spin" /> : <ArrowUpRight className="size-[18px]" />}
                      </button>
                    </div>
                  </div>
                </div>
              </form>
              <p className="mt-9 text-center text-[13px] text-disclaimer">ConceptFlow can make mistakes. Review important outputs carefully.</p>
            </div>
          </div>
        ) : (
          <div className="mx-auto flex w-full max-w-[780px] flex-col gap-7 px-6 py-12">
            {messages.map((message, index) => <div key={`${message.role}-${index}`} className={message.role === "user" ? "self-end rounded-2xl bg-brand px-4 py-3" : "rounded-2xl border border-border bg-card px-4 py-3 text-muted-foreground"}>{message.text}</div>)}
            <button onClick={startNewChat} className="self-center rounded-md border border-border bg-secondary px-4 py-2 text-sm hover:bg-accent">Start a new chat</button>
          </div>
        )}
      </section>
    </main>
  );
}
