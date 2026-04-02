# MiroFish API Documentation

**Base URL:** `http://localhost:5001/api`

**Framework:** Flask
**Documentation:** This file

---

## Overview

MiroFish API provides endpoints for:
- **Graph Management** - Upload documents, generate ontology, build knowledge graphs
- **Simulation** - Create and run multi-agent simulations
- **Entity Operations** - Read and filter entities from graphs
- **Report Generation** - Query simulation results

---

## API Endpoints

### Graph API (`/api/graph/`)

#### Project Management

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/project/<project_id>` | Get project details |
| GET | `/project/list` | List all projects |
| DELETE | `/project/<project_id>` | Delete a project |
| POST | `/project/<project_id>/reset` | Reset project state |

**GET /project/list**
```json
// Response
{
  "success": true,
  "data": [...],
  "count": 5
}
```

#### Ontology Generation

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/ontology/generate` | Upload files and generate ontology |

**POST /ontology/generate**
- Content-Type: `multipart/form-data`
- Parameters:
  - `files` (required): PDF/MD/TXT files
  - `simulation_requirement` (required): Simulation description
  - `project_name` (optional): Project name
  - `additional_context` (optional): Extra context

```json
// Response
{
  "success": true,
  "data": {
    "project_id": "proj_xxxx",
    "ontology": {
      "entity_types": [...],
      "edge_types": [...]
    },
    "analysis_summary": "...",
    "files": [...],
    "total_text_length": 12345
  }
}
```

#### Graph Building

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/build` | Build knowledge graph from project |
| GET | `/build/status/<task_id>` | Get graph build task status |

**POST /build**
```json
// Request
{
  "project_id": "proj_xxxx",
  "graph_name": "My Graph",
  "chunk_size": 500,
  "chunk_overlap": 50,
  "force": false
}

// Response
{
  "success": true,
  "data": {
    "project_id": "proj_xxxx",
    "task_id": "task_xxxx",
    "message": "Graph build task started"
  }
}
```

---

### Simulation API (`/api/simulation/`)

#### Entity Reading

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/entities/<graph_id>` | Get all filtered entities |
| GET | `/entities/<graph_id>/<entity_uuid>` | Get single entity details |
| GET | `/entities/<graph_id>/by-type/<entity_type>` | Get entities by type |

**GET /entities/<graph_id>**
- Query params:
  - `entity_types`: Comma-separated entity types
  - `enrich`: Include edge info (default: true)

#### Simulation Management

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/create` | Create new simulation |
| POST | `/prepare` | Prepare simulation environment |
| GET | `/prepare/status/<task_id>` | Get prepare task status |
| POST | `/run` | Run simulation |
| GET | `/run/status/<simulation_id>` | Get simulation status |
| POST | `/stop` | Stop running simulation |
| GET | `/status/<simulation_id>` | Get simulation state |
| GET | `/list` | List simulations |

**POST /create**
```json
// Request
{
  "project_id": "proj_xxxx",
  "graph_id": "mirofish_xxxx",
  "enable_twitter": true,
  "enable_reddit": true
}

// Response
{
  "success": true,
  "data": {
    "simulation_id": "sim_xxxx",
    "project_id": "proj_xxxx",
    "graph_id": "mirofish_xxxx",
    "status": "created"
  }
}
```

**POST /prepare**
```json
// Request
{
  "simulation_id": "sim_xxxx",
  "entity_types": ["Student", "PublicFigure"],
  "use_llm_for_profiles": true,
  "parallel_profile_count": 5,
  "force_regenerate": false
}

// Response
{
  "success": true,
  "data": {
    "simulation_id": "sim_xxxx",
    "task_id": "task_xxxx",
    "status": "preparing|ready",
    "already_prepared": false
  }
}
```

**POST /run**
```json
// Request
{
  "simulation_id": "sim_xxxx",
  "max_rounds": 10
}

// Response
{
  "success": true,
  "data": {
    "simulation_id": "sim_xxxx",
    "task_id": "task_xxxx",
    "status": "running"
  }
}
```

#### Agent Interaction

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/interview` | Interview an agent |
| POST | `/interview/batch` | Batch interview agents |

**POST /interview**
```json
// Request
{
  "simulation_id": "sim_xxxx",
  "entity_uuid": "entity-uuid",
  "prompt": "What do you think about...",
  "use_memory": true
}

// Response
{
  "success": true,
  "data": {
    "response": "Based on my memory...",
    "agent_id": "...",
    "memory_used": true
  }
}
```

---

### Report API (`/api/report/`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/generate` | Generate simulation report |
| GET | `/status/<task_id>` | Get report generation status |
| GET | `/result/<simulation_id>` | Get report result |

**POST /generate**
```json
// Request
{
  "simulation_id": "sim_xxxx",
  "query": "Analyze the simulation results...",
  "report_type": "deep_analysis|quick_summary"
}

// Response
{
  "success": true,
  "data": {
    "task_id": "task_xxxx",
    "status": "processing"
  }
}
```

---

### Memory API (`/api/memory/`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/history/<simulation_id>` | Get simulation memory history |
| GET | `/agent/<entity_uuid>` | Get agent memory |

---

## Response Format

All endpoints return JSON:

```json
{
  "success": true|false,
  "data": {...},
  "error": "Error message (if success=false)"
}
```

## HTTP Status Codes

| Code | Meaning |
|------|---------|
| 200 | Success |
| 400 | Bad Request (missing/invalid parameters) |
| 404 | Not Found |
| 500 | Internal Server Error |

---

## Configuration

Required environment variables:
- `LLM_API_KEY` - LLM API key
- `LLM_BASE_URL` - LLM API base URL
- `LLM_MODEL_NAME` - Model name
- `ZEP_API_KEY` - Zep Cloud API key

---

## Swagger/OpenAPI

Currently using Flask (not FastAPI) - no automatic Swagger generation.
API documentation maintained in this file.
