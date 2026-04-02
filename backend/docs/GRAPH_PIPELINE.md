# GraphRAG Pipeline Documentation

## Overview

The MiroFish backend implements a sophisticated GraphRAG (Graph Retrieval-Augmented Generation) pipeline that integrates knowledge graphs with social media simulation (OASIS) for generating contextual reports. The pipeline consists of four main phases:

```
┌─────────────────────────────────────────────────────────────────────┐
│                    GraphRAG Pipeline Flow                            │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  1. SEED EXTRACTION          2. GRAPH CONSTRUCTION                  │
│  ┌──────────────────┐         ┌──────────────────┐                  │
│  │ Document Upload   │         │ Ontology Define  │                  │
│  │ + Ontology Gen   │────────▶│ + Chunk & Index  │                  │
│  │ (LLM-powered)    │         │ (Zep Cloud API)  │                  │
│  └──────────────────┘         └────────┬─────────┘                  │
│                                        │                             │
│                                        ▼                             │
│  4. REPORT GENERATION    3. SIMULATION & MEMORY                      │
│  ┌──────────────────┐         ┌──────────────────┐                  │
│  │ Zep Retrieval    │◀────────│ Agent Profiles    │                  │
│  │ + ReACT Agent    │         │ + Memory Injection│                  │
│  │ (Report Agent)   │         │ (Zep Updater)     │                  │
│  └──────────────────┘         └──────────────────┘                  │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

## Phase 1: Seed Extraction (Ontology Generation)

**Files**: `app/services/ontology_generator.py`

### Process
1. **Document Upload**: User uploads documents (PDF, MD, TXT) via `POST /api/graph/ontology/generate`
2. **Text Extraction**: `FileParser.extract_text()` extracts raw text content
3. **LLM-powered Analysis**: `OntologyGenerator.generate()` sends text + simulation requirement to LLM
4. **Schema Extraction**: LLM outputs entity types and relationship types

### Ontology Structure
```python
{
    "entity_types": [
        {
            "name": "Student",           # PascalCase
            "description": "A student entity...",
            "attributes": [{"name": "full_name", "type": "text", ...}],
            "examples": ["Zhang Wei", "Li Ming"]
        },
        ... (exactly 10 types required, last 2 must be Person & Organization fallbacks)
    ],
    "edge_types": [
        {
            "name": "WORKS_FOR",         # UPPER_SNAKE_CASE
            "description": "Employment relationship",
            "source_targets": [{"source": "Person", "target": "Organization"}]
        },
        ... (6-10 relationship types)
    ]
}
```

### Key Constraints
- **Exactly 10 entity types**: 8 specific + 2 fallback (Person, Organization)
- **Zep API limits**: Max 10 custom entity types, 10 custom edge types
- **Reserved attribute names**: `name`, `uuid`, `group_id`, `name_embedding`, `summary`, `created_at`

---

## Phase 2: Graph Construction (Zep Cloud)

**Files**: 
- `app/services/graph_builder.py`
- `app/api/graph.py` (API endpoints)

### Construction Flow
```
build_graph_async(text, ontology)
    │
    ├── 1. create_graph()        → Zep Cloud creates empty graph
    │
    ├── 2. set_ontology()         → Register entity/edge types with Zep
    │
    ├── 3. split_text()          → Chunk text (default: 500 chars, 50 overlap)
    │
    ├── 4. add_text_batches()     → Send chunks as EpisodeData to Zep
    │                               (batches of 3, with 1s delay)
    │
    ├── 5. _wait_for_episodes()   → Poll each episode until processed=true
    │
    └── 6. _get_graph_info()      → Fetch node/edge counts
```

### Key Classes
- **GraphBuilderService**: Main orchestrator for graph construction
- **GraphInfo**: Dataclass with `graph_id`, `node_count`, `edge_count`, `entity_types`
- **TextProcessor**: Handles text chunking with overlap

### API Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/graph/ontology/generate` | Upload docs, generate ontology |
| POST | `/api/graph/build` | Build graph from project |
| GET | `/api/graph/data/<graph_id>` | Get full graph data |
| DELETE | `/api/graph/delete/<graph_id>` | Delete graph |
| GET | `/api/graph/task/<task_id>` | Query build task status |

---

## Phase 3: Memory Injection (Simulation-Graph Sync)

**Files**: 
- `app/services/zep_graph_memory_updater.py`
- `app/services/simulation_runner.py`

### Memory Updater Flow
```
SimulationRunner.start_simulation(enable_graph_memory_update=True, graph_id=...)
    │
    └── ZepGraphMemoryManager.create_updater(simulation_id, graph_id)
            │
            └── ZepGraphMemoryUpdater.start()
                    │
                    └── _worker_loop() [background thread]
                            │
                            ├── Queue: receives AgentActivity from simulation
                            ├── Platform Buffers: accumulate BATCH_SIZE=5 per platform
                            └── _send_batch_activities() → Zep Graph Add API
```

### AgentActivity Structure
```python
@dataclass
class AgentActivity:
    platform: str           # twitter / reddit
    agent_id: int
    agent_name: str
    action_type: str        # CREATE_POST, LIKE_POST, FOLLOW, etc.
    action_args: Dict[str, Any]  # Full context (post content, target user, etc.)
    round_num: int
    timestamp: str
```

### Activity → Episode Conversion
Each `AgentActivity.to_episode_text()` generates natural language:
```
"Zhang Wei: 发布了第一条帖子：「学术诚信是教育的基石」"
"Li Ming: 点赞了Wang Fang的帖子：「支持正当学术调查」"
```

### Memory Injection Features
- **Per-platform batching**: Twitter/Reddit accumulate separately (BATCH_SIZE=5)
- **Rich context**: action_args includes full post content, author info, etc.
- **Filtering**: `DO_NOTHING` activities are skipped
- **Retry mechanism**: 3 retries with exponential backoff

---

## Phase 4: Query/Retrieval (Report Agent)

**Files**: 
- `app/services/zep_tools.py` (retrieval tools)
- `app/services/report_agent.py` (ReACT agent)

### Retrieval Tools

| Tool | Purpose | Method |
|------|---------|--------|
| **InsightForge** | Deep multi-dimensional search, auto-generates sub-queries | `insight_forge()` |
| **PanoramaSearch** | Full graph view including historical/expired facts | `panorama_search()` |
| **QuickSearch** | Fast simple search | `search_graph()` |
| **InterviewAgents** | Multi-perspective agent interviews | `interview_agents()` |

### Search Flow
```python
ZepToolsService.search_graph(graph_id, query, limit=10, scope="edges")
    │
    ├── Zep.graph.search()  # Hybrid search (semantic + BM25)
    │                       # Reranker: cross_encoder
    │
    └── Returns SearchResult:
            - facts: List[str]
            - edges: List[Dict]
            - nodes: List[Dict]
            - total_count: int
```

### ReACT Report Agent
```python
ReportAgent.generate_report(simulation_requirement, graph_id)
    │
    ├── 1. Planning: LLM designs report outline
    │
    └── 2. Section Generation (per section):
            │
            └── ReACT Loop (max 5 iterations):
                    │
                    ├── Thought: LLM analyzes what info needed
                    │
                    ├── Action: Call retrieval tool (InsightForge, etc.)
                    │
                    ├── Observation: Parse tool results
                    │
                    └── Final Answer: Generate section content
```

---

## Integration Points

### With OASIS Simulation Engine
| Component | Integration | File |
|-----------|-------------|------|
| **SimulationRunner** | Creates ZepGraphMemoryUpdater when simulation starts | `simulation_runner.py:378` |
| **Agent Actions** | Activities flow from simulation → Memory Updater | `simulation_runner.py:24` |
| **Profile Generator** | Reads entities from Zep to create OASIS profiles | `oasis_profile_generator.py` |

### With Zep Cloud Memory
| Component | Integration | File |
|-----------|-------------|------|
| **GraphBuilder** | Creates/updates Zep Standalone Graph | `graph_builder.py` |
| **ZepGraphMemoryUpdater** | Streams simulation events to Zep | `zep_graph_memory_updater.py` |
| **ZepEntityReader** | Reads/ilters entities from Zep | `zep_entity_reader.py` |
| **ZepToolsService** | Provides retrieval tools to Report Agent | `zep_tools.py` |

### With Frontend API
| Endpoint | Purpose | Flow |
|----------|---------|------|
| `POST /api/graph/ontology/generate` | Upload + ontology | User → Backend → LLM → Response |
| `POST /api/graph/build` | Build graph | User → Backend → Zep → Progress polling |
| `POST /api/simulation/create` | Create simulation | User → Backend → State saved |
| `POST /api/simulation/prepare` | Prepare agents | Backend → ZepEntityReader → OasisProfileGenerator |
| `POST /api/simulation/start` | Run simulation | Backend → OASIS + ZepGraphMemoryUpdater |
| `POST /api/report/generate` | Generate report | Backend → ReportAgent (ZepTools) → Report |

---

## Data Flow Summary

```
1. DOCUMENTS
   └── [Upload] → FileParser.extract_text()
                  └── OntologyGenerator.generate() [LLM]
                        └── Ontology Schema

2. KNOWLEDGE GRAPH (Zep Cloud)
   └── GraphBuilderService.build_graph_async()
        ├── create_graph()
        ├── set_ontology()
        ├── split_text() [TextProcessor]
        ├── add_text_batches() → EpisodeData
        └── _wait_for_episodes()

3. SIMULATION (OASIS)
   └── SimulationManager.prepare_simulation()
        ├── ZepEntityReader.filter_defined_entities()
        └── OasisProfileGenerator.generate_profiles_from_entities()
            └── SimulationRunner.start_simulation()
                  └── ZepGraphMemoryUpdater [background]
                        └── add_batch() → Zep Graph

4. RETRIEVAL (Report Agent)
   └── ReportAgent.generate_report()
        └── ZepToolsService.insight_forge() / search_graph()
             └── Zep.graph.search()

5. REPORT
   └── ReACT Loop → Final markdown report
```

---

## Key Files Summary

| File | Lines | Purpose |
|------|-------|---------|
| `app/services/graph_builder.py` | 506 | Zep Graph construction service |
| `app/services/zep_graph_memory_updater.py` | 554 | Simulation→Graph memory sync |
| `app/services/zep_entity_reader.py` | 437 | Entity filtering and retrieval |
| `app/services/zep_tools.py` | 1736 | Retrieval tools for Report Agent |
| `app/services/ontology_generator.py` | 506 | LLM-powered ontology generation |
| `app/services/oasis_profile_generator.py` | 1205 | Entity→Agent profile conversion |
| `app/services/report_agent.py` | 2572 | ReACT report generation agent |
| `app/services/simulation_runner.py` | 1768 | OASIS simulation orchestration |
| `app/services/simulation_manager.py` | 529 | Simulation lifecycle management |
| `app/api/graph.py` | 622 | Graph API endpoints |
| `app/api/simulation.py` | 2716 | Simulation API endpoints |
| `app/utils/zep_paging.py` | 143 | Zep pagination utilities |
| `app/config.py` | 75 | Configuration management |

---

## Issues & Improvements Noted

1. **No dedicated "seed" extraction**: The term "seed" isn't explicitly used - instead, entities are extracted via LLM-powered ontology generation then used as seeds for simulation.

2. **Ontology validation happens post-LLM**: LLM output is validated/processed in `_validate_and_process()` - could add more robust validation.

3. **Parallel profile generation**: `OasisProfileGenerator` supports `parallel_count` parameter but implementation could benefit from async/await instead of threading.

4. **No explicit GraphRAG query routing**: The pipeline doesn't have explicit routing between different retrieval strategies - relies on Report Agent's ReACT loop to decide.

5. **Episode polling timeout**: `_wait_for_episodes()` has a 600s timeout - could be configurable or use webhooks if Zep supports.

6. **No graph updating after initial build**: Once graph is built, there's no mechanism to update entity/edge types - only new episodes are added via memory injection.
