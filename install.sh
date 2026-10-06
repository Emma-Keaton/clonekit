#!/usr/bin/env bash
# clonekit one-command installer.
#
# Links (or copies) the skill tree into every agent you point it at, and
# writes an AGENTS.md router. Run it from the project you want to install
# into; the clonekit checkout can live anywhere.
#
#   ./install.sh                      detect agents in the current directory
#   ./install.sh --agent claude,cursor force these agents
#   ./install.sh --global             also install to home-directory targets
#   ./install.sh --copy               copy instead of symlink
#   ./install.sh --dry-run            show what would happen
set -euo pipefail

REPO="$(cd -P "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILLS_SRC="$REPO/.agents/skills"
DEST="$(pwd -P)"
BEGIN='<!-- clonekit:begin -->'
END='<!-- clonekit:end -->'

MODE=link
DRY=0
GLOBAL=0
AGENTS=""

usage() {
  cat <<'EOF'
clonekit installer. Usage: ./install.sh [options]

  --agent <list>   comma-separated agents to install for, instead of auto-detect
                   (claude, opencode, cursor, cline, qwen, gemini, agentsmd)
  --global         also install into home-directory targets where supported
  --copy           copy skill folders instead of symlinking
  --dry-run        print the plan, change nothing
  -h, --help       this help

Auto-detect looks in the current directory for .claude/, .opencode/,
.cursor/, .clinerules/, QWEN.md, .qwen/, GEMINI.md, .gemini/, AGENTS.md.
Skill-capable agents (claude, opencode) get linked skill folders; rules-based
agents (cursor, cline, qwen, gemini) get a pointer block; every target gets
the AGENTS.md router. Re-running is idempotent; existing files are backed up
to *.bak before a block is added, never otherwise modified.
EOF
}

while [ $# -gt 0 ]; do
  case "$1" in
    --agent) AGENTS="${2:-}"; shift 2 ;;
    --agent=*) AGENTS="${1#*=}"; shift ;;
    --global) GLOBAL=1; shift ;;
    --copy) MODE=copy; shift ;;
    --dry-run) DRY=1; shift ;;
    -h|--help) usage; exit 0 ;;
    *) echo "install: unknown option '$1' (try --help)" >&2; exit 2 ;;
  esac
done

# symlink support probe (some Windows setups refuse symlinks)
CAN_LINK=0
probe_dir="$(mktemp -d)"
if ln -s "$SKILLS_SRC" "$probe_dir/probe" 2>/dev/null && [ -L "$probe_dir/probe" ]; then
  CAN_LINK=1
fi
rm -rf "$probe_dir"
if [ "$MODE" = link ] && [ "$CAN_LINK" -eq 0 ]; then
  echo "install: symlinks not supported here, falling back to copies."
  MODE=copy
fi

say() { printf '%s\n' "$*"; }
would() { if [ "$DRY" -eq 1 ]; then say "DRY: $*"; fi; }

install_skills() {
  # $1 = destination skills dir
  local dest="$1" s name target
  would "link skills into $dest"
  [ "$DRY" -eq 1 ] && return 0
  mkdir -p "$dest"
  for s in "$SKILLS_SRC"/*; do
    [ -d "$s" ] || continue
    name="$(basename "$s")"
    target="$dest/$name"
    if [ "$MODE" = link ]; then
      if [ -L "$target" ] && [ "$(readlink "$target")" = "$s" ]; then
        continue
      fi
      rm -rf "$target"
      ln -s "$s" "$target"
    else
      rm -rf "$target"
      cp -R "$s" "$target"
    fi
    say "  $MODE  $target"
  done
}

block_body() {
  cat <<EOF
# clonekit

Installed from: $REPO

For any clone, rebuild or reverse-engineering request, and for "where are
we" / "what's next" on a clone project: read
$REPO/.agents/skills/clonekit/SKILL.md and follow it. It routes to the other
skills in $REPO/.agents/skills/, and keeps clonekit/status.json in the user's
project. Skills are self-contained: read any SKILL.md directly if your
environment does not load skill folders. Tools run from the project root:
$REPO/bin/replica <command> (or python3 <skill>/<tool>.py).
EOF
}

update_block() {
  # $1 = file to (back up and) write the clonekit block into
  local file="$1" tmp
  would "update block in $file"
  [ "$DRY" -eq 1 ] && return 0
  mkdir -p "$(dirname "$file")"
  if [ -f "$file" ] && ! grep -qF "$BEGIN" "$file"; then
    cp "$file" "$file.bak"
    say "  backup $file.bak"
  fi
  tmp="$file.tmp.$$"
  if [ -f "$file" ]; then
    sed "/^$BEGIN\$/,/^$END\$/d" "$file" > "$tmp"
  else
    : > "$tmp"
  fi
  {
    printf '%s\n' "$BEGIN"
    block_body
    printf '%s\n' "$END"
  } >> "$tmp"
  mv "$tmp" "$file"
  say "  block $file"
}

install_agentsmd() {
  local file="$DEST/AGENTS.md"
  if [ -f "$file" ] && ! grep -qF "$BEGIN" "$file" && \
     grep -qF ".agents/skills/clonekit/SKILL.md" "$file"; then
    say "  AGENTS.md already routes clonekit, left untouched"
    return 0
  fi
  if [ ! -f "$file" ] && [ "$DEST" = "$REPO" ]; then
    would "copy AGENTS.md to $file"
    if [ "$DRY" -eq 0 ]; then
      cp "$REPO/AGENTS.md" "$file"
      say "  write $file"
    fi
    return 0
  fi
  update_block "$file"
}

want() {
  # $1 = agent name; true if requested explicitly or auto-detected
  case ",$AGENTS," in
    *",$1,"*) return 0 ;;
  esac
  [ -n "$AGENTS" ] && return 1
  return 0
}

detected_any=0
note_detect() { detected_any=1; }

extra=""
if [ "$DRY" -eq 1 ]; then extra=" (dry-run)"; fi
say "clonekit install  (source: $REPO)"
say "target: $DEST   mode: $MODE$extra"

if want claude && { [ -z "$AGENTS" ] && [ -d "$DEST/.claude" ] || [ -n "$AGENTS" ]; }; then
  note_detect
  say "claude: skills -> $DEST/.claude/skills"
  install_skills "$DEST/.claude/skills"
  if [ "$GLOBAL" -eq 1 ]; then
    say "claude (global): skills -> $HOME/.claude/skills"
    install_skills "$HOME/.claude/skills"
  fi
fi

if want opencode && { [ -z "$AGENTS" ] && [ -d "$DEST/.opencode" ] || [ -n "$AGENTS" ]; }; then
  note_detect
  say "opencode: skills -> $DEST/.opencode/skills"
  install_skills "$DEST/.opencode/skills"
  if [ "$GLOBAL" -eq 1 ]; then
    say "opencode (global): skills -> $HOME/.config/opencode/skills"
    install_skills "$HOME/.config/opencode/skills"
  fi
fi

if want cursor && { [ -z "$AGENTS" ] && [ -d "$DEST/.cursor" ] || [ -n "$AGENTS" ]; }; then
  note_detect
  say "cursor: pointer -> $DEST/.cursor/rules/clonekit.mdc"
  if [ "$DRY" -eq 0 ]; then
    mkdir -p "$DEST/.cursor/rules"
    if [ ! -f "$DEST/.cursor/rules/clonekit.mdc" ]; then
      printf -- '---\ndescription: clonekit skill routing\n---\n%s\n%s\n' \
        "$BEGIN" "$END" > "$DEST/.cursor/rules/clonekit.mdc"
    fi
  fi
  update_block "$DEST/.cursor/rules/clonekit.mdc"
fi

if want cline && { [ -z "$AGENTS" ] && [ -e "$DEST/.clinerules" ] || [ -n "$AGENTS" ]; }; then
  note_detect
  say "cline: pointer -> $DEST/.clinerules/clonekit.md"
  update_block "$DEST/.clinerules/clonekit.md"
fi

if want qwen && { [ -z "$AGENTS" ] && { [ -f "$DEST/QWEN.md" ] || [ -d "$DEST/.qwen" ]; } || [ -n "$AGENTS" ]; }; then
  note_detect
  say "qwen: pointer -> $DEST/QWEN.md"
  update_block "$DEST/QWEN.md"
fi

if want gemini && { [ -z "$AGENTS" ] && { [ -f "$DEST/GEMINI.md" ] || [ -d "$DEST/.gemini" ]; } || [ -n "$AGENTS" ]; }; then
  note_detect
  say "gemini: pointer -> $DEST/GEMINI.md"
  update_block "$DEST/GEMINI.md"
  if [ "$GLOBAL" -eq 1 ]; then
    say "gemini (global): pointer -> $HOME/.gemini/GEMINI.md"
    update_block "$HOME/.gemini/GEMINI.md"
  fi
fi

install_agentsmd

if [ "$detected_any" -eq 0 ] && [ -z "$AGENTS" ]; then
  say ""
  say "No agent directories detected here. The skills are ready under"
  say "$SKILLS_SRC and the AGENTS.md router is in place. Force an agent with:"
  say "  ./install.sh --agent claude,cursor,cline,qwen,gemini,opencode"
fi

say ""
say "Done. Every agent now routes clone requests through"
say ".agents/skills/clonekit/SKILL.md. Verify with: ./bin/replica doctor"
