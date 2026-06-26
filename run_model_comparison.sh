#!/bin/bash
set -euo pipefail

# Model comparison benchmark
# Runs gf-url-shortener-hard with multiple models on both tools

SCENARIO="gf-url-shortener-hard"
SCENARIO_DIR="$(pwd)/scenarios/$SCENARIO"
RESULTS_FILE="$(pwd)/runs/model-comparison-$(date +%Y%m%d-%H%M).json"

# Models to test
# Claude Code uses Bedrock model IDs, Kiro uses short names
declare -A CC_MODELS=(
  ["sonnet-4.6"]="global.anthropic.claude-sonnet-4-6"
  ["opus-4.8"]="global.anthropic.claude-opus-4-8"
  ["haiku-4.5"]="us.anthropic.claude-haiku-4-5-20251001-v1:0"
)

declare -A KIRO_MODELS=(
  ["sonnet-4.6"]="claude-sonnet-4.6"
  ["opus-4.8"]="claude-opus-4.8"
  ["haiku-4.5"]="claude-haiku-4.5"
)

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

echo "[]" > "$RESULTS_FILE"

run_claude_code() {
  local model_name="$1"
  local model_id="$2"
  local trial_dir="$(pwd)/runs/cc-${model_name}-${SCENARIO}/trial-1"

  echo ""
  echo "========================================"
  echo "  Claude Code | Model: $model_name"
  echo "  Model ID: $model_id"
  echo "========================================"

  rm -rf "$trial_dir"
  mkdir -p "$trial_dir/src"
  cp "$SCENARIO_DIR/SPEC.md" "$trial_dir/"
  cp -r "$SCENARIO_DIR/tests" "$trial_dir/"
  rm -rf "$trial_dir/tests/__pycache__"
  touch "$trial_dir/src/__init__.py"

  cd "$trial_dir"
  
  CLAUDE_CODE_USE_BEDROCK=1 \
  CLAUDE_CODE_DISABLE_THINKING=1 \
  CLAUDE_CODE_MAX_TURNS=50 \
  claude -p \
    --bare \
    --no-session-persistence \
    --output-format json \
    --permission-mode bypassPermissions \
    --model "$model_id" \
    "$PROMPT" > "$trial_dir/result.json" 2>"$trial_dir/stderr.log" || true

  # Parse and display
  python3 -c "
import json, sys
try:
    d = json.load(open('$trial_dir/result.json'))
    cost = d.get('total_cost_usd', 0)
    turns = d.get('num_turns', 0)
    duration = d.get('duration_ms', 0) / 1000
    inp = d.get('usage', {}).get('input_tokens', 0)
    out = d.get('usage', {}).get('output_tokens', 0)
    print(f'  Cost: \${cost:.4f}')
    print(f'  Turns: {turns}')
    print(f'  Duration: {duration:.1f}s')
    print(f'  Input tokens: {inp}')
    print(f'  Output tokens: {out}')
except Exception as e:
    print(f'  ERROR parsing results: {e}', file=sys.stderr)
" 2>&1

  # Verify tests
  echo "  Tests:"
  cd "$trial_dir" && PYTHONPATH=. pytest tests/ -q 2>&1 | tail -3 | sed 's/^/    /'
}

run_kiro() {
  local model_name="$1"
  local model_id="$2"
  local trial_dir="$(pwd)/runs/kiro-${model_name}-${SCENARIO}/trial-1"

  echo ""
  echo "========================================"
  echo "  Kiro CLI | Model: $model_name"
  echo "  Model ID: $model_id"
  echo "========================================"

  rm -rf "$trial_dir"
  mkdir -p "$trial_dir/src"
  cp "$SCENARIO_DIR/SPEC.md" "$trial_dir/"
  cp -r "$SCENARIO_DIR/tests" "$trial_dir/"
  rm -rf "$trial_dir/tests/__pycache__"
  touch "$trial_dir/src/__init__.py"

  cd "$trial_dir"
  
  START_TIME=$(date +%s)
  kiro-cli chat \
    --no-interactive \
    -a \
    --model "$model_id" \
    --effort high \
    "$PROMPT" > "$trial_dir/output.txt" 2>"$trial_dir/stderr.log" || true
  END_TIME=$(date +%s)
  DURATION=$((END_TIME - START_TIME))

  # Extract credits from output
  CREDITS=$(grep -oP "Credits: \K[0-9.]+" "$trial_dir/output.txt" 2>/dev/null | tail -1 || echo "unknown")
  echo "  Duration: ${DURATION}s"
  echo "  Credits: $CREDITS"
  if [ "$CREDITS" != "unknown" ]; then
    echo "  Cost (@\$0.02/credit): \$(echo "$CREDITS * 0.02" | bc)"
  fi

  # Verify tests
  echo "  Tests:"
  cd "$trial_dir" && PYTHONPATH=. pytest tests/ -q 2>&1 | tail -3 | sed 's/^/    /'
}

echo "=== CostToShip Model Comparison ==="
echo "Scenario: $SCENARIO (71 tests)"
echo "Date: $(date -Iseconds)"
echo ""

# Run all models
for model_name in "sonnet-4.6" "opus-4.8" "haiku-4.5"; do
  run_claude_code "$model_name" "${CC_MODELS[$model_name]}"
  cd "$(dirname "$RESULTS_FILE")"/../
  
  run_kiro "$model_name" "${KIRO_MODELS[$model_name]}"
  cd "$(dirname "$RESULTS_FILE")"/../
done

echo ""
echo "=== ALL RUNS COMPLETE ==="
