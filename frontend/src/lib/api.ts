import axios from "axios";

export const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000",
  headers: { "Content-Type": "application/json" },
});

api.interceptors.request.use((config) => {
  const token = typeof window !== "undefined" ? localStorage.getItem("access_token") : null;
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

api.interceptors.response.use(
  (res) => res,
  async (err) => {
    if (err.response?.status === 401) {
      localStorage.removeItem("access_token");
      window.location.href = "/login";
    }
    return Promise.reject(err);
  }
);

// Auth
export const authApi = {
  login: (username: string, password: string) =>
    api.post("/v1/auth/login", { username, password }),
  me: () => api.get("/v1/auth/me"),
};

// Orders
export const orderApi = {
  list: (params?: Record<string, unknown>) => api.get("/v1/orders", { params }),
  get: (id: string) => api.get(`/v1/orders/${id}`),
  create: (data: unknown) => api.post("/v1/orders", data),
  traceability: (id: string) => api.get(`/v1/orders/${id}/traceability`),
  listCustomers: () => api.get("/v1/orders/customers"),
  quotes: (id: string) => api.get(`/v1/orders/${id}/quotes`),
  bom: (id: string) => api.get(`/v1/orders/${id}/bom`),
  generateBom: (id: string) => api.post(`/v1/orders/${id}/bom/generate`),
};

// Quotes
export const quoteApi = {
  approve: (id: string) => api.put(`/v1/quotes/${id}/approve`),
  reject: (id: string) => api.put(`/v1/quotes/${id}/reject`),
};

// CAD
export const cadApi = {
  upload: (formData: FormData) =>
    api.post("/v1/cad-drawings", formData, { headers: { "Content-Type": "multipart/form-data" } }),
  get: (id: string) => api.get(`/v1/cad-drawings/${id}`),
  parseStatus: (id: string) => api.get(`/v1/cad-drawings/${id}/parse-status`),
};

// Production
export const productionApi = {
  getLot: (id: string) => api.get(`/v1/production-lots/${id}`),
  updateQty: (id: string, data: unknown) => api.put(`/v1/production-lots/${id}/actual-qty`, data),
  listForming: (lotId: string) => api.get(`/v1/production-lots/${lotId}/forming`),
  createForming: (lotId: string, data: unknown) => api.post(`/v1/production-lots/${lotId}/forming`, data),
  createWelding: (lotId: string, data: unknown) => api.post(`/v1/production-lots/${lotId}/welding`, data),
  createPacking: (lotId: string, data: unknown) => api.post(`/v1/production-lots/${lotId}/packing`, data),
};

// WorkOrder
export const workOrderApi = {
  list: (params?: Record<string, unknown>) => api.get("/v1/work-orders", { params }),
  get: (id: string) => api.get(`/v1/work-orders/${id}`),
  create: (data: unknown) => api.post("/v1/work-orders", data),
  updateStatus: (id: string, status: string) => api.put(`/v1/work-orders/${id}/status`, { status }),
};

// Equipment
export const equipmentApi = {
  list: () => api.get("/v1/equipment"),
  get: (id: string) => api.get(`/v1/equipment/${id}`),
  updateStatus: (id: string, status: string) =>
    api.put(`/v1/equipment/${id}/status`, { status }),
  sensorData: (id: string, params: Record<string, unknown>) =>
    api.get(`/v1/equipment/${id}/sensor-data`, { params }),
};

// Quality
export const qualityApi = {
  createInspection: (data: unknown) => api.post("/v1/quality-inspections", data),
  getInspection: (id: string) => api.get(`/v1/quality-inspections/${id}`),
  listDefects: (id: string) => api.get(`/v1/quality-inspections/${id}/defects`),
  createDefect: (id: string, data: unknown) => api.post(`/v1/quality-inspections/${id}/defects`, data),
};

// Shipping
export const shippingApi = {
  list: (params?: Record<string, unknown>) => api.get("/v1/shipping-orders", { params }),
  get: (id: string) => api.get(`/v1/shipping-orders/${id}`),
  create: (data: unknown) => api.post("/v1/shipping-orders", data),
  ship: (id: string) => api.put(`/v1/shipping-orders/${id}/ship`),
  listLots: (id: string) => api.get(`/v1/shipping-orders/${id}/lots`),
  addLot: (id: string, data: unknown) => api.post(`/v1/shipping-orders/${id}/lots`, data),
  deliveryRisk: () => api.get("/v1/shipping-orders/delivery-risk"),
  listClaims: (params?: Record<string, unknown>) => api.get("/v1/shipping-orders/claims", { params }),
  createClaim: (data: unknown) => api.post("/v1/shipping-orders/claims", data),
};

// Receiving / Inventory
export const receivingApi = {
  list:         (params?: Record<string, unknown>) => api.get("/v1/receiving-lots", { params }),
  get:          (id: string) => api.get(`/v1/receiving-lots/${id}`),
  create:       (data: unknown) => api.post("/v1/receiving-lots", data),
  history:      (lotId: string) => api.get(`/v1/receiving-lots/${lotId}/history`),
  supplierQuality: (params?: Record<string, unknown>) =>
    api.get("/v1/receiving-lots/supplier-quality", { params }),
  traceability: (id: string) => api.get(`/v1/receiving-lots/${id}/traceability`),
};

// Supplier
export const supplierApi = {
  list: () => api.get("/v1/suppliers"),
  quality: (id: string) => api.get(`/v1/suppliers/${id}/quality`),
};

// KPI
export const kpiApi = {
  summary: () => api.get("/v1/ai/kpi/summary"),
  records: (type?: string) => api.get("/v1/ai/kpi/records", { params: type ? { kpi_type: type } : {} }),
};

// AI
export const aiApi = {
  query: (text: string, agentType = "INTEGRATED") =>
    api.post("/v1/ai/query", { query: text, agent_type: agentType }),
  kpiSummary: () => api.get("/v1/ai/kpi/summary"),
};

// WebSocket helpers
export const wsUrl = (path: string) =>
  (process.env.NEXT_PUBLIC_WS_URL ?? "ws://localhost:8000") + path;
