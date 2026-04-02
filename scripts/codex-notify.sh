#!/usr/bin/env bash

set -euo pipefail

log_file="${HOME}/.codex/log/codex-tui.log"
bell_cooldown="${CODEX_NOTIFY_COOLDOWN:-2}"
watcher_pid=""
last_bell_at=0

# Older shells may still export ntfy auto-done settings even after the shell
# integration was removed from ~/.bashrc. Clear them before launching Codex so
# child login shells do not try to send desktop notifications over DBus.
unset AUTO_NTFY_DONE_IGNORE
unset AUTO_NTFY_DONE_OPTS
unset AUTO_NTFY_DONE_UNFOCUSED_ONLY
unset AUTO_NTFY_DONE_LONGER_THAN
unset ntfy_start_time
unset ntfy_command

start_watcher() {
    [ -f "$log_file" ] || return 0

    tail -n 0 -F "$log_file" 2>/dev/null | while IFS= read -r line; do
        case "$line" in
            *"codex_core::tasks: close"*)
                now=$(date +%s)
                if [ $((now - last_bell_at)) -ge "$bell_cooldown" ]; then
                    printf '\a' > /dev/tty
                    last_bell_at=$now
                fi
                ;;
        esac
    done &
    watcher_pid=$!
}

stop_watcher() {
    if [ -n "${watcher_pid:-}" ]; then
        kill "$watcher_pid" 2>/dev/null || true
        wait "$watcher_pid" 2>/dev/null || true
    fi
}

start_watcher
trap stop_watcher EXIT INT TERM

command codex "$@"
