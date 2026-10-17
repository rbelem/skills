# Reference

Gotchas per tool, plus the desktop boundaries and the failure taxonomy. Open the section for the tool in play.

## browser-harness

- Find elements in the accessibility tree, not screenshots. Filter `cdp("Accessibility.getFullAXTree")["nodes"]` in Python before printing.
- Click path: AX node, box center, `click_at_xy(x, y)`, then verify with a targeted check. Raw HTML is the fallback for canvas and exotic widgets.
- First navigation of a task is `new_tab(url)`. The daemon preserves the attached tab across invocations. Reuse tabs with `list_tabs()` and `switch_tab()` instead of stacking duplicates.
- Focus-gated pages take `cdp("Emulation.setFocusEmulationEnabled", enabled=True)` inside a `try/finally`. Keep work in the background.
- A dead or stale daemon gets `browser-harness --doctor`. Recover before replacing anything.

## Browser Use family

- The `browser-use` CLI is the harness (same code, `--version` reports the harness version). Its 3.0 rewrite removed `--cdp-url` and `--code`: set `BU_CDP_URL` and pipe Python on stdin. `--headed` does nothing — local control attaches to the visible Chrome. Session recording was removed; screenshot per step instead.
- Devbox trap: this desktop exports `PYTHONPATH` into the nix Python 3.14 site-packages, and a `uvx`/`uv tool` run of `browser-use` then imports that pydantic and dies with `ModuleNotFoundError: No module named 'pydantic_core._pydantic_core'`. Strip it: `env -u PYTHONPATH uvx --from browser-use browser-use ...`.
- Daemon state: local runs share one default daemon; `BU_NAME` names cloud ones. `doctor --json` reports install, daemon, and browser health (`browser_ready`).
- Recordings: `recordings enable` saves browser actions locally, `recordings --latest` prints the newest directory, and `video init`/`video review`/`video export --reviewed` compile one to MP4 — a debugging artifact for a failed session.

## jev-ultrafast

- Prerequisites: Chrome attachable through browser-harness (`browser-harness --doctor`), `TYPESAFE_API_KEY`, and `TEXT_MODEL_API_KEY`. A missing key surfaces at tool-call time. A run that stalls at browser attach means no attachable Chrome.
- A backgrounded or occluded Chrome window freezes renderer timers, menu mounts, and screenshots. Relaunch it with occlusion-backgrounding and timer-throttling disabled.
- Re-observe after every action. Page-fingerprint caches that track only inputs and scroll miss DOM changes that add buttons.
- SPA menus toggle on plain `click` events, so `el.click()` beats CDP mouse pairs, and `a[href]` extractors are blind to href-less SPA anchors.
- Unlabeled inputs need container-text fallback labels, and aria-derived field mappings can be stale on arrival. Verify labels from the DOM. For portal-style dialogs, extract real DOM ids from the page HTML, fill by id, and screenshot after every fill.

## cua-driver

- Element tokens die across snapshots: re-observe before every click, never retry a dead token, verify from fresh state or independent ground truth (a zero exit code is not task success), and pass one named session on every call.
- On Linux, Chromium trusted clicks refuse to preserve background posture (`browser_input_trust_unavailable`). Request `dom_event` when synthetic click semantics are acceptable, or use the native ladder. Never foreground the browser silently.
- Linux Chromium cannot resolve its native modal dialogs while backgrounded. Retry with `delivery_mode:"foreground"` only when foreground activation is acceptable.

## Wayland and KWin boundaries

- KWin exposes no foreign-toplevel protocols, so window discovery rides the AT-SPI registry, and screenshot, activation, and refocus routes are refused.
- Per-window capture is impossible on KWin. Desktop capture needs a one-time interactive portal grant, and that grant is never auto-approved.
- Chromium mutation on Wayland requires provable compositor identity. Generic or ambiguous identity refuses mutation.

## Failure taxonomy

| Symptom | Cause | Handling |
|---|---|---|
| Silent 30 s timeout, daemon serves cached apps | Wedged AT-SPI registry | Restart `at-spi-dbus-bus.service`, else relogin |
| `list_windows {pid}` returns `[]` under `dbus-run-session` | Bus mismatch: daemon on the real bus, browser on a private one | Move everyone onto one bus |
| Storage wiped while the browser still runs | Profile under the sandbox's private /tmp | Flatpak rule 2 |
| Wrapper pid killed, browser still alive | Sandbox outlives the wrapper | Flatpak rule 1 |
| `stale_element_token` repeated | Tokens died across snapshots | Re-observe per click, budget the retries |
| Expected window or dialog never appeared | Timing, dirty profile, or product bug | One wholesale retry, then treat as red |
| Click returned ok, the effect check failed | Product bug | Red immediately, never retried |
