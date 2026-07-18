# Memory Wiki Plugin: Compiled Knowledge Vault for OpenClaw

**Source**: OpenClaw docs (plugins/memory-wiki.md)
**Date**: 2026-07-19

## Why It Matters

The memory-wiki plugin is a **bundled (included in core) plugin** that compiles durable knowledge into a navigable wiki: deterministic pages, structured claims with evidence, provenance, dashboards, and machine-readable digests.

It addresses a gap our workspace has been feeling — our exploration notes, experiments, and memory files are all flat markdown, searchable via `memory_search`, but lacking structured claims, provenance tracking, stale detection, and dashboard visibility.

## Architecture

```
Memory-wiki sits beside active memory (not replacing it):

Active Memory Plugin  ──► Recall, semantic search, promotion, dreaming
Memory Wiki Plugin   ──► Compiled wiki pages, provenance-rich syntheses,
                         dashboards, wiki_search/wiki_get/wiki_apply
```

Memory layer separation:
| Layer | Owns |
|-------|------|
| Active memory plugin | Recall, semantic search, promotion, dreaming, memory runtime |
| memory-wiki | Compiled wiki pages, provenance-rich syntheses, dashboards, wiki search/get/apply |

## Three Vault Modes

### 1. Isolated (default)
Self-contained curated knowledge store. No dependency on any active memory plugin. Best for a standalone wiki.

### 2. Bridge
Reads public memory artifacts and event logs from the active memory plugin through public plugin SDK seams. Compiles what the active memory plugin exports without reaching into internals.

Can index:
- Exported memory artifacts (`indexMemoryRoot`)
- Daily notes (`indexDailyNotes`)
- Dream reports (`indexDreamReports`)
- Memory event logs (`followMemoryEvents`)

### 3. Unsafe-local
Escape hatch for same-machine local private paths. Experimental and non-portable.

## Vault Layout

```
<vault>/
  AGENTS.md
  WIKI.md
  index.md
  inbox.md
  entities/          ← People, systems, projects, objects
  concepts/          ← Ideas, abstractions, patterns, policies
  syntheses/         ← Compiled summaries and maintained rollups
  sources/           ← Imported raw material
  reports/           ← Generated dashboards
  _attachments/
  _views/
  .openclaw-wiki/    ← Cache (agent-digest.json, claims.jsonl)
```

Managed content stays inside generated blocks; human note blocks preserved.

## Structured Claims

Claims are first-class frontmatter, not freeform text:

```yaml
claims:
  - id: claim.ev0.pattern
    text: "Ev0 (mu=0.22, sigma=0.04) is the most stable Lenia pattern at R=20"
    status: supported
    confidence: 0.95
    evidence:
      - kind: experiment
        sourceId: experiments/lenia_jax.py
        weight: 0.8
        confidence: 0.95
```

Each claim can have status (supported/contested/refuted), confidence, and structured evidence with source id, path, lines, weight, privacy tier.

## Agent Tools

| Tool | Purpose |
|------|---------|
| `wiki_status` | Vault mode, health, Obsidian CLI availability |
| `wiki_search` | Search wiki pages with mode params (person, route, evidence, claim) |
| `wiki_get` | Read a wiki page by id/path |
| `wiki_apply` | Narrow synthesis/metadata mutations without freeform surgery |
| `wiki_lint` | Structural checks, provenance gaps, contradictions |

Search modes:
- `auto` — balanced default
- `find-person` — person-like entities, aliases, handles
- `route-question` — agent cards, ask-for hints
- `source-evidence` — source pages and evidence metadata
- `raw-claim` — matching structured claims

## Dashboards (auto-generated)

When `render.createDashboards: true`, compile maintains:

| Report | Tracks |
|--------|--------|
| `reports/open-questions.md` | Unresolved questions |
| `reports/contradictions.md` | Contradiction note clusters |
| `reports/low-confidence.md` | Low-confidence pages/claims |
| `reports/claim-health.md` | Claims missing structured evidence |
| `reports/stale-pages.md` | Stale or unknown freshness |
| `reports/person-agent-directory.md` | Person/entity routing cards |
| `reports/relationship-graph.md` | Structured relationship edges |
| `reports/provenance-coverage.md` | Evidence class coverage |
| `reports/privacy-review.md` | Non-public privacy tiers |

## Applicability to Our Workspace

Our workspace at D:\openclaw_workspace has:
- 122 exploration notes (diverse topics: Lenia, Neural CA, Agent frameworks, complex systems)
- 131 experiment files (Python code, results)
- 98 memory files (daily logs, structured memory)

### What Would Improve

1. **Entity pages** — Our experiments could have wiki entity pages:
   - `entity.lenia` → page for our Lenia work with claims, evidence sources, experiment links
   - `entity.emergence-lab` → page for the emergence-lab framework
   - `entity.neural-lenia` → Neural Lenia entity with experiment references

2. **Claims with provenance** — Convert flat observations into structured claims:
   - "Lenia R=20 sweet spot: 79.6% structure rate" → structured claim linked to experiment results
   - "Multi-channel Lenia > diversity" → claim with evidence from experiments/lenia_multichannel_jax.py
   - "Stochastic updates (p=0.5) enable survival" → claim with evidence link

3. **Dashboards** — Auto-generated health reports:
   - Stale pages: which exploration notes haven't been reviewed
   - Low confidence: which claims need more evidence
   - Contradictions: where different experiments disagree

4. **Synthesis pages** — Compiled summaries of related explorations, like:
   - "Google SOS analysis" → synthesis of multiple exploration notes
   - "Agent framework comparison" → synthesis of AgentSilex, cadCAD, OpenClaw

## Configuration for Our Setup

```json5
{
  plugins: {
    entries: {
      "memory-wiki": {
        enabled: true,
        config: {
          vaultMode: "bridge",
          vault: {
            path: "D:\\openclaw_workspace\\.wiki",
            renderMode: "native",
          },
          bridge: {
            enabled: true,
            readMemoryArtifacts: true,
            indexDailyNotes: true,
            indexMemoryRoot: true,
          },
          search: {
            backend: "shared",
            corpus: "all",
          },
          render: {
            createDashboards: true,
            createBacklinks: true,
          },
        },
      },
    },
  },
}
```

## Related Docs
- [Memory Overview](/concepts/memory)
- [Active Memory Plugin](/concepts/active-memory)
- [CLI: wiki](/cli/wiki)
- [CLI: memory](/cli/memory)
