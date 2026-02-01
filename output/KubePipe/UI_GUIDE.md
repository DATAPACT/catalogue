# KubePipe UI - Setup and Usage Guide

## 📋 Overview

The KubePipe UI is a modern web-based interface for managing and monitoring your pipeline orchestration platform. It provides an intuitive dashboard for:

- Managing Kubeflow Pipelines (KFP)
- Deploying Argo Workflows
- Monitoring pipeline runs and status
- Viewing sustainability metrics (CO₂ and energy)
- Tracking GDPR compliance
- Embedded Kubeflow UI access

## 🚀 Quick Start

### Prerequisites

1. **Node.js 18+** and npm installed - **REQUIRED!**
   - Check version: `node --version` (must show v18.x.x or higher)
   - If you have Node.js < 18, see [Node.js Upgrade Guide](../NODEJS_UPGRADE.md)
   - ⚠️ **The UI will not work with Node.js 12-17** - you'll see errors
2. **KubePipe API** running (see [API Setup](#api-setup) below)
3. **Kubeflow Pipelines** (optional, for full functionality)

### 1. Install Dependencies

```bash
cd ui
npm install
```

### 2. Start Development Server

```bash
# From ui/ directory
npm run dev

# Or from project root
bash scripts/start_ui.sh
```

The UI will be available at: **http://localhost:3000**

### 3. Start the API Backend

In a separate terminal:

```bash
# From project root
uv run uvicorn kubepipe.api.main:app --reload --host 127.0.0.1 --port 8000
```

The API will be available at: **http://127.0.0.1:8000**

## 📡 API Setup

The UI requires the KubePipe FastAPI backend to be running. Here's how to set it up:

### Development Mode (Mock Execution)

Perfect for local development without Kubernetes:

```bash
# Start API in mock mode (default)
uv run uvicorn kubepipe.api.main:app --reload --host 127.0.0.1 --port 8000
```

### Production Mode (with Kubeflow)

For real pipeline execution with Kubeflow Pipelines:

```bash
# 1. Port-forward Kubeflow services
kubectl -n kubeflow port-forward svc/ml-pipeline 8888:8888

# 2. Set environment variables
export KUBEPIPE_EXECUTION_MODE=kfp
export KUBEPIPE_KFP_HOST=http://127.0.0.1:8888

# 3. Start API
uv run uvicorn kubepipe.api.main:app --reload --host 127.0.0.1 --port 8000
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the `ui/` directory:

```env
# API endpoint (default: /api/v1 proxied to localhost:8000)
VITE_API_URL=http://127.0.0.1:8000/api/v1
```

### Runtime Configuration

Use the **Settings** page in the UI to configure:

- Execution mode (Mock or KFP)
- KFP API host
- KFP UI URL
- Namespaces for Kubeflow and Argo
- Caching settings

## 📂 Project Structure

```
ui/
├── src/
│   ├── api/
│   │   └── client.js          # API client with axios
│   ├── components/
│   │   ├── Layout.jsx          # Main layout with sidebar
│   │   ├── Card.jsx            # Card components
│   │   ├── Button.jsx          # Button component
│   │   ├── Badge.jsx           # Status badges
│   │   └── LoadingSpinner.jsx  # Loading indicator
│   ├── pages/
│   │   ├── Dashboard.jsx       # Main dashboard
│   │   ├── Pipelines.jsx       # KFP pipeline management
│   │   ├── ArgoWorkflows.jsx   # Argo workflow deployment
│   │   ├── Runs.jsx            # Pipeline run tracking
│   │   ├── KubeflowUI.jsx      # Embedded Kubeflow UI
│   │   ├── Sustainability.jsx  # Carbon & energy metrics
│   │   ├── Compliance.jsx      # GDPR compliance
│   │   └── Settings.jsx        # Configuration
│   ├── App.jsx                 # Main app with routing
│   ├── main.jsx                # Entry point
│   └── index.css               # Global styles
├── index.html
├── package.json
├── vite.config.js              # Vite configuration
└── README.md
```

## 🎯 Features Guide

### 1. Dashboard

**Purpose**: Overview of your pipeline orchestration platform

**Features**:
- System health status
- Pipeline statistics (total runs, active pipelines, workflows)
- Recent activity feed
- Quick access cards

**Usage**: Navigate to `/dashboard` (default page)

### 2. KFP Pipelines

**Purpose**: Manage and execute Kubeflow Pipelines

**Features**:
- View available pipelines
- Execute pipelines with parameters
- Simulate pipeline execution (dry run)
- Compile pipelines to YAML
- View execution results

**Usage**:
1. Select a pipeline from the list
2. Click "Execute Pipeline" to run it
3. Click "Simulate" to test without execution
4. Click "Compile" to generate YAML artifact

### 3. Argo Workflows

**Purpose**: Deploy and manage Argo Workflows

**Features**:
- Deploy workflows from YAML
- Monitor workflow status
- View workflow progress
- Delete workflows
- Load example workflows

**Usage**:
1. Paste Argo Workflow YAML or click "Example"
2. Set namespace (default: `argo`)
3. Click "Deploy" to submit to Kubernetes
4. Monitor status in the workflow list

### 4. Pipeline Runs

**Purpose**: Track pipeline execution history

**Features**:
- View all pipeline runs
- Check run status (Running, Succeeded, Failed)
- View run details and metadata
- Monitor duration and timestamps
- Direct link to Kubeflow UI

**Usage**:
1. Click on any run to view details
2. Use "Refresh" to update status
3. Click "View in Kubeflow UI" for detailed logs

### 5. Kubeflow UI (Embedded)

**Purpose**: Access Kubeflow Pipelines dashboard within KubePipe

**Features**:
- Embedded iframe of Kubeflow UI
- Configurable URL
- Fallback to external link
- Setup instructions

**Prerequisites**:
```bash
# Port-forward Kubeflow UI
kubectl -n kubeflow port-forward svc/ml-pipeline-ui 8080:80
```

**Usage**:
1. Ensure port-forward is active
2. Configure URL in Settings (default: http://127.0.0.1:8080)
3. View embedded UI or open in new tab

### 6. Sustainability Metrics

**Purpose**: Monitor environmental impact of ML training

**Features**:
- CO₂ emissions tracking
- Energy consumption monitoring
- Historical trend charts
- Breakdown by pipeline stage
- Optimization recommendations

**Data Source**: CodeCarbon integration in pipelines

**Usage**: View metrics automatically collected during pipeline runs

### 7. GDPR Compliance

**Purpose**: Track privacy and data protection compliance

**Features**:
- Privacy risk assessment status
- Applied mitigations (PII anonymization, data minimization)
- Compliance workflow visualization
- GDPR feature overview

**Data Source**: Privacy risk assessment components in pipelines

**Usage**: Review compliance status after executing pipelines with sensitive data

### 8. Settings

**Purpose**: Configure platform connections and preferences

**Features**:
- Execution mode (Mock/KFP)
- Kubeflow API and UI URLs
- Namespace configuration
- Caching settings
- Environment variable preview

**Usage**:
1. Adjust settings as needed
2. Click "Save Settings" to persist
3. Restart UI if needed for some changes

## 🐛 Troubleshooting

### UI Can't Connect to API

**Error**: `Network Error` or `Connection Refused`

**Solutions**:
1. Ensure API is running: `curl http://127.0.0.1:8000/`
2. Check proxy in `vite.config.js`
3. Verify CORS settings in API

### Kubeflow UI Won't Load

**Error**: Iframe shows error or blank page

**Solutions**:
1. Verify port-forward:
   ```bash
   kubectl -n kubeflow port-forward svc/ml-pipeline-ui 8080:80
   ```
2. Check URL in Settings
3. Try opening in new tab (CORS issue)
4. Ensure Kubeflow is installed in your cluster

### Argo Workflows Not Deploying

**Error**: `Deployment failed`

**Solutions**:
1. Install Argo Workflows:
   ```bash
   kubectl create namespace argo
   kubectl apply -n argo -f https://github.com/argoproj/argo-workflows/releases/latest/download/install.yaml
   ```
2. Check namespace exists
3. Verify YAML syntax
4. Check API logs for details

### Port 3000 Already in Use

**Error**: `Port 3000 is already in use`

**Solutions**:
```bash
# Use different port
npm run dev -- --port 3001

# Or kill existing process
lsof -ti:3000 | xargs kill -9
```

### Build Errors

**Error**: Module not found or build failures

**Solutions**:
```bash
# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install

# Clear Vite cache
rm -rf .vite
```

## 🔒 Security Notes

- **CORS**: Currently configured for `localhost:3000`. Update in `kubepipe/api/main.py` for production.
- **Authentication**: Not implemented. Add authentication middleware for production use.
- **Secrets**: Don't store secrets in localStorage. Use secure backend storage.
- **Iframe**: Kubeflow UI embedding may be blocked by CSP. Use "Open in New Tab" if needed.

## 📈 Performance Tips

1. **Enable Caching**: Turn on pipeline caching in Settings for faster reruns
2. **Mock Mode**: Use mock execution mode for development to avoid cluster overhead
3. **Lazy Loading**: Components load on demand, no need to optimize
4. **API Batching**: Dashboard makes minimal API calls, metrics are cached

## 🚀 Production Deployment

### Build for Production

```bash
cd ui
npm run build
```

This creates optimized static files in `ui/dist/`.

### Serve with API

Option 1: **Serve UI from FastAPI**

```python
# In kubepipe/api/main.py, add:
from fastapi.staticfiles import StaticFiles

app.mount("/", StaticFiles(directory="ui/dist", html=True), name="ui")
```

Option 2: **Separate Nginx Server**

```nginx
server {
    listen 80;
    
    location / {
        root /path/to/ui/dist;
        try_files $uri $uri/ /index.html;
    }
    
    location /api {
        proxy_pass http://localhost:8000;
    }
}
```

Option 3: **Docker Container**

```dockerfile
FROM node:18 AS build
WORKDIR /app
COPY ui/package*.json ./
RUN npm install
COPY ui/ ./
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
```

## 📚 Additional Resources

- [React Documentation](https://react.dev/)
- [Vite Guide](https://vitejs.dev/guide/)
- [Tailwind CSS](https://tailwindcss.com/docs)
- [Kubeflow Pipelines](https://www.kubeflow.org/docs/components/pipelines/)
- [Argo Workflows](https://argoproj.github.io/workflows/)

## 🤝 Contributing to UI

1. Follow React best practices
2. Use functional components with hooks
3. Keep components small and focused
4. Add loading states for async operations
5. Handle errors gracefully
6. Use Tailwind utility classes
7. Test with both mock and real API modes

## 📝 License

Same as KubePipe project (TBD)

---

**Need Help?** Contact: rajashekar.kolichala@uibk.ac.at
