# Argo Workflow → Kubeflow Pipeline Converter

Automatic converter that transforms Argo Workflow YAML files into Kubeflow Pipeline Python DSL code.

## Features

- ✓ **Automatic conversion** from Argo Workflow YAML to Kubeflow Pipeline Python
- ✓ **Container-based components** preserved with original images and commands
- ✓ **DAG dependencies** automatically extracted and converted
- ✓ **Sequential steps** supported
- ✓ **Auto-compilation** to KFP YAML format

## Quick Start

### Method 1: Demo Script (Recommended)

```bash
# Convert and compile in one go
uv run python demo_converter.py
```

This will:
1. Convert `examples/argo/hello-world.yaml` to Python
2. Compile it to Kubeflow Pipeline YAML
3. Show you where the files are saved

### Method 2: Programmatic Usage

```python
from kubepipe.core.argo_to_kfp_converter import convert_argo_to_kfp

# Convert Argo YAML to KFP Python
convert_argo_to_kfp(
    "examples/argo/hello-world.yaml",
    "output.py"
)
```

### Method 3: CLI Tool (has version compatibility issues currently)

```bash
# Note: Requires fixing typer version compatibility
python cli_converter.py convert examples/argo/hello-world.yaml
```

## Example Conversion

**Input: Argo Workflow (YAML)**
```yaml
apiVersion: argoproj.io/v1alpha1
kind: Workflow
metadata:
  generateName: hello-world-
spec:
  entrypoint: hello
  templates:
    - name: hello
      container:
        image: busybox
        command: [echo]
        args: ["Hello World!"]
```

**Output: Kubeflow Pipeline (Python)**
```python
from kfp import dsl

@dsl.component(base_image='busybox')
def hello_op():
    """hello component."""
    import subprocess
    result = subprocess.run(['echo', 'Hello World!'], 
                          capture_output=True, text=True)
    print(result.stdout)

@dsl.pipeline(name='hello_world')
def hello_world_pipeline():
    task = hello_op()
    task.set_display_name('hello')
```

## Supported Argo Features

| Argo Feature | Conversion Status |
|--------------|-------------------|
| Container templates | ✓ Supported |
| Command & Args | ✓ Supported |
| Image specification | ✓ Supported |
| DAG workflows | ✓ Supported |
| Sequential steps | ✓ Supported |
| Dependencies | ✓ Supported |
| Environment variables | ⚠️ Partial |
| Resource requests | ⚠️ Partial |
| Volumes & ConfigMaps | ✗ Not yet |
| Conditionals | ✗ Not yet |

## Architecture

```
┌─────────────────────┐
│  Argo Workflow YAML │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────────┐
│ ArgoToKFPConverter      │
│  - Parse YAML           │
│  - Extract templates    │
│  - Generate components  │
│  - Build pipeline       │
└──────────┬──────────────┘
           │
           ▼
┌─────────────────────────┐
│  KFP Python DSL Code    │
└──────────┬──────────────┘
           │
           ▼
┌─────────────────────────┐
│  KFP Compiler           │
└──────────┬──────────────┘
           │
           ▼
┌─────────────────────────┐
│  KFP Pipeline YAML      │
│  (Ready to deploy)      │
└─────────────────────────┘
```

## Files Created

- **kubepipe/core/argo_to_kfp_converter.py** - Main converter class
- **demo_converter.py** - Simple demo script
- **cli_converter.py** - CLI tool (has typer compatibility issues)

## Deployment Workflow

1. **Convert** Argo YAML → KFP Python
   ```bash
   uv run python demo_converter.py
   ```

2. **Review** generated Python code
   ```bash
   cat examples/hello-world_kfp_auto_converted.py
   ```

3. **Deploy** compiled YAML to Kubeflow
   - Upload `artifacts/hello_world_kfp_pipeline.yaml` to KFP UI
   - Or use KubePipe API to submit

## Limitations

- **Complex workflows**: Multi-stage DAGs may need manual adjustment
- **Custom resources**: PVCs, ConfigMaps not auto-converted
- **Conditionals**: When/if conditions require manual implementation
- **Loops**: Argo loops need to be rewritten using KFP ParallelFor

## Future Enhancements

- [ ] Support for Argo conditionals (`when`)
- [ ] Loop conversion (Argo → KFP ParallelFor)
- [ ] Volume and ConfigMap handling
- [ ] Artifact passing between steps
- [ ] Parameter propagation
- [ ] Resource requests/limits conversion
- [ ] Fix Typer CLI compatibility

## Usage in KubePipe

The converter integrates with KubePipe's existing workflow:

```bash
# Traditional: Deploy Argo directly
kubepipe argo-deploy examples/argo/my-workflow.yaml

# New: Convert to KFP then deploy
uv run python demo_converter.py
# Then upload artifacts/*.yaml to KFP UI
```

This gives you the flexibility to:
- Keep using Argo for container-native workflows
- Convert to KFP when you need ML pipeline features
- Mix and match based on your use case
