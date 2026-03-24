const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1"

function headers(): Record<string, string> {
  const token = typeof window !== "undefined" ? localStorage.getItem("tcp_token") : ""
  return {
    "Content-Type": "application/json",
    Authorization: token ? `Bearer ${token}` : "",
  }
}

async function get<T = any>(path: string): Promise<T> {
  const res = await fetch(`${API}${path}`, { headers: headers() })
  if (!res.ok) throw new Error(`API error: ${res.status}`)
  return res.json()
}

async function post<T = any>(path: string, body?: any): Promise<T> {
  const res = await fetch(`${API}${path}`, {
    method: "POST",
    headers: headers(),
    body: body ? JSON.stringify(body) : undefined,
  })
  if (!res.ok) {
    const err = await res.json().catch(() => ({}))
    throw new Error(err.detail || `API error: ${res.status}`)
  }
  return res.json()
}

async function uploadFile<T = any>(path: string, formData: FormData): Promise<T> {
  const token = typeof window !== "undefined" ? localStorage.getItem("tcp_token") : ""
  const res = await fetch(`${API}${path}`, {
    method: "POST",
    headers: { Authorization: token ? `Bearer ${token}` : "" },
    body: formData,
  })
  if (!res.ok) throw new Error(`Upload error: ${res.status}`)
  return res.json()
}

// Auth
export const login = (email: string, password: string) =>
  post("/auth/login", { email, password })

// Dashboard
export const getDashboardStats = () => get("/dashboard/stats")
export const getDashboardCharts = (entityId: string) => get(`/dashboard/charts/${entityId}`)
export const getDashboardOverview = () => get("/dashboard/overview")

// OEMs
export const getOEMs = () => get("/oems/")
export const getOEM = (id: string) => get(`/oems/${id}`)
export const createOEM = (body: any) => post("/oems/", body)

// Components
export const getComponents = () => get("/components/")
export const getComponent = (id: string) => get(`/components/${id}`)
export const getComponentParams = (id: string) => get(`/components/${id}/parameters`)
export const uploadDatasheet = (file: File, oemName: string, modelName: string, category: string = "Cell") => {
  const fd = new FormData()
  fd.append("file", file)
  fd.append("oem_name", oemName)
  fd.append("model_name", modelName)
  fd.append("category", category)
  return uploadFile("/components/upload-datasheet", fd)
}
export const getCategories = () => get("/components/categories")
export const uploadComplianceSheet = (file: File, oemName: string, modelName: string) => {
  const fd = new FormData()
  fd.append("file", file)
  fd.append("oem_name", oemName)
  fd.append("model_name", modelName)
  return uploadFile("/components/upload-compliance-sheet", fd)
}

// Projects
export const getProjects = () => get("/projects/")
export const getProject = (id: string) => get(`/projects/${id}`)
export const createProject = (body: any) => post("/projects/", body)

// Sheets
export const getSheets = () => get("/sheets/")
export const getSheet = (id: string) => get(`/sheets/${id}`)
export const createSheet = (projectId: string, componentId: string) =>
  post("/sheets/", { project_id: projectId, component_id: componentId })

// Templates
export const getTemplates = () => get("/templates/")

// Workflow
export const getPendingWorkflows = () => get("/workflow/pending")
export const getWorkflowCount = () => get("/workflow/count")
export const advanceWorkflow = (sheetId: string, body: any) =>
  post(`/workflow/${sheetId}/advance`, body)

// RFQ
export const getRFQs = () => get("/rfq/")
export const getRFQ = (id: string) => get(`/rfq/${id}`)
export const matchRFQ = (id: string) => get(`/rfq/${id}/match`)
export const createRFQ = (body: any) => post("/rfq/", body)
export const uploadRFQ = (file: File, customerName: string, projectName: string) => {
  const fd = new FormData()
  fd.append("file", file)
  fd.append("customer_name", customerName)
  fd.append("project_name", projectName)
  return uploadFile("/rfq/upload", fd)
}

// Comparison
export const getComparisonMatrix = (modelIds: string[]) =>
  get(`/comparison/matrix?model_ids=${modelIds.join(",")}`)

// Documents
export const getDocuments = () => get("/documents/")
export const generateTechnicalSignal = (body: any) => post("/documents/technical-signal", body)

// Mail
export const sendTechnicalMail = (body: any) => post("/mail/technical", body)

// Pipeline
export const getPipeline = () => get("/pipeline/")
export const getPipelineStats = () => get("/pipeline/stats")
export const getDeal = (id: string) => get(`/pipeline/${id}`)
export const createDeal = (body: any) => post("/pipeline/", body)
export const advanceDeal = (id: string, body: any) => post(`/pipeline/${id}/advance`, body)

// Google Drive Fetcher
export const searchDrive = (query: string, type: string = "") =>
  get(`/gdrive/search?q=${encodeURIComponent(query)}${type ? `&type=${type}` : ""}`)
export const fetchAndExtract = (body: {
  file_id: string; file_name: string; oem_name: string; model_name: string; category: string
}) => post("/gdrive/fetch-and-extract", body)
