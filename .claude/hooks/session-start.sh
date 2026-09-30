#!/bin/bash
# Installs the video-editing toolchain (ffmpeg, HyperFrames, headless Chrome,
# GSAP) so the video-editing skill can render in Claude Code on the web.
set -euo pipefail

if [ "${CLAUDE_CODE_REMOTE:-}" != "true" ]; then
  exit 0
fi

# ffmpeg / ffprobe — SFX synthesis, audio mixing, render verification.
if ! command -v ffmpeg >/dev/null 2>&1 || ! command -v ffprobe >/dev/null 2>&1; then
  apt-get update -qq >/dev/null 2>&1 || true
  DEBIAN_FRONTEND=noninteractive apt-get install -y -qq ffmpeg >/dev/null
fi

# HyperFrames CLI — the rendering engine.
if ! command -v hyperframes >/dev/null 2>&1; then
  npm install -g hyperframes >/dev/null 2>&1
fi

# Chrome Headless Shell used by `hyperframes render` (cached after first run).
hyperframes browser ensure </dev/null >/dev/null 2>&1

# HyperFrames companion skills (hyperframes-core, media-use, ...).
if [ ! -d "$HOME/.claude/skills/hyperframes" ]; then
  hyperframes skills </dev/null >/dev/null 2>&1 || true
fi

# cdn.jsdelivr.net is blocked by the network policy, so keep a local GSAP
# copy that compositions can reference instead of the CDN URL.
GSAP_DIR="$HOME/.cache/hyperframes-vendor"
if [ ! -f "$GSAP_DIR/gsap.min.js" ]; then
  mkdir -p "$GSAP_DIR"
  (cd "$GSAP_DIR" && npm install --no-save --silent gsap@3.14.2 >/dev/null 2>&1 \
    && cp node_modules/gsap/dist/gsap.min.js gsap.min.js)
fi
if [ -n "${CLAUDE_ENV_FILE:-}" ]; then
  echo "export HYPERFRAMES_GSAP_JS=\"$GSAP_DIR/gsap.min.js\"" >> "$CLAUDE_ENV_FILE"
fi

# graphify — knowledge graph of the repo (graphify-out/). The PreToolUse
# hooks in settings.json call /usr/local/bin/graphify, so it must exist.
if ! command -v graphify >/dev/null 2>&1; then
  pip install -q graphifyy >/dev/null 2>&1 \
    || pip install -q --break-system-packages graphifyy >/dev/null 2>&1 || true
fi
if [ ! -f "$HOME/.claude/skills/graphify/SKILL.md" ] && command -v graphify >/dev/null 2>&1; then
  graphify install </dev/null >/dev/null 2>&1 || true
fi
