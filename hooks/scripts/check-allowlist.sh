#!/usr/bin/env bash
set -euo pipefail

INPUT=$(cat)

# Extract fields safely using jq
AGENT=$(echo "$INPUT" | jq -r '.session.agent // empty')
TOOL=$(echo "$INPUT" | jq -r '.data.tool_name // empty')
CMD=$(echo "$INPUT" | jq -r '.data.arguments.command // .data.arguments.CommandLine // .data.arguments.cmd // empty')

# Default agent if unspecified
AGENT="${AGENT:-ruth}"

block_action() {
  local reason="$1"
  echo "{\"action\": \"block\", \"reason\": \"$reason\"}"
  exit 0
}

allow_action() {
  echo '{"action": "allow"}'
  exit 0
}

# If tool is not shell/bash, verify agent-level tool restrictions
if [[ "$TOOL" != "bash" && "$TOOL" != "shell" && -n "$TOOL" ]]; then
  case "$AGENT" in
    codebase-scout)
      if [[ "$TOOL" != "read_file" && "$TOOL" != "read" && "$TOOL" != "grep" ]]; then
        block_action "codebase-scout is restricted to read-only inspection (read, grep)"
      fi
      ;;
    qmd-scout)
      if [[ "$TOOL" != "read_file" && "$TOOL" != "read" && "$TOOL" != "grep" && "$TOOL" != "skill" ]]; then
        block_action "qmd-scout is restricted to read, grep, skill, and qmd shell"
      fi
      ;;
    sfl-docs-ideational-judge|sfl-docs-interpersonal-judge|sfl-docs-textual-judge)
      if [[ "$TOOL" != "read_file" && "$TOOL" != "read" && "$TOOL" != "grep" ]]; then
        block_action "metafunction judges are strictly read-only (read, grep)"
      fi
      ;;
    sfl-docs-drafter)
      if [[ "$TOOL" != "read_file" && "$TOOL" != "read" && "$TOOL" != "grep" && "$TOOL" != "write_file" && "$TOOL" != "write" ]]; then
        block_action "sfl-docs-drafter can write new files but cannot edit existing files or run shell"
      fi
      ;;
    sfl-docs-editor)
      if [[ "$TOOL" != "read_file" && "$TOOL" != "read" && "$TOOL" != "grep" && "$TOOL" != "write_file" && "$TOOL" != "write" && "$TOOL" != "edit" ]]; then
        block_action "sfl-docs-editor is restricted to write, edit, and read/grep"
      fi
      ;;
  esac
  allow_action
fi

# Shell command allowlist enforcement
if [[ "$TOOL" == "bash" || "$TOOL" == "shell" || -n "$CMD" ]]; then
  CMD_TRIMMED="$(echo "$CMD" | sed -e 's/^[[:space:]]*//')"

  case "$AGENT" in
    ruth)
      if [[ "$CMD_TRIMMED" =~ ^plannotator[[:space:]]+annotate ]]; then
        allow_action
      else
        block_action "ruth shell execution is restricted to plannotator annotate"
      fi
      ;;

    codebase-scout)
      if [[ "$CMD_TRIMMED" =~ ^git[[:space:]]+(log|diff|show|blame|status|rev-parse|ls-files|grep|shortlog|describe|branch|tag|remote)([[:space:]]|$) ]] || \
         [[ "$CMD_TRIMMED" =~ ^(ls|fd|wc|head|tail|cat|stat|file)([[:space:]]|$) ]]; then
        allow_action
      else
        block_action "codebase-scout shell execution is restricted to read-only git and file inspection"
      fi
      ;;

    qmd-scout)
      if [[ "$CMD_TRIMMED" =~ ^qmd([[:space:]]|$) ]] || \
         [[ "$CMD_TRIMMED" =~ ^env[[:space:]]+-u[[:space:]]+CI[[:space:]]+qmd([[:space:]]|$) ]]; then
        allow_action
      else
        block_action "qmd-scout shell execution is restricted to qmd CLI commands"
      fi
      ;;

    sfl-docs-workflow)
      if [[ "$CMD_TRIMMED" =~ ^(qmd|git|ls|cat|head|tail)([[:space:]]|$) ]] || \
         [[ "$CMD_TRIMMED" =~ ^env[[:space:]]+-u[[:space:]]+CI[[:space:]]+qmd([[:space:]]|$) ]]; then
        allow_action
      else
        block_action "sfl-docs-workflow shell execution is restricted to allowlisted commands"
      fi
      ;;

    *)
      block_action "$AGENT has no shell execution permission"
      ;;
  esac
fi

allow_action
