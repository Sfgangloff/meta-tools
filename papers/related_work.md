# Related Work — meta-tools

Notes from a literature scan on 2026-05-04. Compares our `meta-tools`
project against existing self-evolving agent / tool-creation frameworks,
with special attention to mathematical reasoning.

## Anchor reference

- **A Survey of Self-Evolving Agents** (Gao, Geng, Hua et al., TMLR 2026)
  arXiv: 2507.21046 — saved as `papers/2507.21046.pdf`
  GitHub: https://github.com/CharlesQ9/Self-Evolving-Agents

The survey organizes the field along four axes: **What / When / How / Where to evolve**.
Our project lives in:
- **What:** Tool → Creation (Phases 1–4) and Tool → Selection (Phase 5)
- **When:** Inter-test-time (tools persist across sessions)
- **How:** Reward-based / textual feedback (the trajectory itself is the signal)
- **Where:** Currently general; future domain-specific variants possible

## General-purpose tool-creation frameworks (direct lineage)

| Framework | What it does | Relation to meta-tools |
|---|---|---|
| **Voyager** (Wang et al., 2023) | Minecraft agent with growing skill library of executable code, iterative prompting + self-verification | Canonical ancestor — same idea: agent extends its own skill set over time |
| **CREATOR** (Qian et al., EMNLP 2023) | Code-as-tool creation; disentangles abstract reasoning from concrete tool use | Closest to Phases 1+2 (`analyze_trajectory` + `develop_tool`) |
| **CRAFT** (Yuan et al., ICLR 2024) | Creates AND retrieves from specialized toolsets via multi-view matching | Closest to Phase 5 — registry + retrieval split is already there |
| **Alita / SkillWeaver / ATLASS** | Various tool-creation systems referenced in survey Fig. 2 | Same paradigm, different emphases |

## Math-reasoning analogues

| Framework | What it does | Notes |
|---|---|---|
| **LEGO-Prover** | Builds a library of lemmas discovered during proof attempts; reuses them in later proofs | The closest math analogue. Reports +13.4% on CoqHammer when extracted lemmas are added to the prover's library. "Lemma" is the math equivalent of our generated tool. |
| **LADDER** (Simonds & Yoshiyama, 2025) | RL-based intra-test-time self-evolution for math reasoning | In survey taxonomy under Intra-test-time / RL |
| **Agent0** (Nov 2025) | Self-evolving via tool-integrated reasoning; Curriculum Agent + Executor Agent | +18% math, +24% general on Qwen3-8B-Base. Co-evolution pattern; less about tool creation, more about task generation. |
| **ARTIST** | Couples agentic reasoning, RL, tool integration | +22% over base on hardest math tasks |
| **ToRA / MathCoder / MuMath-Code / Llemma** | Tool *use* (calculators, CAS, theorem provers) for math | Use a fixed toolset; not tool creation |

## Where meta-tools is positioned

Differentiation from closest comparators:

1. **vs. Voyager / CREATOR / CRAFT** — those are research systems with bespoke
   runtimes. Ours is an MCP server, so it plugs into a real coding agent
   (Claude Code) and extends a real working toolset live.

2. **vs. LEGO-Prover** — they extract lemmas during proof search; we extract
   tools during arbitrary reasoning trajectories. The closest math-mode
   adaptation would be: trajectory = proof attempt log, generated tool =
   a Lean/Coq tactic or lemma.

3. **vs. Agent0 / ARTIST** — those are RL training pipelines that update model
   weights. Ours is inference-time, no weight updates. Complementary, not
   competing.

## Idea for a future phase (math variant)

If we want to apply meta-tools to math reasoning, **LEGO-Prover is the
reference architecture**, but our system is more general because the "tool"
is arbitrary Python rather than a lemma in a specific proof assistant.

A natural Phase 6+ would be: domain-specific generators (a math variant that
emits Lean tactics, a data variant that emits SQL templates, etc.) sharing
the same registry / shelf machinery from Phases 1–5.

## Source links

- [Survey: Self-Evolving Agents (arXiv 2507.21046)](https://arxiv.org/abs/2507.21046)
- [EvoAgentX — Awesome Self-Evolving Agents](https://github.com/EvoAgentX/Awesome-Self-Evolving-Agents)
- [CRAFT (arXiv 2309.17428)](https://arxiv.org/abs/2309.17428)
- [CREATOR (ACL Anthology)](https://aclanthology.org/2023.findings-emnlp.462.pdf)
- [Voyager (OpenReview)](https://openreview.net/forum?id=ehfRiF0R3a)
- [Agent0 (arXiv 2511.16043)](https://arxiv.org/html/2511.16043v1)
- [ARTIST (arXiv 2505.01441)](https://arxiv.org/abs/2505.01441)
- [Llemma (arXiv 2310.10631)](https://arxiv.org/abs/2310.10631)
- [LLM-Based Theorem Provers overview (incl. LEGO-Prover)](https://www.emergentmind.com/topics/llm-based-theorem-provers)
