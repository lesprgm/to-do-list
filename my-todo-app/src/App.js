import React, { useEffect, useMemo, useRef, useState } from "react";
import { createRoot } from "react-dom/client";
import axios from "axios";
import {
  Plus,
  Filter,
  Edit,
  Trash2,
  Loader2,
  AlertCircle,
  CheckCircle2,
  X,
  Search,
  ChevronLeft,
  ChevronRight,
  Tags,
} from "lucide-react";
import { QueryClient, QueryClientProvider, useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

/**
 * To-Do Frontend
 * Stack: React + TailwindCSS + React Query + Axios + lucide-react
 *
 * API (provided by backend):
 *  - POST   /v1/tasks
 *  - GET    /v1/tasks                       (supports: status, tags, search, page, pageSize)
 *  - GET    /v1/tasks/{id}
 *  - PATCH  /v1/tasks/{id}
 *  - DELETE /v1/tasks/{id}
 *
 * Env:
 *  - REACT_APP_API_BASE_URL (e.g., http://localhost:4000)
 */

/****************************** utils ********************************/ 
const API = axios.create({
  baseURL: process.env.REACT_APP_API_BASE_URL || "",
  headers: { "Content-Type": "application/json" },
});

function clsx(...classes) {
  return classes.filter(Boolean).join(" ");
}

function useDebouncedValue(value, delay = 400) {
  const [v, setV] = useState(value);
  useEffect(() => {
    const t = setTimeout(() => setV(value), delay);
    return () => clearTimeout(t);
  }, [value, delay]);
  return v;
}

function formatError(err) {
  if (!err) return "";
  const m = err?.response?.data?.message || err?.message || "Something went wrong";
  return typeof m === "string" ? m : JSON.stringify(m);
}

function parseListResponse(resp) {
  // Accepts multiple common shapes to reduce coupling with backend shape.
  // Expected shapes:
  // 1) { items: Task[], total, page, pageSize }
  // 2) { data: Task[], meta: { total, page, pageSize } }
  // 3) { results, totalCount }
  const d = resp?.data || {};
  if (Array.isArray(d.items)) {
    return { items: d.items, total: d.total ?? d.items.length, page: d.page ?? 1, pageSize: d.pageSize ?? d.items.length };
  }
  if (Array.isArray(d.data)) {
    const meta = d.meta || {};
    return { items: d.data, total: meta.total ?? d.data.length, page: meta.page ?? 1, pageSize: meta.pageSize ?? d.data.length };
  }
  if (Array.isArray(d.results)) {
    return { items: d.results, total: d.totalCount ?? d.results.length, page: d.page ?? 1, pageSize: d.pageSize ?? d.results.length };
  }
  if (Array.isArray(d)) {
    return { items: d, total: d.length, page: 1, pageSize: d.length };
  }
  return { items: [], total: 0, page: 1, pageSize: 10 };
}

/****************************** API hooks *****************************/
async function listTasks({ page, pageSize, status, search, tags }) {
  const params = {};
  if (page) params.page = page;
  if (pageSize) params.pageSize = pageSize;
  if (status && status !== "all") params.status = status;
  if (search) params.search = search;
  if (tags && tags.length) params.tags = tags.join(",");
  const resp = await API.get("/v1/tasks", { params });
  return parseListResponse(resp);
}

async function createTask(payload) {
  const resp = await API.post("/v1/tasks", payload);
  return resp.data;
}

async function getTask(id) {
  const resp = await API.get(`/v1/tasks/${id}`);
  return resp.data;
}

async function updateTask(id, payload) {
  const resp = await API.patch(`/v1/tasks/${id}`, payload);
  return resp.data;
}

async function deleteTask(id) {
  const resp = await API.delete(`/v1/tasks/${id}`);
  return resp.data;
}

/****************************** UI primitives *************************/
function Button({ as: As = "button", className = "", variant = "primary", size = "md", disabled, ...props }) {
  const base = "inline-flex items-center justify-center gap-2 rounded-2xl font-medium transition focus:outline-none focus-visible:ring-2 focus-visible:ring-offset-2 focus-visible:ring-black/20 disabled:opacity-60 disabled:cursor-not-allowed";
  const variants = {
    primary: "bg-black text-white hover:bg-black/90",
    secondary: "bg-white text-gray-900 border border-gray-200 hover:bg-gray-50",
    danger: "bg-red-600 text-white hover:bg-red-500",
    ghost: "bg-transparent text-gray-700 hover:bg-gray-100",
  };
  const sizes = { sm: "px-3 py-1.5 text-sm", md: "px-4 py-2", lg: "px-5 py-2.5 text-base" };
  return (
    <As className={clsx(base, variants[variant], sizes[size], className)} disabled={disabled} {...props} />
  );
}

function Input({ className = "", ...props }) {
  return (
    <input
      className={clsx(
        "w-full rounded-2xl border border-gray-300 bg-white px-3 py-2 text-gray-900 placeholder:text-gray-400 shadow-sm focus:border-gray-900 focus:ring-2 focus:ring-black/20",
        className
      )}
      {...props}
    />
  );
}

function Select({ className = "", children, ...props }) {
  return (
    <select
      className={clsx(
        "w-full rounded-2xl border border-gray-300 bg-white px-3 py-2 text-gray-900 shadow-sm focus:border-gray-900 focus:ring-2 focus:ring-black/20",
        className
      )}
      {...props}
    >
      {children}
    </select>
  );
}

function Textarea({ className = "", ...props }) {
  return (
    <textarea
      className={clsx(
        "w-full rounded-2xl border border-gray-300 bg-white px-3 py-2 text-gray-900 placeholder:text-gray-400 shadow-sm focus:border-gray-900 focus:ring-2 focus:ring-black/20",
        className
      )}
      {...props}
    />
  );
}

function Badge({ children, className = "" }) {
  return (
    <span className={clsx("inline-flex items-center rounded-full border border-gray-300 px-2.5 py-0.5 text-xs font-medium", className)}>
      {children}
    </span>
  );
}

function Spinner({ label = "Loading" }) {
  return (
    <div className="flex items-center gap-2 text-gray-700" role="status" aria-live="polite" aria-busy="true">
      <Loader2 className="h-4 w-4 animate-spin" aria-hidden />
      <span className="sr-only">{label}</span>
    </div>
  );
}

function Alert({ type = "error", title = "", description = "", onClose }) {
  const isError = type === "error";
  const Icon = isError ? AlertCircle : CheckCircle2;
  const color = isError ? "bg-red-50 border-red-200 text-red-800" : "bg-emerald-50 border-emerald-200 text-emerald-800";
  return (
    <div className={clsx("flex items-start gap-3 rounded-2xl border p-3", color)} role={isError ? "alert" : "status"}>
      <Icon className="mt-0.5 h-5 w-5 shrink-0" aria-hidden />
      <div className="flex-1">
        {title && <div className="font-semibold">{title}</div>}
        {description && <div className="text-sm opacity-90">{description}</div>}
      </div>
      {onClose && (
        <button onClick={onClose} className="rounded-full p-1 hover:bg-black/5" aria-label="Close alert">
          <X className="h-4 w-4" aria-hidden />
        </button>
      )}
    </div>
  );
}

function Modal({ open, onClose, title, children }) {
  const dialogRef = useRef(null);
  useEffect(() => {
    function onKey(e) {
      if (e.key === "Escape") onClose?.();
    }
    document.addEventListener("keydown", onKey);
    return () => document.removeEventListener("keydown", onKey);
  }, [onClose]);
  useEffect(() => {
    if (open) {
      // focus first input
      const el = dialogRef.current?.querySelector("input, textarea, select, button");
      el?.focus();
    }
  }, [open]);
  if (!open) return null;
  return (
    <div className="fixed inset-0 z-50" role="dialog" aria-modal="true" aria-labelledby="modal-title">
      <div className="absolute inset-0 bg-black/40" onClick={onClose} />
      <div className="absolute inset-0 flex items-center justify-center p-4">
        <div ref={dialogRef} className="w-full max-w-xl rounded-3xl bg-white p-6 shadow-xl" role="document">
          <div className="mb-4 flex items-start justify-between gap-4">
            <h2 id="modal-title" className="text-lg font-semibold">{title}</h2>
            <button onClick={onClose} className="rounded-full p-2 hover:bg-gray-100" aria-label="Close">
              <X className="h-5 w-5" aria-hidden />
            </button>
          </div>
          {children}
        </div>
      </div>
    </div>
  );
}

/****************************** Feature: Filters *************************/
function FilterBar({ filters, setFilters, total, isFetching }) {
  const [q, setQ] = useState(filters.search || "");
  const debounced = useDebouncedValue(q, 400);
  useEffect(() => {
    setFilters((f) => ({ ...f, search: debounced, page: 1 }));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [debounced]);

  const [tagsInput, setTagsInput] = useState("");

  function addTag(tag) {
    const t = tag.trim();
    if (!t) return;
    setFilters((f) => ({ ...f, tags: Array.from(new Set([...(f.tags || []), t])), page: 1 }));
    setTagsInput("");
  }

  function removeTag(tag) {
    setFilters((f) => ({ ...f, tags: (f.tags || []).filter((x) => x !== tag), page: 1 }));
  }

  return (
    <div className="flex flex-col gap-3 rounded-3xl border border-gray-200 bg-white p-4 shadow-sm">
      <div className="flex flex-wrap items-center gap-2">
        <div className="flex items-center gap-2 rounded-2xl border border-gray-300 bg-white px-3 py-2 shadow-sm focus-within:ring-2 focus-within:ring-black/20">
          <Search className="h-4 w-4 text-gray-500" aria-hidden />
          <input
            id="task-search"
            type="search"
            placeholder="Search tasks…"
            value={q}
            onChange={(e) => setQ(e.target.value)}
            className="w-56 bg-transparent text-sm focus:outline-none"
            aria-label="Search tasks"
          />
        </div>
        <div className="flex items-center gap-2">
          <label htmlFor="status" className="sr-only">Status</label>
          <Select
            id="status"
            value={filters.status || "all"}
            onChange={(e) => setFilters((f) => ({ ...f, status: e.target.value, page: 1 }))}
            className="w-40"
            aria-label="Filter by status"
          >
            <option value="all">All statuses</option>
            <option value="todo">To do</option>
            <option value="in_progress">In progress</option>
            <option value="done">Done</option>
          </Select>
        </div>
        <div className="flex flex-wrap items-center gap-2">
          <div className="flex items-center gap-2 rounded-2xl border border-gray-300 bg-white px-3 py-2 shadow-sm">
            <Tags className="h-4 w-4 text-gray-500" aria-hidden />
            <input
              type="text"
              placeholder="Add tag & press Enter"
              value={tagsInput}
              onChange={(e) => setTagsInput(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter") {
                  e.preventDefault();
                  addTag(tagsInput);
                }
              }}
              className="w-48 bg-transparent text-sm focus:outline-none"
              aria-label="Add tag"
            />
          </div>
          <div className="flex flex-wrap gap-1">
            {(filters.tags || []).map((t) => (
              <Badge key={t} className="gap-1">
                <span>#{t}</span>
                <button className="-mr-1 rounded-full p-1 hover:bg-gray-200" aria-label={`Remove tag ${t}`} onClick={() => removeTag(t)}>
                  <X className="h-3 w-3" aria-hidden />
                </button>
              </Badge>
            ))}
          </div>
        </div>
        <div className="ms-auto flex items-center gap-2">
          <label htmlFor="pageSize" className="sr-only">Items per page</label>
          <Select
            id="pageSize"
            value={filters.pageSize}
            onChange={(e) => setFilters((f) => ({ ...f, pageSize: Number(e.target.value), page: 1 }))}
            className="w-36"
            aria-label="Items per page"
          >
            {[5, 10, 20, 50].map((n) => (
              <option key={n} value={n}>{n} / page</option>
            ))}
          </Select>
          <div className="hidden sm:flex items-center gap-2 text-sm text-gray-600" aria-live="polite">
            <Filter className="h-4 w-4" aria-hidden />
            {isFetching ? "Updating…" : `${total} total`}
          </div>
        </div>
      </div>
    </div>
  );
}

/****************************** Feature: Task Form *************************/
function TaskFormModal({ open, onClose, initialTask }) {
  const isEdit = Boolean(initialTask?.id);
  const [title, setTitle] = useState(initialTask?.title || "");
  const [description, setDescription] = useState(initialTask?.description || "");
  const [status, setStatus] = useState(initialTask?.status || "todo");
  const [tags, setTags] = useState(initialTask?.tags || []);
  const [tagInput, setTagInput] = useState("");
  const [err, setErr] = useState("");
  const queryClient = useQueryClient();

  useEffect(() => {
    if (open) {
      setTitle(initialTask?.title || "");
      setDescription(initialTask?.description || "");
      setStatus(initialTask?.status || "todo");
      setTags(initialTask?.tags || []);
      setTagInput("");
      setErr("");
    }
  }, [open, initialTask]);

  const createMut = useMutation({
    mutationFn: createTask,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["tasks"] });
      onClose?.();
    },
    onError: (e) => setErr(formatError(e)),
  });

  const updateMut = useMutation({
    mutationFn: (payload) => updateTask(initialTask.id, payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["tasks"] });
      onClose?.();
    },
    onError: (e) => setErr(formatError(e)),
  });

  function addTagLocal(t) {
    const tag = t.trim();
    if (!tag) return;
    setTags((prev) => Array.from(new Set([...prev, tag])));
    setTagInput("");
  }

  function removeTagLocal(t) {
    setTags((prev) => prev.filter((x) => x !== t));
  }

  const canSubmit = title.trim().length > 0 && !(createMut.isPending || updateMut.isPending);

  return (
    <Modal open={open} onClose={onClose} title={isEdit ? "Edit Task" : "New Task"}>
      {err && (
        <div className="mb-3">
          <Alert type="error" title="Could not save task" description={err} onClose={() => setErr("")} />
        </div>
      )}
      <form
        className="flex flex-col gap-3"
        onSubmit={(e) => {
          e.preventDefault();
          const payload = { title: title.trim(), description, status, tags };
          isEdit ? updateMut.mutate(payload) : createMut.mutate(payload);
        }}
      >
        <div>
          <label htmlFor="title" className="mb-1 block text-sm font-medium">Title<span className="text-red-600">*</span></label>
          <Input id="title" required value={title} onChange={(e) => setTitle(e.target.value)} placeholder="e.g., Ship MVP" />
        </div>
        <div>
          <label htmlFor="description" className="mb-1 block text-sm font-medium">Description</label>
          <Textarea id="description" rows={3} value={description} onChange={(e) => setDescription(e.target.value)} placeholder="Optional details…" />
        </div>
        <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
          <div>
            <label htmlFor="statusSelect" className="mb-1 block text-sm font-medium">Status</label>
            <Select id="statusSelect" value={status} onChange={(e) => setStatus(e.target.value)}>
              <option value="todo">To do</option>
              <option value="in_progress">In progress</option>
              <option value="done">Done</option>
            </Select>
          </div>
          <div>
            <label className="mb-1 block text-sm font-medium">Tags</label>
            <div className="flex items-center gap-2 rounded-2xl border border-gray-300 bg-white px-3 py-2 shadow-sm">
              <Tags className="h-4 w-4 text-gray-500" aria-hidden />
              <input
                type="text"
                placeholder="Add tag & press Enter"
                value={tagInput}
                onChange={(e) => setTagInput(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === "Enter") {
                    e.preventDefault();
                    addTagLocal(tagInput);
                  }
                }}
                className="w-full bg-transparent text-sm focus:outline-none"
                aria-label="Add tag"
              />
            </div>
            <div className="mt-2 flex flex-wrap gap-1">
              {tags.map((t) => (
                <Badge key={t} className="gap-1">
                  <span>#{t}</span>
                  <button className="-mr-1 rounded-full p-1 hover:bg-gray-200" aria-label={`Remove tag ${t}`} onClick={() => removeTagLocal(t)}>
                    <X className="h-3 w-3" aria-hidden />
                  </button>
                </Badge>
              ))}
            </div>
          </div>
        </div>
        <div className="flex items-center justify-end gap-2 pt-2">
          <Button type="button" variant="ghost" onClick={onClose}>Cancel</Button>
          <Button type="submit" disabled={!canSubmit}>
            {(createMut.isPending || updateMut.isPending) && <Loader2 className="h-4 w-4 animate-spin" aria-hidden />}
            {isEdit ? "Save changes" : "Create task"}
          </Button>
        </div>
      </form>
    </Modal>
  );
}

/****************************** Feature: Task List *************************/
function TaskRow({ task, onEdit, onDelete }) {
  const statusColor = {
    todo: "bg-gray-100 text-gray-800 border-gray-200",
    in_progress: "bg-blue-50 text-blue-800 border-blue-200",
    done: "bg-emerald-50 text-emerald-800 border-emerald-200",
  }[task.status] || "bg-gray-100 text-gray-800 border-gray-200";

  return (
    <div className="grid grid-cols-1 items-center gap-3 rounded-2xl border border-gray-200 bg-white p-4 shadow-sm md:grid-cols-12">
      <div className="md:col-span-5">
        <div className="text-base font-medium text-gray-900">{task.title}</div>
        {task.description && <div className="mt-1 text-sm text-gray-600 line-clamp-2">{task.description}</div>}
        <div className="mt-2 flex flex-wrap gap-1">
          {(task.tags || []).map((t) => (
            <Badge key={t}>#{t}</Badge>
          ))}
        </div>
      </div>
      <div className="md:col-span-2">
        <span className={clsx("inline-flex rounded-full border px-2.5 py-1 text-xs font-medium", statusColor)}>{task.status}</span>
      </div>
      <div className="flex gap-2 md:col-span-3 md:justify-center">
        <Button variant="secondary" size="sm" onClick={() => onEdit(task)} aria-label={`Edit ${task.title}`}>
          <Edit className="h-4 w-4" aria-hidden />
          <span className="sr-only">Edit</span>
        </Button>
        <Button variant="danger" size="sm" onClick={() => onDelete(task)} aria-label={`Delete ${task.title}`}>
          <Trash2 className="h-4 w-4" aria-hidden />
          <span className="sr-only">Delete</span>
        </Button>
      </div>
      <div className="text-xs text-gray-500 md:col-span-2 md:text-right">
        {task.updatedAt ? new Date(task.updatedAt).toLocaleString() : task.createdAt ? new Date(task.createdAt).toLocaleString() : null}
      </div>
    </div>
  );
}

function Pagination({ page, pageSize, total, onPageChange }) {
  const totalPages = Math.max(1, Math.ceil(total / pageSize));
  const canPrev = page > 1;
  const canNext = page < totalPages;
  const pages = useMemo(() => {
    const arr = [];
    const max = totalPages;
    const start = Math.max(1, page - 1);
    const end = Math.min(max, page + 1);
    for (let i = start; i <= end; i++) arr.push(i);
    if (!arr.includes(1)) arr.unshift(1);
    if (!arr.includes(max)) arr.push(max);
    return Array.from(new Set(arr));
  }, [page, totalPages]);

  return (
    <nav className="flex items-center justify-between gap-2" aria-label="Pagination">
      <div className="text-sm text-gray-600">Page {page} of {totalPages}</div>
      <div className="flex items-center gap-1">
        <Button variant="secondary" size="sm" disabled={!canPrev} onClick={() => onPageChange(page - 1)} aria-label="Previous page">
          <ChevronLeft className="h-4 w-4" aria-hidden />
        </Button>
        {pages.map((p, i) => (
          <Button
            key={`${p}-${i}`}
            size="sm"
            variant={p === page ? "primary" : "secondary"}
            aria-current={p === page ? "page" : undefined}
            onClick={() => onPageChange(p)}
          >
            {p}
          </Button>
        ))}
        <Button variant="secondary" size="sm" disabled={!canNext} onClick={() => onPageChange(page + 1)} aria-label="Next page">
          <ChevronRight className="h-4 w-4" aria-hidden />
        </Button>
      </div>
    </nav>
  );
}

/****************************** Main Screen *************************/
function TasksScreen() {
  const queryClient = useQueryClient();
  const [filters, setFilters] = useState({ status: "all", tags: [], search: "", page: 1, pageSize: 10 });
  const [selected, setSelected] = useState(null);
  const [showForm, setShowForm] = useState(false);
  const [alert, setAlert] = useState(null); // { type, title, description }

  const { data, isLoading, isFetching, error } = useQuery({
    queryKey: ["tasks", filters],
    queryFn: () => listTasks(filters),
    keepPreviousData: true,
  });

  const delMut = useMutation({
    mutationFn: (id) => deleteTask(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["tasks"] });
      setAlert({ type: "success", title: "Task deleted", description: "The task has been removed." });
    },
    onError: (e) => setAlert({ type: "error", title: "Delete failed", description: formatError(e) }),
  });

  const tasks = data?.items || [];
  const total = data?.total || 0;

  return (
    <section aria-labelledby="tasks-title" className="">
      <div className="mb-4 flex items-center justify-between">
        <h1 id="tasks-title" className="text-xl font-semibold">Tasks</h1>
        <Button onClick={() => { setSelected(null); setShowForm(true); }}>
          <Plus className="h-4 w-4" aria-hidden />
          New Task
        </Button>
      </div>

      {alert && (
        <div className="mb-3">
          <Alert type={alert.type} title={alert.title} description={alert.description} onClose={() => setAlert(null)} />
        </div>
      )}

      <FilterBar filters={filters} setFilters={setFilters} total={total} isFetching={isFetching} />

      <div className="mt-4" aria-live="polite">
        {isLoading ? (
          <div className="flex items-center gap-2 text-gray-700"><Spinner label="Loading tasks" /><span>Loading tasks…</span></div>
        ) : error ? (
          <Alert type="error" title="Could not load tasks" description={formatError(error)} />
        ) : tasks.length === 0 ? (
          <div className="rounded-3xl border border-dashed border-gray-300 p-8 text-center text-gray-600">
            <p className="text-sm">No tasks found. Try adjusting filters or create a new task.</p>
            <div className="mt-3">
              <Button onClick={() => { setSelected(null); setShowForm(true); }}>Create your first task</Button>
            </div>
          </div>
        ) : (
          <div className="flex flex-col gap-3">
            {tasks.map((t) => (
              <TaskRow
                key={t.id}
                task={t}
                onEdit={(task) => { setSelected(task); setShowForm(true); }}
                onDelete={(task) => {
                  if (confirm(`Delete task: "${task.title}"?`)) {
                    delMut.mutate(task.id);
                  }
                }}
              />
            ))}
          </div>
        )}
      </div>

      <div className="mt-4">
        <Pagination
          page={filters.page}
          pageSize={filters.pageSize}
          total={total}
          onPageChange={(p) => setFilters((f) => ({ ...f, page: p }))}
        />
      </div>

      <TaskFormModal open={showForm} onClose={() => setShowForm(false)} initialTask={selected} />
    </section>
  );
}

/****************************** App Shell *************************/
function AppShell() {
  return (
    <div className="min-h-screen bg-gray-50">
      <a href="#main" className="sr-only focus:not-sr-only focus:absolute focus:m-4 focus:rounded-md focus:bg-white focus:px-3 focus:py-2 focus:shadow">Skip to main content</a>
      <header className="sticky top-0 z-40 border-b border-gray-200 bg-white/80 backdrop-blur">
        <div className="mx-auto max-w-6xl px-4 py-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <div className="h-8 w-8 rounded-2xl bg-black" aria-hidden />
              <span className="text-lg font-semibold">To‑Do</span>
            </div>
            <span className="text-sm text-gray-500">Frontend Demo</span>
          </div>
        </div>
      </header>
      <main id="main" className="mx-auto max-w-6xl px-4 py-6">
        <div className="grid grid-cols-1 gap-6">
          <TasksScreen />
        </div>
      </main>
      <footer className="border-t border-gray-200 bg-white/60">
        <div className="mx-auto max-w-6xl px-4 py-6 text-sm text-gray-500">Built with React, Tailwind, and React Query. Keyboard-friendly, ARIA-labeled, responsive.</div>
      </footer>
    </div>
  );
}

/****************************** Boot *********************************/
const queryClient = new QueryClient();

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <AppShell />
    </QueryClientProvider>
  );
}

// If you're using Create React App, src/index.js should look like:
// import React from 'react';
// import { createRoot } from 'react-dom/client';
// import App from './App';
// const container = document.getElementById('root');
// const root = createRoot(container);
// root.render(<App />);
