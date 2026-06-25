#!/bin/bash
set -euo pipefail

# CostToShip Benchmark Runner
# Usage: ./run_benchmark.sh <tool> <scenario> [trial_number]
# Example: ./run_benchmark.sh claude-code gf-url-shortener-hard 1

TOOL="${1:?Usage: $0 <claude-code|kiro-cli> <scenario> [trial_number]}"
SCENARIO="${2:?Usage: $0 <tool> <scenario> [trial_number]}"
TRIAL="${3:-1}"

SCENARIO_DIR="$(pwd)/scenarios/$SCENARIO"
TRIAL_DIR="$(pwd)/runs/${TOOL}-${SCENARIO}/trial-${TRIAL}"

if [ ! -d "$SCENARIO_DIR" ]; then
  echo "ERROR: Scenario not found: $SCENARIO_DIR"
  exit 1
fi

echo "=== CostToShip Benchmark ==="
echo "Tool:     $TOOL"
echo "Scenario: $SCENARIO"
echo "Trial:    $TRIAL"
echo "=========================="

# Prepare clean trial directory
rm -rf "$TRIAL_DIR"
mkdir -p "$TRIAL_DIR/src"
cp "$SCENARIO_DIR/SPEC.md" "$TRIAL_DIR/"
cp -r "$SCENARIO_DIR/tests" "$TRIAL_DIR/"
rm -rf "$TRIAL_DIR/tests/__pycache__"
touch "$TRIAL_DIR/src/__init__.py"

# Build the prompt
PROMPT="You are given a specification (SPEC.md) and a test suite (tests/).

Your task: implement all Python modules under src/ that satisfy the requirements in SPEC.md and pass all tests.

The project structure must be:
src/__init__.py (already exists)
src/models.py
src/storage.py
src/validation.py
src/shortener.py
src/analytics.py
src/rate_limiter.py
src/expiration.py

Run 'PYTHONPATH=. pytest tests/ -v' to verify your implementation passes. Keep iterating until ALL tests are green. When done, confirm all tests pass."

START_TIME=$(date +%s)

case "$TOOL" in
  claude-code)
    echo "Running Claude Code (Bedrock, Sonnet 4)..."
    cd "$TRIAL_DIR" && \
    CLAUDE_CODE_USE_BEDROCK=1 \
    CLAUDE_CODE_DISABLE_THINKING=1 \
    CLAUDE_CODE_MAX_TURNS=50 \
    claude -p \
      --bare \
      --no-session-persistence \
      --output-format json \
      --permission-mode bypassPermissions \
      --model us.anthropic.claude-sonnet-4-20250514-v1:0 \
      "$PROMPT" > "$TRIAL_DIR/result.json" 2>"$TRIAL_DIR/stderr.log"
    
    EXIT_CODE=$?
    END_TIME=$(date +%s)
    DURATION=$((END_TIME - START_TIME))
    
    # Parse results
    python3 -c "
import json
d = json.load(open('$TRIAL_DIR/result.json'))
print(f'Success: {not d.get(\"is_error\", False)}')
print(f'Turns: {d[\"num_turns\"]}')
print(f'Duration: {d[\"duration_ms\"]/1000:.1f}s')
print(f'Cost: \${d[\"total_cost_usd\"]:.4f}')
print(f'Input tokens: {d[\"usage\"][\"input_tokens\"]}')
print(f'Output tokens: {d[\"usage\"][\"output_tokens\"]}')
print(f'Cache read: {d[\"usage\"][\"cache_read_input_tokens\"]}')
print(f'Cache create: {d[\"usage\"][\"cache_creation_input_tokens\"]}')
"
    ;;
    
  kiro-cli)
    echo "Running Kiro CLI (Sonnet 4)..."
    cd "$TRIAL_DIR" && \
    kiro-cli chat \
      --no-interactive \
      -a \
      --model claude-sonnet-4 \
      --effort high \
      "$PROMPT" > "$TRIAL_DIR/output.txt" 2>"$TRIAL_DIR/stderr.log"
    
    EXIT_CODE=$?
    END_TIME=$(date +%s)
    DURATION=$((END_TIME - START_TIME))
    
    # Parse credits from output
    CREDITS=$(grep -oP "Credits: \K[0-9.]+" "$TRIAL_DIR/stderr.log" 2>/dev/null || echo "unknown")
    echo "Duration: ${DURATION}s"
    echo "Credits: $CREDITS"
    echo "Cost (@\$0.02/credit): \$$(echo "$CREDITS * 0.02" | bc 2>/dev/null || echo 'N/A')"
    ;;
    
  *)
    echo "ERROR: Unknown tool: $TOOL (use claude-code or kiro-cli)"
    exit 1
    ;;
esac

# Verify tests pass
echo ""
echo "=== Verifying Tests ==="
cd "$TRIAL_DIR" && PYTHONPATH=. pytest tests/ -q 2>&1 | tail -5

echo ""
echo "=== Trial Complete ==="
echo "Results in: $TRIAL_DIR"
