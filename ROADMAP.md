# MiroFish ROADMAP (GSD Methodology)

**Last Updated:** 2026-04-02
**Status:** Planning Phase Complete, Executing M1

---

## Milestone 1: Foundation (Weeks 1-2)
**Goal:** Fork sync, dev environment, Docker hardening

- [ ] Fork sync with upstream 666ghj/MiroFish
- [ ] Dev environment setup & verification (`npm run setup:all`)
- [ ] Dependency audit & security updates
- [ ] Docker configuration hardening
- [ ] Backend starts at localhost:5001
- [ ] Frontend builds and loads at localhost:3000

---

## Milestone 2: Core Enhancement (Weeks 3-5)
**Goal:** Improve simulation engine, memory, and reporting

- [ ] GraphRAG pipeline improvements
- [ ] Agent memory system upgrades (Zep Cloud integration)
- [ ] ReportAgent toolset expansion
- [ ] Simulation parameter tuning
- [ ] OASIS engine integration review

---

## Milestone 3: UX/Frontend (Weeks 6-8)
**Goal:** Refactor Vue frontend, add real-time features

- [ ] Vue component refactoring
- [ ] TypeScript migration assessment
- [ ] Real-time simulation dashboard
- [ ] Agent interaction interface
- [ ] Report visualization improvements

---

## Milestone 4: Production Hardening (Weeks 9-10)
**Goal:** Security, performance, CI/CD

- [ ] API rate limiting & security hardening
- [ ] Performance profiling (Python & Vue)
- [ ] CI/CD setup (GitHub Actions)
- [ ] Monitoring & logging integration
- [ ] Load testing with 100+ agents

---

## GSD Workflow

### Phase Commands Used
```bash
/gsd:new-project  # Initialize
/gsd:map-codebase  # Analyze existing code
/gsd:discuss-phase # Capture preferences
/gsd:plan-phase    # Create atomic tasks
/gsd:execute-phase # Run in waves
/gsd:verify-work   # UAT testing
/gsd:ship          # Release
```

### Wave Execution
- **Wave 1:** Foundation (parallel)
- **Wave 2:** Backend Core (parallel)
- **Wave 3:** Frontend Core (parallel)

---

## Decisions Log

| Date | Question | Decision |
|------|----------|----------|
| 2026-04-02 | Fork sync vs new features | Sync first, then enhance |
| 2026-04-02 | Memory backend | Continue with Zep Cloud |
| 2026-04-02 | Simulation scale | Target 100+ agents |
| 2026-04-02 | Frontend framework | Vue + TypeScript assessment |
| 2026-04-02 | API strategy | REST only (v1) |
| 2026-04-02 | Deployment target | Self-hosted + Docker |

---

## File Structure Reference
```
~/.hermes/mirofish-planning/
├── STATE.md              # Current state tracking
├── PLAN.md               # Atomic task list (XML format)
└── IMPLEMENTATION_PLAN.md # This plan
```
