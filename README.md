# CostToShip — AI Coding Tools Benchmark

**The true cost of AI-generated code — measured by what works, not what runs.**

An independent benchmark comparing AI coding tools on **cost per successful task**.

🔗 **[Live Dashboard](https://d3om46wvracj6h.cloudfront.net/costtoship/index.html)** — Interactive results with charts

## Headline Result

| Model | Claude Code | Kiro CLI | Ratio |
|-------|------------|----------|:---:|
| Sonnet 4 | $0.3373 | $0.0468 | **7.2×** |
| Sonnet 4.6 | $0.2214 | $0.0396 | **5.6×** |
| Opus 4.8 | $0.3426 | $0.0968 | **3.5×** |
| Haiku 4.5 | $0.1061 | $0.0136 | **7.8×** |

> All models pass 71/71 tests on both tools. The cost ratio holds (3.5×–7.8×) regardless of model choice.

## Quick Start

```bash
# Run a single trial
./run_benchmark.sh claude-code gf-url-shortener-hard 1
./run_benchmark.sh kiro-cli gf-url-shortener-hard 1

# Run model comparison across all models
./run_model_comparison.sh

# Run N=5 trials
for i in {1..5}; do ./run_benchmark.sh claude-code gf-url-shortener-hard $i; done
for i in {1..5}; do ./run_benchmark.sh kiro-cli gf-url-shortener-hard $i; done
```

## Scenarios

| Scenario | Type | Tests | Difficulty | Description |
|----------|------|-------|-----------|-------------|
| `gf-url-shortener` | Greenfield | 19 | Easy | Single-file URL shortener |
| `gf-url-shortener-hard` | Greenfield | 71 | Medium | Multi-file URL shortener with analytics, rate limiting, expiration |

## Tools Under Test

| Tool | Models Tested | Settings |
|------|--------------|----------|
| Claude Code CLI | Sonnet 4, Sonnet 4.6, Opus 4.8, Haiku 4.5 | `--bare --no-session-persistence --permission-mode bypassPermissions` |
| Kiro CLI Pro | Sonnet 4, Sonnet 4.6, Opus 4.8, Haiku 4.5 | `--no-interactive -a --effort high` |

## Key Findings

1. **Cost ratio holds across all models** — Kiro is consistently 3.5×–7.8× cheaper
2. **Cheaper models = bigger ratio** — Haiku 7.8×, Sonnet 5.6×, Opus 3.5×
3. **Kiro credit multipliers matter** — Opus at 2.2× credits narrows the gap
4. **All models pass first try** — scenario is too easy to differentiate quality
5. **Opus uses fewer turns** (11 vs 20–32) but costs more per token

## Methodology

- **Same model:** Both tools use the same Claude model per trial — differences measure harness efficiency
- **Fresh session:** Each trial starts with zero context, verbatim prompt
- **Automated scoring:** pytest test suite (binary pass/fail, 71 tests)
- **Version pinned:** Tool versions and model versions recorded
- **Cost normalized:** Claude Code via Bedrock pay-per-use, Kiro via credits @ $0.02/credit (Pro subscription)

## Project Structure

```
costtoship/
├── README.md
├── run_benchmark.sh          # Single-trial runner
├── run_model_comparison.sh   # Multi-model comparison runner
├── scenarios/                # Benchmark scenarios (spec + tests)
│   ├── gf-url-shortener/
│   └── gf-url-shortener-hard/
├── runs/                     # Trial outputs (gitignored)
├── docs/                     # Results & methodology docs
│   └── results.md
└── dashboard/
    └── index.html            # Dashboard (deployed to CloudFront)
```

## Links

- 📊 [Live Dashboard](https://d3om46wvracj6h.cloudfront.net/costtoship/index.html)
- 📄 [Detailed Results](docs/results.md)

## License

MIT

## Author

Independent benchmark by Gili · Not affiliated with any vendor
