# TypeScript Migration Assessment - MiroFish Frontend

## Current TypeScript Adoption Status

| Metric | Value |
|--------|-------|
| tsconfig.json | ❌ Not present |
| TypeScript files (.ts) | 0 |
| JavaScript files (.js) | 9 |
| Vue files (.vue) | 16 |
| Vue files with `<script lang="ts">` | 0 |
| **Total lines of code** | ~20,859 |

### Project Dependencies (from package.json)

```json
{
  "vue": "^3.5.24",
  "vue-router": "^4.6.3",
  "vue-i18n": "^11.3.0",
  "axios": "^1.14.0",
  "d3": "^7.9.0"
}
```

### Build Tool
- Vite 7.2.4 with @vitejs/plugin-vue 6.0.1

---

## Migration Effort Estimate: **MEDIUM**

### Effort Breakdown

| Category | Assessment | Notes |
|----------|------------|-------|
| Infrastructure setup | Low | Vite supports TypeScript via @vitejs/plugin-vue |
| Type definitions | Medium | Need to define interfaces for API responses, Vue props, router params |
| API layer (500 LOC) | Medium | 5 files - axios service, simulation, report, graph, pendingUpload store |
| Router (52 LOC) | Low | Simple routes with typed params |
| Store (33 LOC) | Low | Simple reactive state |
| Components (15,253 LOC) | Medium-High | 8 components + App.vue, complex business logic |
| Views (6,106 LOC) | Medium-High | 6 views with substantial logic |

### Complexity Factors

**Favorable:**
- Clean Vue 3 Composition API usage with `<script setup>`
- Good JSDoc annotations already present
- Well-structured API layer with consistent patterns
- Small team-friendly codebase size

**Challenging:**
- No gradual typing path - full migration required
- D3.js has complex typing requirements
- No existing type definitions for API contracts
- Large Vue components with complex prop drilling

---

## Recommended Migration Steps

### Phase 1: Infrastructure Setup (Day 1)
1. Install TypeScript and type dependencies:
   ```bash
   npm install -D typescript @types/node @types/d3 @vitejs/plugin-vue
   ```

2. Create `tsconfig.json`:
   ```json
   {
     "compilerOptions": {
       "target": "ESNext",
       "useDefineForClassFields": true,
       "module": "ESNext",
       "lib": ["ESNext", "DOM", "DOM.Iterable"],
       "skipLibCheck": true,
       "moduleResolution": "bundler",
       "allowImportingTsExtensions": true,
       "resolveJsonModule": true,
       "isolatedModules": true,
       "noEmit": true,
       "jsx": "preserve",
       "strict": true,
       "noUnusedLocals": false,
       "noUnusedParameters": false,
       "noFallthroughCasesInSwitch": true,
       "paths": {
         "@/*": ["./src/*"]
       }
     },
     "include": ["src/**/*.ts", "src/**/*.d.ts", "src/**/*.tsx", "src/**/*.vue"],
     "references": [{ "path": "./tsconfig.node.json" }]
   }
   ```

3. Rename files incrementally: `.js` → `.ts`, `.vue` with `<script lang="ts">`

### Phase 2: Type Definitions (Day 1-2)
Create `src/types/` directory with:

```
src/types/
├── api/
│   ├── simulation.d.ts
│   ├── graph.d.ts
│   ├── report.d.ts
│   └── index.d.ts
├── components.d.ts
└── router.d.ts
```

**Priority type definitions:**
1. API response types (Simulation, Graph, Report, Project)
2. Vue component prop types
3. Router param types

### Phase 3: API Layer Migration (Day 2-3)
**Priority: HIGH** - Core data contracts

1. `src/api/index.ts` - Axios service with typed interceptors
2. `src/api/simulation.ts` - 23 API functions
3. `src/api/graph.ts`, `src/api/report.ts`
4. `src/store/pendingUpload.ts`

### Phase 4: Router & Store (Day 3)
1. `src/router/index.ts` - Typed route params
2. `src/i18n/index.ts` - If using typed i18n

### Phase 5: Components & Views (Day 3-5)
**Priority: MEDIUM** - Work from leaves inward

Order:
1. `src/components/LanguageSwitcher.vue` (smallest)
2. `src/components/GraphPanel.vue`
3. `src/components/HistoryDatabase.vue`
4. `src/views/Home.vue`
5. `src/App.vue`
6. Step components (Step1-5)
7. Complex views (SimulationView, Process, etc.)

---

## Priority Files to Migrate First

### Tier 1 - Critical (Foundation)
| File | LOC | Reason |
|------|-----|--------|
| `src/api/index.js` | 69 | Axios instance - all API calls |
| `src/api/simulation.js` | 187 | Largest API module |
| `src/types/api/index.d.ts` | - | Shared type definitions |

### Tier 2 - High Value
| File | LOC | Reason |
|------|-----|--------|
| `src/store/pendingUpload.js` | 33 | Simple state - good starter |
| `src/router/index.js` | 52 | Route typing prevents bugs |
| `src/components/LanguageSwitcher.vue` | 124 | Small, isolated |

### Tier 3 - Medium Effort
| File | LOC | Reason |
|------|-----|--------|
| `src/views/Home.vue` | ~600 | Entry point |
| `src/components/Step1GraphBuild.vue` | 700 | Moderate complexity |
| `src/components/GraphPanel.vue` | 1423 | Heavy D3 usage |

### Tier 4 - Complex (Migrate Last)
| File | LOC | Reason |
|------|-----|--------|
| `src/components/Step4Report.vue` | 5162 | Largest file |
| `src/components/Step5Interaction.vue` | 2584 | Complex interactions |
| `src/components/Step3Simulation.vue` | 1266 | Real-time updates |
| `src/views/SimulationRunView.vue` | 452 | WebSocket-like patterns |

---

## Estimated Timeline

| Phase | Duration | Effort |
|-------|----------|--------|
| Phase 1: Infrastructure | 0.5 day | Low |
| Phase 2: Type Definitions | 1 day | Medium |
| Phase 3: API Layer | 1 day | Medium |
| Phase 4: Router & Store | 0.5 day | Low |
| Phase 5: Components & Views | 2-3 days | Medium-High |
| **Total** | **5-6 days** | **Medium** |

---

## Migration Strategy Notes

1. **Incremental conversion**: Rename `.js` → `.ts` one file at a time
2. **Strict mode off initially**: Enable `strict: false` initially, tighten later
3. **Vue SFC**: Add `<script lang="ts">` to Vue files progressively
4. **Type-first approach**: Define interfaces before implementing logic
5. **IDE support**: Use VSCode with Volar extension for Vue TypeScript support
6. **Keep tests updated**: If adding tests, use Vitest with TypeScript

---

## External Type Dependencies Needed

```bash
npm install -D @types/node @types/d3
```

For Vue library types, ensure `vite-env.d.ts` includes:
```typescript
/// <reference types="vite/client" />

declare module '*.vue' {
  import type { DefineComponent } from 'vue'
  const component: DefineComponent<{}, {}, any>
  export default component
}
```
