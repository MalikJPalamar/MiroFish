# MiroFish Frontend Architecture

## Overview
Vue 3 + Vite SPA with vue-router, vue-i18n, and Axios. No Pinia/Vuex -- uses simple reactive module pattern for state.

## Tech Stack
- **Framework**: Vue 3.5 (Composition API with `<script setup>`)
- **Build**: Vite 7.2
- **Router**: vue-router 4.6
- **i18n**: vue-i18n 11.3
- **HTTP**: axios 1.14
- **Visualization**: D3 7.9

## File Tree

```
frontend/
├── src/
│   ├── App.vue                    # Root component (router-view only)
│   ├── main.js                    # App bootstrap, registers router & i18n
│   │
│   ├── api/                       # API integration layer
│   │   ├── index.js               # Axios instance + interceptors + retry logic
│   │   ├── graph.js               # Ontology generation, graph build, project APIs
│   │   ├── simulation.js          # Full simulation CRUD + run control APIs
│   │   └── report.js              # Report generation + chat APIs
│   │
│   ├── components/
│   │   ├── GraphPanel.vue         # D3-based knowledge graph visualization
│   │   ├── HistoryDatabase.vue    # Historical simulation browser
│   │   ├── LanguageSwitcher.vue   # i18n locale toggle
│   │   ├── Step1GraphBuild.vue    # Step 1: Graph construction (ontology)
│   │   ├── Step2EnvSetup.vue      # Step 2: Simulation environment setup
│   │   ├── Step3Simulation.vue    # Step 3: Simulation execution
│   │   ├── Step4Report.vue        # Step 4: Report generation
│   │   └── Step5Interaction.vue   # Step 5: Post-simulation interaction/chat
│   │
│   ├── views/
│   │   ├── Home.vue               # Landing page with history + quick start
│   │   ├── MainView.vue           # Process container (orchestrates steps 1-5)
│   │   ├── Process.vue            # Step-based workflow controller
│   │   ├── SimulationView.vue     # Simulation detail + configuration
│   │   ├── SimulationRunView.vue  # Real-time simulation execution view
│   │   ├── ReportView.vue         # Report viewing + chat interface
│   │   └── InteractionView.vue    # Agent interaction panel
│   │
│   ├── router/
│   │   └── index.js               # 6 routes with dynamic params (projectId, simulationId, reportId)
│   │
│   ├── store/
│   │   └── pendingUpload.js       # Reactive module for pending file upload state
│   │
│   └── i18n/
│       └── index.js               # vue-i18n setup, dynamic locale import from /locales/
│
├── locales/                        # External to src/ (sibling directory)
│   ├── languages.json             # Available locale metadata
│   ├── en.json                    # English translations
│   └── zh.json                    # Chinese translations
│
├── index.html
├── vite.config.js
└── package.json
```

## Routes

| Path | Name | View | Params |
|------|------|------|--------|
| `/` | Home | Home.vue | - |
| `/process/:projectId` | Process | Process.vue | projectId |
| `/simulation/:simulationId` | Simulation | SimulationView.vue | simulationId |
| `/simulation/:simulationId/start` | SimulationRun | SimulationRunView.vue | simulationId |
| `/report/:reportId` | Report | ReportView.vue | reportId |
| `/interaction/:reportId` | Interaction | InteractionView.vue | reportId |

## State Management

**No Pinia/Vuex** -- uses simple reactive module pattern.

`src/store/pendingUpload.js` exports a reactive singleton `state` plus helper functions:
- `setPendingUpload(files, requirement)` -- store pending upload data
- `getPendingUpload()` -- retrieve pending state
- `clearPendingUpload()` -- reset state

Used for: Home page captures files/requirement → immediately navigates to Process → Process calls API.

## i18n Setup

- **Library**: vue-i18n (Composition API mode, `legacy: false`)
- **Locales**: Dynamically imported via `import.meta.glob` from `../../../locales/*.json`
- **Default**: Chinese (`zh`), fallback: Chinese
- **Persistence**: Locale saved to `localStorage` key `locale`
- **Language Switcher**: `LanguageSwitcher.vue` component

Locale files (en.json, zh.json) live in `~/MiroFish/locales/` (sibling to frontend/).

## API Integration Patterns

### Axios Instance (`api/index.js`)
- Base URL: `VITE_API_BASE_URL` env var or `http://localhost:5001`
- Timeout: 5 minutes (long-running operations)
- Request interceptor: injects `Accept-Language` header
- Response interceptor: validates `success` flag, throws on error
- Exponential backoff retry: `requestWithRetry(fn, maxRetries=3, delay=1000)`

### API Modules
- **`api/graph.js`**: `generateOntology`, `buildGraph`, `getTaskStatus`, `getGraphData`, `getProject`
- **`api/simulation.js`**: Full lifecycle -- create, prepare, start/stop, profiles, posts, timeline, agents, interview agents, history
- **`api/report.js`**: `generateReport`, `getReportStatus`, `getAgentLog`, `getConsoleLog`, `getReport`, `chatWithReport`

### Pattern
```js
// All API calls use axios instance with interceptors
import service from './index'
export const someAction = (data) => service.post('/api/path', data)

// Long-running operations use retry
import { requestWithRetry } from './index'
export const longRunning = (data) => requestWithRetry(() => service.post('/api/path', data), 3, 1000)
```

## Component Descriptions

| Component | Purpose |
|-----------|---------|
| `GraphPanel` | D3.js knowledge graph visualization with interactive nodes/edges |
| `HistoryDatabase` | Browse/search past simulations with project details |
| `LanguageSwitcher` | Toggle between zh/en locales |
| `Step1GraphBuild` | Upload documents + define simulation requirements → generate ontology |
| `Step2EnvSetup` | Configure entity types, agent profiles, platform settings (Twitter/Reddit) |
| `Step3Simulation` | Monitor running simulation with real-time updates |
| `Step4Report` | Generate and view analysis reports with agent logs |
| `Step5Interaction` | Chat with simulation agents post-run |

## Key Design Notes

- **SPA with dynamic routing** -- no page reloads, all state in memory/localStorage
- **Process workflow**: Home → Process (5 steps) → Simulation/Report/Interaction views
- **Real-time updates**: Polling-based status APIs for simulation runs and report generation
- **Modular API layer**: Separate files for graph, simulation, report domains
- **D3 visualization**: GraphPanel handles knowledge graph rendering
