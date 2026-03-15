# MiroFish - Deep Codebase Analysis

## What Is MiroFish?

**"A Simple and Universal Swarm Intelligence Engine — Predicting Anything"**

MiroFish is a multi-agent AI prediction engine that simulates social media ecosystems and public opinion dynamics. It takes real-world seed information (news, policy documents, novels, financial data), builds a knowledge graph, spawns thousands of autonomous AI agents with distinct personalities and memories, and lets them interact on simulated Twitter and Reddit platforms. The emergent behavior of these agents produces predictions about how real-world events might unfold.

**Core Thesis:** Simulation-as-prediction — instead of training a model on historical data to extrapolate, you simulate the actual dynamics of a system (people, opinions, social networks) and observe what emerges.

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        Frontend (Vue 3 + Vite)                  │
│  Home → Graph Build → Env Setup → Simulation → Report → Chat   │
└──────────────────────────────┬──────────────────────────────────┘
                               │ REST API (Axios)
┌──────────────────────────────▼──────────────────────────────────┐
│                     Backend (Flask, port 5001)                  │
│  ┌──────────┐  ┌──────────────┐  ┌────────────┐                │
│  │ Graph API │  │ Simulation   │  │ Report API │                │
│  │ (617 LOC) │  │ API (2711)   │  │ (1015 LOC) │                │
│  └─────┬─────┘  └──────┬───────┘  └─────┬──────┘                │
│        │               │                │                       │
│  ┌─────▼───────────────▼────────────────▼──────┐                │
│  │            13 Service Modules                │                │
│  │  ontology_generator    graph_builder         │                │
│  │  zep_entity_reader     oasis_profile_gen     │                │
│  │  simulation_config_gen simulation_runner     │                │
│  │  simulation_manager    simulation_ipc        │                │
│  │  report_agent          zep_tools             │                │
│  │  zep_graph_updater     text_processor        │                │
│  └──────────────┬───────────────────────────────┘                │
│                 │                                                │
│  ┌──────────────▼───────────────────────────────┐                │
│  │           External Dependencies              │                │
│  │  • CAMEL-OASIS (multi-agent simulation)      │                │
│  │  • Zep Cloud (GraphRAG / memory)             │                │
│  │  • OpenAI-compatible LLM API (Qwen-plus)     │                │
│  └──────────────────────────────────────────────┘                │
└─────────────────────────────────────────────────────────────────┘
```

---

## The 5-Step Pipeline

### Step 1: Graph Construction
- User uploads seed documents (PDF, MD, TXT)
- LLM generates an ontology (10 entity types + relationship types)
- Zep Cloud builds a knowledge graph via GraphRAG
- Entities: Person, Organization, Event, Location, etc.
- Relationships: KNOWS, CRITICIZES, SUPPORTS, etc.

### Step 2: Environment Setup
- Entities are filtered from the knowledge graph
- LLM generates OASIS agent profiles with:
  - Persona, biography, MBTI, profession, sentiment bias
  - Activity schedule (time-zone-aware, peaks at 19-22h China time)
  - Stance (supportive/opposing/neutral/observer)
  - Platform-specific attributes (followers, karma, etc.)
- Simulation config is auto-generated from natural language requirements

### Step 3: Simulation Execution
- Parallel dual-platform simulation (Twitter + Reddit simultaneously)
- **Round-based:** each round = 60 simulated minutes
- Per round, each active agent:
  1. Reads its profile + recent memory from Zep
  2. LLM generates an action (CREATE_POST, LIKE, REPOST, REPLY, etc.)
  3. Action executed in platform simulator
  4. Results recorded as time-series
- Activity multipliers by time-of-day (dead hours 0-5am: 5%, peak 19-22h: 150%)
- Supports mid-simulation intervention (inject events, modify agents)

### Step 4: Report Generation
- ReACT-pattern Report Agent with tool use:
  - **InsightForge** — deep semantic search with sub-question generation
  - **PanoramaSearch** — broad contextual retrieval
  - **QuickSearch** — fast targeted queries
- Plans report structure → searches → writes → reflects (1-2 refinement rounds)
- Output: structured Markdown with agent quotes and tool citations

### Step 5: Deep Interaction
- Chat with individual simulated agents post-simulation
- Ask "why did you do X?" — agents respond from their simulated memory
- Explore counterfactual "what-if" scenarios
- Uses IPC to query frozen simulation state

---

## Key Technical Innovations

| Innovation | Description |
|---|---|
| **GraphRAG → Agent Generation** | Knowledge graphs auto-constructed from raw text, then converted to agent profiles |
| **Dual-Platform Parallelism** | Twitter + Reddit run simultaneously with shared memory/time |
| **Dynamic Intervention** | Pause simulation, inject breaking news, modify agent behavior, resume |
| **Agent Interview System** | Post-simulation interrogation via IPC to explore causal chains |
| **ReACT Report Generation** | Reports built with LLM tool-use pattern, maintaining full traceability |
| **Time-Aware Behavioral Realism** | Agents follow realistic daily activity patterns with timezone awareness |
| **Zero-Risk Policy Testing** | Test policies/strategies in simulation before real-world deployment |

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | Vue 3.5+, Vue Router, Axios, D3.js, Vite |
| Backend | Flask 3.0+, Python 3.11+ |
| LLM | OpenAI-compatible API (Alibaba Qwen-plus recommended) |
| Knowledge Graph | Zep Cloud 3.13 (GraphRAG) |
| Simulation Engine | CAMEL-OASIS 0.2.5 + CAMEL-AI 0.2.78 |
| Deployment | Docker / docker-compose |
| License | AGPL-3.0 |

---

## How to Integrate Simulation-as-Prediction Into Your Project

### Core Concepts to Extract

1. **The Agent Profile Model**
   - Each agent is a JSON blob: persona, biography, attributes, behavioral params
   - Activity level (0-1), sentiment bias (-1 to 1), stance, influence weight
   - This is domain-agnostic — adapt it to any simulation domain

2. **The Seed → Graph → Agents Pipeline**
   - Feed documents → LLM extracts ontology → GraphRAG builds knowledge graph → graph entities become agent profiles
   - This is the key automation: you don't hand-craft agents, the system generates them from source material

3. **Round-Based Simulation with LLM Decision-Making**
   - Each tick: active agents query LLM with their profile + memory → get action → execute
   - Memory updates propagate causally through the timeline
   - This pattern works for any domain: markets, politics, product adoption, etc.

4. **The Intervention Pattern**
   - Pause → inject new context → resume
   - Enables scenario branching and A/B testing of strategies

5. **Post-Simulation Analysis**
   - Agent interviews (why did you do X?)
   - ReACT-based report generation with search tools
   - This turns raw simulation data into actionable insights

### Integration Approaches

**Option A: Use MiroFish as a Service**
- Deploy MiroFish as-is, feed it your domain's seed data
- Use its API endpoints to trigger simulations programmatically
- Consume reports and agent interviews via API

**Option B: Extract the Simulation Core**
- Key files to port: `simulation_runner.py`, `oasis_profile_generator.py`, `simulation_config_generator.py`
- Swap OASIS for your own simulation environment if needed
- Keep the LLM-driven agent decision loop — it's the core innovation

**Option C: Adopt the Architecture Pattern**
- Implement the seed → graph → agents → simulate → analyze pipeline in your own stack
- Use any GraphRAG solution (Zep, Neo4j, custom)
- Use any multi-agent framework (CAMEL, AutoGen, CrewAI, custom)
- The pattern is more valuable than the specific implementation

### Key Dependencies to Evaluate

| Dependency | Role | Alternatives |
|---|---|---|
| Zep Cloud | Graph memory + RAG | Neo4j + LangChain, custom GraphRAG |
| CAMEL-OASIS | Social simulation engine | Custom agent loop, AutoGen, Mesa |
| Qwen-plus | LLM backbone | GPT-4o, Claude, Llama, any OpenAI-compatible |

### What Makes This Approach Powerful

1. **Emergent behavior** — you don't code the prediction, it emerges from agent interactions
2. **Explainability** — you can interview agents to understand *why* a prediction emerged
3. **Scenario testing** — branch simulations to test different interventions
4. **Domain flexibility** — same engine works for politics, markets, product launches, crisis management
5. **Natural language interface** — users describe what they want to predict, system handles the rest

---

## File Reference

| Path | Purpose | Lines |
|---|---|---|
| `backend/app/services/simulation_runner.py` | Core simulation execution | 1763 |
| `backend/app/services/report_agent.py` | ReACT report generation | 2571 |
| `backend/app/services/oasis_profile_generator.py` | Agent profile creation | 1200 |
| `backend/app/services/zep_tools.py` | Search tools for reports | 1735 |
| `backend/app/services/simulation_config_generator.py` | Auto config generation | 987 |
| `backend/app/api/simulation.py` | Simulation REST API | 2711 |
| `backend/app/api/report.py` | Report REST API | 1015 |
| `backend/app/api/graph.py` | Graph building REST API | 617 |
| `backend/scripts/run_parallel_simulation.py` | Dual-platform simulator | — |
| `frontend/src/components/Step1GraphBuild.vue` | Graph build UI | — |
| `frontend/src/components/Step3Simulation.vue` | Simulation control UI | — |
| `frontend/src/views/Process.vue` | Main workflow orchestrator | ~52KB |
