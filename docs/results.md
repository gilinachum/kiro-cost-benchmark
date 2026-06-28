# Benchmark Results

## Model Comparison — gf-url-shortener-hard (71 tests)

**Date:** 2026-06-26
**Scenario:** Multi-file URL shortener (7 modules, 71 pytest tests)
**Result:** All models pass 71/71 on both tools

| Model | Claude Code Cost | CC Turns | CC Time | Kiro Credits | Kiro Cost (@$0.02) | Kiro Time | CC/Kiro Ratio |
|-------|-----------------|----------|---------|--------------|-------------------|-----------|:---:|
| Sonnet 4.6 | $0.2214 | 20 | 80.5s | 1.98 | $0.0396 | 77s | 5.6× |
| Opus 4.8 | $0.3426 | 11 | 71.0s | 4.84 | $0.0968 | 128s | 3.5× |
| Haiku 4.5 | $0.1061 | 26 | 74.9s | 0.68 | $0.0136 | 56s | 7.8× |

### Key Findings

1. **Cost ratio holds across all models** — Kiro is consistently 3.5×–7.8× cheaper
2. **Cheaper models = bigger ratio** — Haiku 7.8×, Sonnet 5.6×, Opus 3.5×
3. **Kiro credit multipliers matter** — Opus at 2.2× credits narrows the gap vs Haiku at 0.4×
4. **All models pass first try** — scenario is too easy to differentiate quality
5. **Opus uses fewer turns** (11 vs 20-32) but costs more per token

### Credit Multipliers (Kiro Pro)

| Model | Credits/Unit |
|-------|:---:|
| Haiku 4.5 | 0.40× |
| Sonnet 4 / 4.5 / 4.6 | 1.30× |
| Opus 4.5 / 4.6 / 4.7 / 4.8 | 2.20× |
| DeepSeek 3.2 | 0.25× |

### Notes

- Claude Code: `CLAUDE_CODE_DISABLE_THINKING=1` (Bedrock extended thinking bug)
- Claude Code: `--permission-mode bypassPermissions --bare --no-session-persistence`
- Kiro CLI: `--no-interactive -a --effort high`
- N=1 per model (statistical significance requires N=5)
- All costs are at Kiro Pro subscription rate ($0.02/credit)

## Easy Scenario — gf-url-shortener (19 tests)

| Tool | Model | Cost | Time | Result |
|------|-------|------|------|--------|
| Claude Code | Sonnet 4 | $0.0619 | 28s | 19/19 ✅ |
| Kiro CLI | Sonnet 4 | 0.62 cr ($0.0124) | 35.6s | 19/19 ✅ |
