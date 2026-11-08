#!/usr/bin/env bash
set -euo pipefail

# ==============================================================================
# install-opencode.sh — Integrate R.U.T.H. with OpenCode
# ==============================================================================
# Automates:
#   1. Global OpenCode configuration (~/.config/opencode/)
#      - Mounts R.U.T.H. skills directory in opencode.jsonc
#      - Installs ruth-guardrails.js plugin (enforcing check-allowlist.sh)
#      - Generates OpenCode agent profiles for ruth and all 8 subagents
#   2. Project-level export (--project <dir>)
#      - Exports AGENTS.md and opencode.json into target repository
#   3. Diagnostic verification (--check)
#   4. Clean removal (--uninstall)
# ==============================================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
OPENCODE_CONFIG_DIR="${HOME}/.config/opencode"
OPENCODE_AGENTS_DIR="${OPENCODE_CONFIG_DIR}/agents"
OPENCODE_PLUGINS_DIR="${OPENCODE_CONFIG_DIR}/plugins"
OPENCODE_JSONC="${OPENCODE_CONFIG_DIR}/opencode.jsonc"

COLOR_GREEN="\033[0;32m"
COLOR_BLUE="\033[0;34m"
COLOR_YELLOW="\033[0;33m"
COLOR_RED="\033[0;31m"
COLOR_RESET="\033[0m"

log_info()    { echo -e "${COLOR_BLUE}==>${COLOR_RESET} $*"; }
log_success() { echo -e "${COLOR_GREEN}✓${COLOR_RESET} $*"; }
log_warn()    { echo -e "${COLOR_YELLOW}!${COLOR_RESET} $*"; }
log_error()   { echo -e "${COLOR_RED}✗${COLOR_RESET} $*"; }

usage() {
  cat << EOF
Usage: $(basename "$0") [options]

Integrate R.U.T.H. (OpenGAP) with OpenCode.

Options:
  -g, --global          Install globally into ~/.config/opencode (default)
  -p, --project <dir>   Export R.U.T.H into a specific project workspace
  -c, --check           Verify OpenCode installation, plugins, skills, and agents
  -u, --uninstall       Remove global R.U.T.H configuration from ~/.config/opencode
  -h, --help            Show this help message

Examples:
  $(basename "$0")                    # Global installation
  $(basename "$0") --check            # Check status
  $(basename "$0") -p /path/to/repo   # Export into project workspace
  $(basename "$0") --uninstall        # Remove global integration
EOF
  exit 0
}

check_dependencies() {
  if ! command -v opencode >/dev/null 2>&1; then
    log_warn "OpenCode CLI is not in PATH."
    log_info "Install with: npm install -g opencode  or  brew install sst/tap/opencode"
  else
    log_success "Found OpenCode CLI: $(command -v opencode) ($(opencode --version 2>/dev/null || true))"
  fi
}

install_plugin() {
  mkdir -p "${OPENCODE_PLUGINS_DIR}"
  local target_plugin="${OPENCODE_PLUGINS_DIR}/ruth-guardrails.js"
  local allowlist_script="${REPO_DIR}/hooks/scripts/check-allowlist.sh"

  log_info "Installing OpenCode plugin: ${target_plugin}..."

  cat << EOF > "${target_plugin}"
// R.U.T.H. OpenCode Guardrails Plugin
// Enforces tool allowlists and human-in-the-loop boundaries
import { spawnSync } from "node:child_process";

const ALLOWLIST_SCRIPT = "${allowlist_script}";

function checkCommand(command, agent) {
  const payload = {
    event: "pre_tool_use",
    timestamp: new Date().toISOString(),
    data: {
      tool_name: "bash",
      arguments: { command: command || "" },
    },
    session: {
      agent: agent || "ruth",
    },
  };

  const res = spawnSync(ALLOWLIST_SCRIPT, [], {
    input: JSON.stringify(payload),
    encoding: "utf-8",
  });

  if (res.stdout) {
    try {
      const parsed = JSON.parse(res.stdout);
      if (parsed.action === "block") {
        throw new Error(\`[R.U.T.H Guardrail Blocked]: \${parsed.reason}\`);
      }
    } catch (e) {
      if (e.message && e.message.startsWith("[R.U.T.H Guardrail")) {
        throw e;
      }
    }
  }
}

export default {
  id: "ruth-guardrails",

  // OpenCode 2 runtime
  async setup(ctx) {
    await ctx.tool.hook("execute.before", (event) => {
      if ((event.tool === "shell" || event.tool === "bash") && typeof event.input?.command === "string") {
        checkCommand(event.input.command, event.agent);
      }
    });
  },

  // OpenCode 1 fallback
  async server() {
    return {
      "tool.execute.before": async (input, output) => {
        if ((input.tool === "bash" || input.tool === "shell") && typeof output?.args?.command === "string") {
          checkCommand(output.args.command, input.agent);
        }
      },
    };
  },
};
EOF

  log_success "Plugin installed: ruth-guardrails"
}

update_opencode_skills() {
  local skills_path="${REPO_DIR}/skills"
  mkdir -p "${OPENCODE_CONFIG_DIR}"

  if [[ ! -f "${OPENCODE_JSONC}" ]]; then
    log_info "Creating ${OPENCODE_JSONC}..."
    cat << EOF > "${OPENCODE_JSONC}"
{
  "\$schema": "https://opencode.ai/config.json",
  "skills": [
    "${skills_path}"
  ]
}
EOF
    log_success "Initialized ${OPENCODE_JSONC} with skills path"
    return
  fi

  # Update existing opencode.jsonc using python
  log_info "Registering skills path in ${OPENCODE_JSONC}..."
  python3 - << PYEOF
import re
import sys
import shutil

path = "${OPENCODE_JSONC}"
skill_entry = "${skills_path}"

with open(path, "r", encoding="utf-8") as f:
    content = f.read()

if skill_entry in content:
    print("  Skills path already registered in opencode.jsonc")
    sys.exit(0)

# Create backup
shutil.copy2(path, path + ".bak")

# If skills array exists, insert entry
if re.search(r'"skills"\s*:\s*\[', content):
    content = re.sub(
        r'("skills"\s*:\s*\[)',
        r'\1\n    "' + skill_entry + '",',
        content,
        count=1
    )
else:
    # Insert skills section after opening brace
    content = re.sub(
        r'(\{)',
        r'\1\n  "skills": [\n    "' + skill_entry + '"\n  ],',
        content,
        count=1
    )

with open(path, "w", encoding="utf-8") as f:
    f.write(content)

print("  Successfully added skills path to opencode.jsonc")
PYEOF
  log_success "Updated skills configuration"
}

generate_agent_profiles() {
  mkdir -p "${OPENCODE_AGENTS_DIR}"
  log_info "Generating OpenCode agent profiles in ${OPENCODE_AGENTS_DIR}..."

  # 1. Main Ruth Agent
  cat << EOF > "${OPENCODE_AGENTS_DIR}/ruth.md"
---
description: Documentation-crafting agent in the R.U.T.H persona voice (Records Uncertainty, Traces History): writes and revises READMEs, API references, changelogs, postmortems, and architecture notes with terminology accountability, bounded uncertainty labels, and confessed euphemisms.
mode: primary
permission:
  read: allow
  grep: allow
  glob: allow
  write: ask
  edit: ask
  bash: ask
---

$(cat "${REPO_DIR}/SOUL.md")

$(cat "${REPO_DIR}/RULES.md")
EOF
  log_success "Generated agent profile: ruth.md"

  # Subagent definitions: name | description | permissions (yaml block)
  declare -A AGENT_PERMS=(
    ["codebase-scout"]="  \"*\": deny\n  read: allow\n  grep: allow\n  glob: allow\n  bash: allow"
    ["qmd-scout"]="  \"*\": deny\n  read: allow\n  grep: allow\n  skill: allow\n  bash: allow"
    ["sfl-docs-drafter"]="  \"*\": deny\n  read: allow\n  grep: allow\n  write: allow"
    ["sfl-docs-editor"]="  \"*\": deny\n  read: allow\n  grep: allow\n  write: allow\n  edit: allow"
    ["sfl-docs-ideational-judge"]="  \"*\": deny\n  read: allow\n  grep: allow"
    ["sfl-docs-interpersonal-judge"]="  \"*\": deny\n  read: allow\n  grep: allow"
    ["sfl-docs-textual-judge"]="  \"*\": deny\n  read: allow\n  grep: allow"
    ["sfl-docs-workflow"]="  \"*\": deny\n  read: allow\n  grep: allow\n  write: allow\n  edit: allow\n  bash: allow\n  skill: allow"
  )

  for agent in codebase-scout qmd-scout sfl-docs-drafter sfl-docs-editor sfl-docs-ideational-judge sfl-docs-interpersonal-judge sfl-docs-textual-judge sfl-docs-workflow; do
    local desc
    desc=$(python3 -c "import yaml; print(yaml.safe_load(open('${REPO_DIR}/agents/${agent}/agent.yaml'))['description'])")
    local perms="${AGENT_PERMS[$agent]}"
    local soul_content
    soul_content=$(cat "${REPO_DIR}/agents/${agent}/SOUL.md")

    cat << EOF > "${OPENCODE_AGENTS_DIR}/${agent}.md"
---
description: ${desc}
mode: subagent
permission:
$(echo -e "${perms}")
---

${soul_content}
EOF
    log_success "Generated agent profile: ${agent}.md"
  done
}

export_to_project() {
  local target_dir="$1"
  mkdir -p "${target_dir}"
  log_info "Exporting R.U.T.H into project workspace: ${target_dir}..."

  if ! command -v opengap >/dev/null 2>&1; then
    log_error "opengap CLI not found. Required for export."
    exit 1
  fi

  (cd "${REPO_DIR}" && opengap export -f opencode) | python3 -c '
import sys

text = sys.stdin.read()
agents_part = ""
config_part = ""

if "# === AGENTS.md ===" in text:
    split1 = text.split("# === AGENTS.md ===")[1]
    if "# === opencode.json ===" in split1:
        agents_part, config_part = split1.split("# === opencode.json ===")
    else:
        agents_part = split1

with open("'"${target_dir}"'/AGENTS.md", "w", encoding="utf-8") as f:
    f.write(agents_part.strip() + "\n")

if config_part.strip():
    with open("'"${target_dir}"'/opencode.json", "w", encoding="utf-8") as f:
        f.write(config_part.strip() + "\n")
'

  log_success "Wrote ${target_dir}/AGENTS.md"
  log_success "Wrote ${target_dir}/opencode.json"
  log_info "You can now run 'opencode' in ${target_dir}"
}

verify_installation() {
  log_info "Verifying OpenCode integration status..."
  check_dependencies

  echo ""
  log_info "Checking OpenCode Plugins:"
  if command -v opencode >/dev/null 2>&1; then
    opencode plugin list || true
  fi

  echo ""
  log_info "Installed Agents in ${OPENCODE_AGENTS_DIR}:"
  if [[ -d "${OPENCODE_AGENTS_DIR}" ]]; then
    ls -1 "${OPENCODE_AGENTS_DIR}"/ruth*.md "${OPENCODE_AGENTS_DIR}"/sfl*.md "${OPENCODE_AGENTS_DIR}"/*scout*.md 2>/dev/null || echo "None found"
  else
    echo "Directory not found: ${OPENCODE_AGENTS_DIR}"
  fi

  echo ""
  log_info "Registered Skills in ${OPENCODE_JSONC}:"
  if [[ -f "${OPENCODE_JSONC}" ]]; then
    grep -n "${REPO_DIR}/skills" "${OPENCODE_JSONC}" || log_warn "R.U.T.H skills not found in ${OPENCODE_JSONC}"
  fi
}

uninstall_global() {
  log_info "Uninstalling R.U.T.H from global OpenCode configuration..."

  # Remove plugin
  rm -f "${OPENCODE_PLUGINS_DIR}/ruth-guardrails.js"
  log_success "Removed ${OPENCODE_PLUGINS_DIR}/ruth-guardrails.js"

  # Remove agents
  rm -f "${OPENCODE_AGENTS_DIR}/ruth.md" \
        "${OPENCODE_AGENTS_DIR}/codebase-scout.md" \
        "${OPENCODE_AGENTS_DIR}/qmd-scout.md" \
        "${OPENCODE_AGENTS_DIR}/sfl-docs-drafter.md" \
        "${OPENCODE_AGENTS_DIR}/sfl-docs-editor.md" \
        "${OPENCODE_AGENTS_DIR}/sfl-docs-ideational-judge.md" \
        "${OPENCODE_AGENTS_DIR}/sfl-docs-interpersonal-judge.md" \
        "${OPENCODE_AGENTS_DIR}/sfl-docs-textual-judge.md" \
        "${OPENCODE_AGENTS_DIR}/sfl-docs-workflow.md"
  log_success "Removed R.U.T.H agents from ${OPENCODE_AGENTS_DIR}"

  # Remove skill from opencode.jsonc
  if [[ -f "${OPENCODE_JSONC}" ]]; then
    python3 - << PYEOF
path = "${OPENCODE_JSONC}"
skill_entry = "${REPO_DIR}/skills"
with open(path, "r", encoding="utf-8") as f:
    lines = f.readlines()

filtered = [line for line in lines if skill_entry not in line]

with open(path, "w", encoding="utf-8") as f:
    f.writelines(filtered)
PYEOF
    log_success "Removed skills entry from ${OPENCODE_JSONC}"
  fi

  log_success "Uninstallation complete."
}

# ------------------------------------------------------------------------------
# Main Dispatch
# ------------------------------------------------------------------------------

ACTION="global"
TARGET_PROJECT=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    -g|--global)
      ACTION="global"
      shift
      ;;
    -p|--project)
      ACTION="project"
      TARGET_PROJECT="${2:-}"
      if [[ -z "$TARGET_PROJECT" ]]; then
        log_error "Option --project requires a directory argument."
        exit 1
      fi
      shift 2
      ;;
    -c|--check)
      ACTION="check"
      shift
      ;;
    -u|--uninstall)
      ACTION="uninstall"
      shift
      ;;
    -h|--help)
      usage
      ;;
    *)
      log_error "Unknown option: $1"
      usage
      ;;
  esac
done

case "$ACTION" in
  global)
    check_dependencies
    update_opencode_skills
    install_plugin
    generate_agent_profiles
    echo ""
    log_success "R.U.T.H is now globally integrated with OpenCode!"
    echo "  - Run interactive session:  opencode run --agent ruth"
    echo "  - In OpenCode TUI:          Select agent 'ruth' or invoke '@codebase-scout', etc."
    echo "  - Via OpenGAP runner:       opengap run -d ${REPO_DIR} -a opencode"
    ;;
  project)
    export_to_project "$TARGET_PROJECT"
    ;;
  check)
    verify_installation
    ;;
  uninstall)
    uninstall_global
    ;;
esac
