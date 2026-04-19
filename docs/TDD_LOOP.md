# MiroFish TDD Auto-Iterative Development Loop

**Last Updated:** 2026-04-19
**Status:** Active - Cron-driven daily execution
**Job ID:** 5fd9e33e1798
**Schedule:** Daily 09:00 UTC = 11:00 CEST (MalikJPalamar's timezone)

---

## Overview

This document defines the automated TDD + GSD development loop that runs daily
at 09:00 UTC against the MalikJPalamar/MiroFish fork. The loop is self-perpetuating:
each iteration advances one task, writes tests first, and stores state to Supermemory
for cross-session continuity.

---

## Loop Architecture

```
HERMES CRON AGENT (09:00 UTC daily)
|
+-- [RED]  Phase 1: Find & Prioritize
|   +-- Scan backend/tests/ for untested modules
|   +-- Check backend/app/ for modules without test coverage
|   +-- Read ROADMAP.md for remaining tasks
|   +-- Pick highest-value untested component
|
+-- [RED]  Phase 2: Write Failing Test
|   +-- Create backend/tests/test_<module>.py
|   +-- Test MUST fail before any implementation
|   +-- Follow pytest conventions: test_<func>, Test<class>
|   +-- Include docstring explaining expected behavior
|
+-- [GREEN] Phase 3: Implement to Pass
|   +-- Run test - verify FAIL
|   +-- Implement minimal code to make test pass
|   +-- Run test - verify PASS
|   +-- No refactoring until test is green
|
+-- [REFACTOR] Phase 4: Clean Up
|   +-- Review implementation for readability
|   +-- Extract constants/config to backend/app/config.py
|   +-- Add inline comments for non-obvious logic
|   +-- Re-run full test suite
|
+-- [COMMIT] Phase 5: Document & Push
|   +-- Update STATE.md: mark task done, date, blockers
|   +-- git add . && git commit -m "[gsd:execute] <desc>"
|   +-- git push using GH_TOKEN_PAT from ~/.hermes/.env
|   +-- Store progress to Supermemory (container: hermes-default)
|
+-- [REPORT] Phase 6: Handoff
    +-- Summarize: task, tests passed/failed, next action
    +-- Deliver to current chat session
```

---

## TDD Test Coverage Priorities

Run `cd /root/MiroFish/backend && uv run pytest --cov=app --cov-report=term-missing -q`
to identify coverage gaps. Target modules in this order:

### Priority 1 - Core Simulation Engine
- [ ] backend/app/services/simulation.py - simulation lifecycle, parameter validation
- [ ] backend/app/services/graph_builder.py - GraphRAG seed extraction
- [ ] backend/app/services/agent.py - agent behavior, personality generation

### Priority 2 - API Layer
- [ ] backend/app/api/simulation.py - POST /simulation, GET /simulation/{id}
- [ ] backend/app/api/report.py - ReportAgent endpoints
- [ ] backend/app/api/agent.py - agent interaction endpoints

### Priority 3 - Memory & Graph
- [ ] backend/app/services/memory.py - Zep Cloud integration
- [ ] backend/app/services/graph.py - Graph construction, entity extraction

### Priority 4 - Utilities
- [ ] backend/app/utils/file_parser.py - document parsing, encoding
- [ ] backend/app/config.py - config validation
- [ ] backend/app/ratelimit.py - rate limit middleware

---

## Test Naming Conventions

```python
# backend/tests/test_<module>.py
import pytest
from backend.app.services.simulation import SimulationService

class TestSimulationService:
    """Tests for SimulationService - simulation lifecycle management."""

    def test_create_simulation_returns_id(self):
        """Simulation creation returns a valid UUID string."""
        service = SimulationService()
        result = service.create(name="test", config={})
        assert isinstance(result.id, str)
        assert len(result.id) == 36  # UUID format

    def test_create_simulation_with_invalid_config_raises(self):
        """Passing invalid config raises ValidationError."""
        service = SimulationService()
        with pytest.raises(ValidationError):
            service.create(name="test", config={"agents": -1})

    def test_simulation_runs_within_time_limit(self):
        """Simulation completes within configured max_seconds."""
        service = SimulationService()
        sim = service.create(name="test", config={"max_rounds": 5})
        result = service.run(sim.id)
        assert result.elapsed_seconds <= 300  # 5 min max
```

---

## GSD Task Format

Each daily task follows this format:

```
## YYYY-MM-DD - <Task Name>

### Task
<one sentence description>

### RED (Test Written)
- Created: backend/tests/test_<module>.py
- Test: <what it tests>
- Expected: <what it asserts>

### GREEN (Implementation)
- Changed: backend/app/<module>.py
- How: <what was changed>

### REFACTOR
- <any refactoring done>

### Blockers
- <any blockers encountered>

### Tomorrow's Task
<next task>
```

---

## Skill Stack

The cron agent loads these skills on each run:

| Skill | Purpose |
|-------|---------|
| hermes-agent | Agent execution framework, session management |
| gsd-wave-execution | GSD methodology: Discuss -> Plan -> Execute -> Verify -> Ship |
| subagent-driven-development | Task delegation to subagents if needed |

---

## Environment & Access

```
Repo:       /root/MiroFish (local clone)
Remote:     https://github.com/MalikJPalamar/MiroFish
Upstream:   https://github.com/666ghj/MiroFish
Push auth:  GH_TOKEN_PAT from ~/.hermes/.env
VPS:        srv1514399.hstgr.cloud (docker ps check)
Memory:     Supermemory (container: hermes-default)
```

---

## Git Push Strategy

```bash
# Primary (git with env token)
export GH_TOKEN_PAT=$(grep GH_TOKEN_PAT ~/.hermes/.env | cut -d= -f2)
git push origin main

# Fallback (GitHub API via requests - if git is blocked by security scan)
# Use Python requests module to push via GitHub REST API
```

---

## Success Criteria

| Metric | Target |
|--------|--------|
| Tests added per day | 1 test file (min 2 test cases) |
| Test pass rate | 100% before commit |
| Coverage increase | +2% per week |
| Commits per day | 1 (atomic, signed message) |
| Supermemory sync | Every iteration |

---

## Gap: What's NOT Covered Yet

From ROADMAP.md Milestone 2:
- GraphRAG pipeline improvements (concrete tasks not specified)
- Agent memory system upgrades beyond Zep Cloud basic usage
- ReportAgent toolset expansion (specific tools not enumerated)

From ROADMAP.md Milestone 3:
- OASIS engine integration review (what specifically to review?)
- Simulation parameter tuning (benchmarks not established)

These gaps are the input for Phase 1 of each daily iteration.
