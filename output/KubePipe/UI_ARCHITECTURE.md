# KubePipe UI Architecture

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                            User's Web Browser                                │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      │ HTTP
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         KubePipe Web UI (React)                              │
│                         Running on localhost:3000                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐   │
│  │  Dashboard   │  │  Pipelines   │  │     Argo     │  │     Runs     │   │
│  └──────────────┘  └──────────────┘  └──────────────┘  └──────────────┘   │
│                                                                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐   │
│  │ Kubeflow UI  │  │Sustainability│  │  Compliance  │  │   Settings   │   │
│  └──────────────┘  └──────────────┘  └──────────────┘  └──────────────┘   │
│                                                                               │
│                         ┌──────────────────────┐                             │
│                         │   API Client (Axios) │                             │
│                         └──────────┬───────────┘                             │
└────────────────────────────────────┼─────────────────────────────────────────┘
                                     │
                                     │ REST API
                                     │ (Proxied in dev)
                                     ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                    KubePipe FastAPI Backend                                  │
│                    Running on localhost:8000                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                               │
│  API Endpoints:                                                               │
│  ├─ GET  /                           (Health check)                          │
│  ├─ GET  /api/v1/stats               (Dashboard statistics)                 │
│  ├─ POST /api/v1/simulate            (Pipeline simulation)                  │
│  ├─ POST /api/v1/compile             (Compile pipeline)                     │
│  ├─ POST /api/v1/execute             (Execute pipeline)                     │
│  ├─ GET  /api/v1/runs/{id}           (Get run status)                       │
│  ├─ POST /api/v1/argo/deploy         (Deploy Argo workflow)                 │
│  ├─ GET  /api/v1/argo/workflows      (List workflows)                       │
│  ├─ DELETE /api/v1/argo/workflows/{name} (Delete workflow)                  │
│  ├─ GET  /api/v1/sustainability/metrics  (Get metrics)                      │
│  └─ GET  /api/v1/compliance/report       (Get compliance)                   │
│                                                                               │
└────────────┬────────────────────────────────┬────────────────────────────────┘
             │                                │
             │                                │
             ▼                                ▼
┌─────────────────────────┐      ┌─────────────────────────┐
│  Kubeflow Pipelines     │      │    Argo Workflows       │
│  (via KFP SDK)          │      │    (via K8s API)        │
├─────────────────────────┤      ├─────────────────────────┤
│                         │      │                         │
│  • Submit runs          │      │  • Deploy workflows     │
│  • Get run status       │      │  • Monitor status       │
│  • Compile pipelines    │      │  • List workflows       │
│  • List experiments     │      │  • Delete workflows     │
│                         │      │                         │
│  Host: 127.0.0.1:8888   │      │  Via: kubectl/K8s API   │
│  Namespace: kubeflow    │      │  Namespace: argo        │
│                         │      │                         │
└────────────┬────────────┘      └────────────┬────────────┘
             │                                │
             │                                │
             ▼                                ▼
┌─────────────────────────────────────────────────────────────┐
│                   Kubernetes Cluster                         │
│                                                               │
│  ┌────────────────┐        ┌────────────────┐               │
│  │ KFP Pipelines  │        │ Argo Workflows │               │
│  │  - Pods        │        │  - Pods        │               │
│  │  - Services    │        │  - CRDs        │               │
│  │  - PVCs        │        │  - Controllers │               │
│  └────────────────┘        └────────────────┘               │
│                                                               │
└───────────────────────────────────────────────────────────────┘
```

## UI Component Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              App.jsx                                         │
│                         (React Router)                                       │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           Layout.jsx                                         │
│                    (Sidebar + Header + Content)                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                               │
│  ┌─────────────────┐                                                         │
│  │   Sidebar       │                                                         │
│  │  Navigation     │                                                         │
│  │                 │                                                         │
│  │  • Dashboard    │                                                         │
│  │  • Pipelines    │      ┌─────────────────────────────────┐               │
│  │  • Argo         │      │      Page Content               │               │
│  │  • Runs         │      │      (React Router Outlet)      │               │
│  │  • Kubeflow UI  │      │                                 │               │
│  │  • Sustainability│     │  Renders current page based on  │               │
│  │  • Compliance   │      │  route (Dashboard, Pipelines,   │               │
│  │  • Settings     │      │  etc.)                          │               │
│  │                 │      │                                 │               │
│  └─────────────────┘      └─────────────────────────────────┘               │
│                                                                               │
└───────────────────────────────────────────────────────────────────────────────┘
```

## Page Component Structure

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         Dashboard.jsx                                        │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                               │
│  State:                                                                       │
│  ├─ stats (total runs, pipelines, workflows)                                │
│  ├─ loading (boolean)                                                        │
│  └─ healthStatus (string)                                                    │
│                                                                               │
│  Effects:                                                                     │
│  └─ useEffect → fetchDashboardData()                                         │
│                   └─ api.healthCheck()                                       │
│                   └─ Set mock stats                                          │
│                                                                               │
│  Components:                                                                  │
│  ├─ Card (Stats display)                                                     │
│  ├─ Badge (Status indicators)                                                │
│  └─ LoadingSpinner                                                           │
│                                                                               │
└───────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                         Pipelines.jsx                                        │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                               │
│  State:                                                                       │
│  ├─ selectedPipeline (object)                                                │
│  ├─ executing (boolean)                                                      │
│  ├─ result (execution response)                                              │
│  └─ simulationResult (simulation response)                                   │
│                                                                               │
│  Actions:                                                                     │
│  ├─ handleExecute()    → api.execute()                                       │
│  ├─ handleSimulate()   → api.simulate()                                      │
│  └─ handleCompile()    → api.compile()                                       │
│                                                                               │
│  Components:                                                                  │
│  ├─ Card (Pipeline list, actions, results)                                  │
│  ├─ Button (Execute, Simulate, Compile)                                     │
│  └─ Badge (Status indicators)                                                │
│                                                                               │
└───────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                      ArgoWorkflows.jsx                                       │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                               │
│  State:                                                                       │
│  ├─ workflows (array)                                                        │
│  ├─ loading (boolean)                                                        │
│  ├─ yamlContent (string)                                                     │
│  ├─ deploying (boolean)                                                      │
│  └─ namespace (string)                                                       │
│                                                                               │
│  Actions:                                                                     │
│  ├─ fetchWorkflows()  → api.argoList()                                       │
│  ├─ handleDeploy()    → api.argoDeploy()                                     │
│  ├─ handleDelete()    → api.argoDelete()                                     │
│  └─ loadExample()     → Set example YAML                                     │
│                                                                               │
│  Components:                                                                  │
│  ├─ Card (Deploy form, workflow list)                                       │
│  ├─ Button (Deploy, Delete, Example)                                        │
│  ├─ Badge (Status: Running, Succeeded, Failed)                              │
│  └─ LoadingSpinner                                                           │
│                                                                               │
└───────────────────────────────────────────────────────────────────────────────┘
```

## Data Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         User Interaction                                     │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      │ Click "Execute Pipeline"
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                      Pipelines.jsx                                           │
│                 handleExecute() called                                       │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      │ setState({ executing: true })
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                      API Client (client.js)                                  │
│              api.execute({ pipeline_id, parameters })                        │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      │ POST /api/v1/execute
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                   FastAPI Backend (main.py)                                  │
│                 execute_pipeline() handler                                   │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      │ Calls KubePipeExecutor
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│               KubePipeExecutor (executor.py)                                 │
│                      submit_run()                                            │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                   ┌──────────────────┴──────────────────┐
                   │                                     │
        Mock Mode  ▼                          KFP Mode   ▼
    ┌──────────────────┐                 ┌──────────────────┐
    │ Return mock      │                 │ Submit to KFP    │
    │ response         │                 │ via KFP client   │
    └──────────────────┘                 └──────────────────┘
                   │                                     │
                   └──────────────────┬──────────────────┘
                                      │ Response
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                      API Response                                            │
│        { status, run_id, detail }                                            │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      │ axios returns
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                   Pipelines.jsx                                              │
│              setResult(response.data)                                        │
│              setState({ executing: false })                                  │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      │ Component re-renders
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                      UI Updates                                              │
│               Display execution result                                       │
│               Show run ID and status                                         │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Build & Development Flow

```
Development:
┌─────────────────────────────────────────────────────────────────────────────┐
│  npm run dev                                                                  │
│       ↓                                                                       │
│  Vite Dev Server                                                              │
│       ↓                                                                       │
│  1. Start server on port 3000                                                │
│  2. Enable Hot Module Replacement (HMR)                                      │
│  3. Proxy /api requests → localhost:8000                                     │
│  4. Compile React/JSX on-the-fly                                             │
│  5. Process Tailwind CSS                                                     │
│  6. Serve index.html + assets                                                │
└─────────────────────────────────────────────────────────────────────────────┘

Production Build:
┌─────────────────────────────────────────────────────────────────────────────┐
│  npm run build                                                                │
│       ↓                                                                       │
│  Vite Build Process                                                           │
│       ↓                                                                       │
│  1. Bundle React components                                                  │
│  2. Minify JavaScript                                                        │
│  3. Process and purge Tailwind CSS                                           │
│  4. Optimize assets (images, fonts)                                          │
│  5. Generate sourcemaps                                                      │
│  6. Output to ui/dist/                                                       │
│       ↓                                                                       │
│  Static Files Ready                                                           │
│  ├─ index.html                                                               │
│  ├─ assets/                                                                  │
│  │  ├─ index-[hash].js                                                       │
│  │  └─ index-[hash].css                                                      │
│  └─ ...                                                                       │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Configuration Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    Configuration Sources                                     │
└─────────────────────────────────────────────────────────────────────────────┘
                   │
     ┌─────────────┼─────────────┐
     │             │             │
     ▼             ▼             ▼
┌──────────┐  ┌──────────┐  ┌──────────┐
│ .env     │  │Settings  │  │Browser   │
│ file     │  │ Page     │  │localStorage│
└──────────┘  └──────────┘  └──────────┘
     │             │             │
     │             │             │
     └─────────────┼─────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                    Merged Configuration                                      │
│                                                                               │
│  Priority:                                                                    │
│  1. Settings Page (localStorage) - Highest                                   │
│  2. Environment Variables (.env)                                             │
│  3. Defaults in code - Lowest                                                │
└─────────────────────────────────────────────────────────────────────────────┘
```

This architecture provides:
- ✅ Clean separation of concerns
- ✅ Reusable components
- ✅ Centralized API communication
- ✅ Flexible configuration
- ✅ Easy to extend and maintain
