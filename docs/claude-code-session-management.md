# Claude Code Session Management for Benchmarks

Practical guide for running clean, isolated, reproducible Claude Code benchmark trials.

## 1. Fresh Session (No Memory/Context)

Each `claude -p` invocation starts a brand-new session by default — no conversation history carries over. To be extra safe:

```bash
# Prevent session from being saved to disk at all
claude -p --no-session-persistence "your prompt here"

# Or use an explicit unique session ID to guarantee isolation
claude -p --session-id "$(uuidgen)" "your prompt here"
```

**Key insight:** `-p` (print mode) already starts fresh. There's no shared state between invocations unless you explicitly use `-c` (continue) or `-r` (resume).

## 2. CLI Flags for Session Management

| Flag | Purpose |
|------|---------|
| `--session-id <uuid>` | Use a specific session UUID (ensures unique identity) |
| `--no-session-persistence` | Don't save session to disk (can't be resumed) |
| `-c, --continue` | Continue most recent conversation (AVOID for benchmarks) |
| `-r, --resume <id>` | Resume a specific session (AVOID for benchmarks) |
| `--fork-session` | Fork when resuming (creates new ID) |

## 3. Non-Interactive Execution

```bash
# Basic non-interactive run
claude -p "Implement a function that reverses a linked list"

# Pipe input
cat problem.md | claude -p "Solve this problem"

# Structured JSON output
claude -p --output-format json "your prompt"

# Streaming JSON (for real-time monitoring)
claude -p --output-format stream-json "your prompt"
```

The `-p` / `--print` flag is essential — it runs non-interactively, prints the response, and exits.

## 4. Capturing Cost/Token Usage

```bash
# JSON output includes usage metadata
claude -p --output-format json "your prompt" > result.json

# Stream JSON gives per-message token counts
claude -p --output-format stream-json "your prompt" > stream.jsonl
```

The JSON output format includes token usage in the response metadata. Parse `result.json` for `input_tokens`, `output_tokens`, and cost info.

For stream-json, look for `result` message type at end of stream which contains cumulative usage.

## 5. Setting Working Directory

```bash
# Simply cd before running
cd /tmp/benchmark-trial-001 && claude -p "your prompt"

# Or use a subshell for isolation
(cd /tmp/clean-workspace && claude -p "your prompt")

# Create a fresh temp dir per trial
TRIAL_DIR=$(mktemp -d)
cp -r ./problem-files/* "$TRIAL_DIR/"
(cd "$TRIAL_DIR" && claude -p "solve this")
```

Claude Code uses the current working directory as its project root. There's no `--cwd` flag for the main command (only for `claude agents`).

## 6. Disabling MCP Tools and Custom Instructions

### Disable CLAUDE.md auto-discovery + MCP + hooks + plugins:

```bash
# --bare mode: skips hooks, plugins, CLAUDE.md auto-discovery, MCP, auto-memory
claude -p --bare "your prompt"
```

`--bare` is the nuclear option — it sets `CLAUDE_CODE_SIMPLE=1` and disables:
- CLAUDE.md auto-discovery
- Hooks
- LSP
- Plugin sync
- Auto-memory
- Background prefetches
- Keychain reads

### Alternatively, for more granular control:

```bash
# Skip all customizations (CLAUDE.md, skills, plugins, hooks, MCP, custom agents)
claude -p --safe-mode "your prompt"

# Restrict to specific tools only
claude -p --tools "Bash,Edit,Read,Write" "your prompt"

# Disable all tools
claude -p --tools "" "your prompt"

# Use strict MCP config (ignore all other MCP configs, provide empty one)
echo '{}' > /tmp/empty-mcp.json
claude -p --strict-mcp-config --mcp-config /tmp/empty-mcp.json "your prompt"

# Disable skills/slash-commands
claude -p --disable-slash-commands "your prompt"
```

### Prevent CLAUDE.md from being read:

Run from a directory with no `CLAUDE.md`, no `.claude/` folder, and use `--bare` to skip `~/.claude/CLAUDE.md`.

## 7. Environment Variables

| Variable | Effect |
|----------|--------|
| `ANTHROPIC_API_KEY` | API key for authentication |
| `ANTHROPIC_MODEL` | Override default model |
| `CLAUDE_CODE_SIMPLE=1` | Same as --bare (minimal mode) |
| `CLAUDE_CODE_SAFE_MODE=1` | Same as --safe-mode |
| `CLAUDE_CODE_MAX_TURNS` | Limit agentic turns (see §8) |
| `CLAUDE_CODE_USE_BEDROCK=1` | Use AWS Bedrock |
| `CLAUDE_CODE_USE_VERTEX=1` | Use Google Vertex |
| `AWS_REGION` / `AWS_PROFILE` | Bedrock config |
| `DISABLE_PROMPT_CACHING=1` | Disable prompt caching |
| `CLAUDE_CODE_SKIP_OOBE=1` | Skip first-run experience |

## 8. Max Turns / Timeout Controls

```bash
# Limit number of agentic turns (agent loops)
CLAUDE_CODE_MAX_TURNS=20 claude -p "your prompt"

# Use --max-turns flag if available (check your version)
claude -p --max-turns 10 "your prompt"

# External timeout with GNU timeout
timeout 300 claude -p "your prompt"

# Effort level controls how much thinking/work Claude does
claude -p --effort low "your prompt"    # minimal
claude -p --effort high "your prompt"   # thorough
claude -p --effort max "your prompt"    # maximum
```

## 9. Exit Status

```bash
claude -p "your prompt"
echo $?  # 0 = success, non-zero = error

# In a script:
if claude -p --output-format json "your prompt" > result.json 2> error.log; then
    echo "SUCCESS"
else
    echo "FAILED with exit code $?"
fi
```

Exit codes:
- `0` — completed successfully
- Non-zero — error (auth failure, timeout, API error, etc.)

## Complete Benchmark Runner Template

```bash
#!/usr/bin/env bash
set -euo pipefail

PROMPT="$1"
TRIAL_DIR=$(mktemp -d)
RESULTS_DIR="./results/$(date +%Y%m%d-%H%M%S)"
mkdir -p "$RESULTS_DIR"

# Copy problem files if needed
# cp -r ./problems/current/* "$TRIAL_DIR/"

# Run isolated trial
START_TIME=$(date +%s%N)

cd "$TRIAL_DIR" && \
  CLAUDE_CODE_MAX_TURNS=30 \
  timeout 600 \
  claude -p \
    --bare \
    --no-session-persistence \
    --output-format json \
    --model sonnet \
    --permission-mode bypassPermissions \
    --tools "Bash,Edit,Read,Write" \
    "$PROMPT" \
  > "$RESULTS_DIR/output.json" 2> "$RESULTS_DIR/stderr.log"

EXIT_CODE=$?
END_TIME=$(date +%s%N)
DURATION_MS=$(( (END_TIME - START_TIME) / 1000000 ))

# Record metadata
cat > "$RESULTS_DIR/meta.json" <<EOF
{
  "exit_code": $EXIT_CODE,
  "duration_ms": $DURATION_MS,
  "trial_dir": "$TRIAL_DIR",
  "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
}
EOF

echo "Trial complete: exit=$EXIT_CODE, duration=${DURATION_MS}ms"
echo "Results: $RESULTS_DIR"

# Cleanup
rm -rf "$TRIAL_DIR"
```

## Key Flags Summary for Clean Benchmarks

```bash
claude -p \
  --bare \                        # No CLAUDE.md, hooks, plugins, MCP
  --no-session-persistence \      # Don't save session
  --output-format json \          # Structured output with usage stats
  --permission-mode bypassPermissions \  # No permission prompts (sandboxed only!)
  --model sonnet \                # Explicit model
  --tools "Bash,Edit,Read,Write" \  # Explicit tool allowlist
  "your prompt"
```

⚠️ **`--permission-mode bypassPermissions`** should ONLY be used in sandboxed environments with no internet access. For safer runs, use `--dangerously-skip-permissions` or `--permission-mode auto`.
