import React, { useEffect, useMemo, useRef, useState } from "react";
import { createRoot } from "react-dom/client";
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

console.log("API Base URL:", process.env.REACT_APP_API_BASE_URL);

/**
 * To-Do Frontend
 * Stack: React + TailwindCSS + React Query + Axios + lucide-react
 *
 * API (provided by backend):
 *  - POST   /v1/tasks/
 *  - GET    /v1/tasks/                       (supports: status, tags, search, page, pageSize)
 *  - GET    /v1/tasks/{id}/
 *  - PATCH  /v1/tasks/{id}/
 *  - DELETE /v1/tasks/{id}/
 *
 * Env:
 *  - REACT_APP_API_BASE_URL (e.g., http://localhost:8000)
 */

/****************************** utils ********************************/ 
const API_BASE = process.env.REACT_APP_API_BASE_URL || "";
async function api(path, { method = "GET", params, body } = {}) {
  let url = `${API_BASE}${path}`;
  if (params && Object.keys(params).length) {
    const usp = new URLSearchParams(params);
    url += `?${usp.toString()}`;
  }
  const res = await fetch(url, {
    method,
    headers: { "Content-Type": "application/json" },
    body: body ? JSON.stringify(body) : undefined,
  });
  if (!res.ok) {
    let data;
    try { data = await res.json(); } catch { data = { message: await res.text() }; }
    const err = new Error(data?.message || res.statusText);
    err.response = { data, status: res.status };
    throw err;
  }
  if (res.status === 204) return null;
  try { return await res.json(); } catch { return {}; }
}

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
  const data = await api("/v1/tasks/", { params });   // ✅ fixed trailing slash
  return parseListResponse({ data });
}

async function createTask(payload) {
  return await api("/v1/tasks/", { method: "POST", body: payload });  // ✅
}

async function getTask(id) {
  return await api(`/v1/tasks/${id}/`);  // ✅
}

async function updateTask(id, payload) {
  return await api(`/v1/tasks/${id}/`, { method: "PATCH", body: payload });  // ✅
}

async function deleteTask(id) {
  return await api(`/v1/tasks/${id}/`, { method: "DELETE" });  // ✅
}

/****************************** UI primitives *************************/
// … (UNCHANGED CODE: Button, Input, Select, Textarea, Badge, Spinner, Alert, Modal)

/****************************** Feature: Filters *************************/
// … (UNCHANGED CODE)

/****************************** Feature: Task Form *************************/
// … (UNCHANGED CODE)

/****************************** Feature: Task List *************************/
// … (UNCHANGED CODE)

/****************************** Main Screen *************************/
// … (UNCHANGED CODE)

/****************************** App Shell *************************/
// … (UNCHANGED CODE)

/****************************** Boot *********************************/
const queryClient = new QueryClient();

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <AppShell />
    </QueryClientProvider>
  );
}
