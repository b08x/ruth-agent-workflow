#!/usr/bin/env bash
set -euo pipefail

# Plannotator HTIL Review Gate
# Wraps plannotator annotate with --gate, --json, --require-approval
# Graceful degradation: if plannotator is not installed, exit with escalation outcome

FILE="${1:-}"
RESULT_FILE="${2:-}"

if [ -z "$FILE" ]; then
  echo '{"error": "No file specified for review gate"}' >&2
  exit 2
fi

if ! command -v plannotator >/dev/null 2>&1; then
  echo "WARNING: plannotator CLI is not installed. Escalating to human." >&2
  if [ -n "$RESULT_FILE" ]; then
    echo '{"decision": "escalate", "reason": "plannotator CLI not found; human review required"}' > "$RESULT_FILE"
  fi
  echo '{"decision": "escalate", "status": "cli_missing", "file": "'"$FILE"'"}'
  exit 1
fi

CMD=(plannotator annotate "$FILE" --gate --json --require-approval)
if [ -n "$RESULT_FILE" ]; then
  CMD+=(--result-file "$RESULT_FILE")
fi

exec "${CMD[@]}"
