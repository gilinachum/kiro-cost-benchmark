# CostToShip — AI Coding Tools Benchmark

**The true cost of AI-generated code — measured by what works, not what runs.**

An independent benchmark comparing AI coding tools on **cost per successful task**.

## Quick Start

```bash
# Run a single trial
./run_benchmark.sh claude-code gf-url-shortener-hard 1
./run_benchmark.sh kiro-cli gf-url-shortener-hard 1

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

| Tool | Model | Settings |
|------|-------|----------|
| Claude Code CLI | Sonnet 4 (Bedrock) | `--bare --no-session-persistence --permission-mode bypassPermissions` |
| Kiro CLI | Sonnet 4 | `--no-interactive -a --effort high` |

## Results (Preliminary)

### GF-URL-Shortener-Hard (71 tests, 7 modules)

| Metric | Claude Code | Kiro CLI |
|--------|-------------|----------|
| Success | ✅ 71/71 | ✅ 71/71 |
| Cost | $0.3373 | $0.0468 (2.34 credits) |
| Time | 113.5s | 110.9s |
| Cost ratio | 1x | **7.2x cheaper** |

> Note: Both tools passed first try. Need harder scenarios to measure cost-per-success (where retries matter).

## Methodology

- **Repeated trials:** Each scenario runs N=5 per tool
- **Automated scoring:** pytest test suite (binary pass/fail)
- **Fresh session:** Each trial starts with zero context
- **Version pinned:** Tool versions and model versions recorded
- **Cost normalized:** Claude Code via Bedrock pay-per-use, Kiro via credits @ $0.02/credit

## Project Structure

```
costtoship/
├── README.md
├── run_benchmark.sh          # Main runner script
├── scenarios/                # Benchmark scenarios (spec + tests + reference)
│   ├── gf-url-shortener/
│   └── gf-url-shortener-hard/
├── runs/                     # Trial outputs (gitignored)
├── docs/                     # Research & methodology docs
└── index.html                # Results visualization (SPA)
```

## License

MIT

## Author

Independent benchmark by Gili · Not affiliated with any vendor
