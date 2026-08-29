#!/usr/bin/env bash
# setup-mistral.sh
# Idempotent installer for MISTRAL_API_KEY used by the upstream ux-transcribe skill.
# Run by the agent from chat during the user's first onboarding
# (see skills/00-welcome/SKILL.md) or manually by the researcher.
#
# MISTRAL_API_KEY lives in ux-transcribe's own store:
#   ~/.config/ux-transcribe/.env
# (Not in ux-research-pipeline/.env — this is a deliberate split, see AGENT.md §9.)
#
# Behavior:
#   1. If the key already exists in the store and is valid (curl 200) — prints [ok] and exits.
#   2. If the key exists but curl returns 401 — prints [fail] and asks to overwrite.
#   3. If there is no key — expects it in the MISTRAL_API_KEY variable (passed by the agent).
#      If the variable is unset — prints instructions.
#   4. Writes the key to the store, makes a test request, prints the result.
#
# Usage (by the agent from chat):
#   MISTRAL_API_KEY="m_xxx..." bash shared/scripts/setup-mistral.sh
#
# Usage (manually by the researcher, to check status):
#   bash shared/scripts/setup-mistral.sh   # no arguments — status check
#
# Exit codes:
#   0 — key present and valid
#   1 — key present but invalid (401 from Mistral)
#   2 — no key, and none passed via MISTRAL_API_KEY
#   3 — network error (key written, but could not be verified)
#   4 — curl not installed / other system error

set -euo pipefail

STORE_DIR="$HOME/.config/ux-transcribe"
STORE_FILE="$STORE_DIR/.env"
MISTRAL_MODELS_URL="https://api.mistral.ai/v1/models"

# ─── Helpers ──────────────────────────────────────────────────────────────────

red()    { printf '\033[31m%s\033[0m\n' "$*"; }
green()  { printf '\033[32m%s\033[0m\n' "$*"; }
yellow() { printf '\033[33m%s\033[0m\n' "$*"; }

read_key_from_store() {
  if [[ -f "$STORE_FILE" ]]; then
    grep -E '^MISTRAL_API_KEY=' "$STORE_FILE" 2>/dev/null \
      | tail -n 1 \
      | sed -E 's/^MISTRAL_API_KEY=//; s/^"//; s/"$//'
  fi
}

check_curl() {
  if ! command -v curl >/dev/null 2>&1; then
    red "[fail] curl is not installed — cannot verify the key."
    yellow "  Install curl (macOS: already present; Linux: apt-get install curl) and run again."
    exit 4
  fi
}

validate_key() {
  local key="$1"
  local http_code
  http_code=$(curl -s -o /dev/null -w '%{http_code}' \
    --max-time 10 \
    -H "Authorization: Bearer $key" \
    "$MISTRAL_MODELS_URL" 2>/dev/null || echo "000")

  case "$http_code" in
    200) return 0 ;;   # ok
    401) return 1 ;;   # invalid key
    000) return 3 ;;   # network / timeout
    *)   yellow "  Mistral API returned HTTP $http_code (neither 200 nor 401). Treating the key as invalid."
         return 1 ;;
  esac
}

write_key_to_store() {
  local key="$1"
  mkdir -p "$STORE_DIR"
  chmod 700 "$STORE_DIR"

  # If the file exists and already has some MISTRAL_API_KEY — drop that line.
  if [[ -f "$STORE_FILE" ]]; then
    grep -v -E '^MISTRAL_API_KEY=' "$STORE_FILE" > "$STORE_FILE.tmp" || true
    mv "$STORE_FILE.tmp" "$STORE_FILE"
  fi

  printf 'MISTRAL_API_KEY="%s"\n' "$key" >> "$STORE_FILE"
  chmod 600 "$STORE_FILE"
}

print_how_to_get_key() {
  cat <<'EOF'

How to get a MISTRAL_API_KEY:
  1. Open https://console.mistral.ai/
  2. Sign up (login via Google is supported).
  3. Go to API Keys → Create new key.
  4. Copy the key (shown only once).
  5. Pass it to the agent in chat — it will run the script.

The key is stored in your home directory (~/.config/ux-transcribe/.env)
with 0600 permissions and never leaves your machine.
EOF
}

# ─── Main ────────────────────────────────────────────────────────────────────

check_curl

EXISTING_KEY="$(read_key_from_store || true)"
INCOMING_KEY="${MISTRAL_API_KEY:-}"

# ── Case 1: no key anywhere ──────────────────────────────────────────────────
if [[ -z "$EXISTING_KEY" && -z "$INCOMING_KEY" ]]; then
  red "[fail] MISTRAL_API_KEY is not configured."
  print_how_to_get_key
  exit 2
fi

# ── Case 2: a new key arrived — write and verify ─────────────────────────────
if [[ -n "$INCOMING_KEY" ]]; then
  if [[ -n "$EXISTING_KEY" && "$EXISTING_KEY" != "$INCOMING_KEY" ]]; then
    yellow "[info] Overwriting the existing key in $STORE_FILE."
  fi
  write_key_to_store "$INCOMING_KEY"
  KEY_TO_CHECK="$INCOMING_KEY"
else
  KEY_TO_CHECK="$EXISTING_KEY"
fi

# ── Validation ───────────────────────────────────────────────────────────────
echo "[..] Checking the key via $MISTRAL_MODELS_URL ..."

set +e
validate_key "$KEY_TO_CHECK"
VALIDATION_RC=$?
set -e

case $VALIDATION_RC in
  0)
    green "[ok] MISTRAL_API_KEY is valid. The key is stored in $STORE_FILE."
    echo "[hint] ux-transcribe and 06-transcribe can now run."
    exit 0
    ;;
  1)
    red "[fail] Key is invalid (HTTP 401). It may be expired, revoked, or copied incorrectly."
    yellow "  Run again with a current key:"
    yellow "    MISTRAL_API_KEY=\"<new key>\" bash shared/scripts/setup-mistral.sh"
    exit 1
    ;;
  3)
    yellow "[skip] Network error — could not reach $MISTRAL_MODELS_URL."
    yellow "  The key was written to $STORE_FILE, but its validity could not be verified."
    yellow "  Check your network and run again with no arguments: bash shared/scripts/setup-mistral.sh"
    exit 3
    ;;
esac
