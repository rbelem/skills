---
name: desktop-browser-automation
description: Drive real browsers on this Linux desktop (KWin/Wayland, flatpak installs) with browser-harness and the Browser Use family (the browser-use CLI and Python agent, browser-harness-mcp), jev-ultrafast, or cua-driver, and pick the right tool per surface. Use when a task needs browser automation — page clicks, typing, or extraction on Chrome, an agentic browser loop, native browser chrome such as permission bubbles or extension e2e, Firefox or Chromium running from flatpak, a browser invisible to AT-SPI, or a browser an MCP cannot spawn.
---

# Desktop browser automation

Route the task to one tool, then drive it through the recipes below. Chrome and Firefox on this desktop ship as flatpaks, so the flatpak rules apply to every desktop launch and every teardown.

## Pick the tool

| Surface | Tool |
|---|---|
| Public page, plain read | curl or the fetch tool. Leave the browser alone. |
| Chrome or Chromium page content (click, type, extract, JS) | browser-harness over CDP. The `browser-use` CLI is the same harness under another name; `browser-use --mcp` serves it to MCP clients. |
| Goal-driven loop over a page | jev-ultrafast, which rides browser-harness; the Python `browser-use` Agent can attach to the same browser. |
| Browser-process chrome: permission bubbles, native dialogs, extension e2e | cua-driver over AT-SPI. CDP cannot see this surface, so no Browser Use tool reaches it. |
| Firefox page content | firefox-devtools MCP against port 9222. cua-driver typed mutation does not support Firefox; the Browser Use family is Chromium-only. |

One browser lane at a time. A browser-harness daemon connects to the whole Chrome instance, not to one site or task.

## Flatpak rules

1. **The sandbox outlives the wrapper pid.** A process that execs `flatpak run <app-id>` hands control to a sandbox the pid does not cover. Teardown is surgical: list `flatpak ps -j`, match the row by `application` plus `pid` or `child-pid`, run `flatpak kill <instanceId>`, then verify the debug port is closed. Never guess among several instances of the app.
2. **The sandbox has a private /tmp.** A browser profile under /tmp dies with the sandbox tmpfs while the browser still runs. Put the profile under a home-granted path such as `~/.local/share/<tool>/profiles`.
3. **An unpacked extension needs a Flatseal grant.** Grant the extension directory's filesystem access to the flatpak before loading it.
4. **An MCP cannot spawn a flatpak browser.** `flatpak run` is not a binary path. Launch it from the shell, then connect the tool to the port.

## Launch recipes

Firefox for the firefox-devtools MCP, which connects to port 9222:

```sh
nohup flatpak run org.mozilla.firefox --marionette --remote-debugging-port=9222 \
  >/tmp/opencode/firefox-flatpak.log 2>&1 &
```

Chromium for CDP, flags straight through `flatpak run` and the profile under the home grant per rule 2:

```sh
nohup flatpak run org.chromium.Chromium --no-first-run \
  --user-data-dir="$HOME/.local/share/browser-profiles/chromium" \
  --remote-debugging-port=9225 about:blank \
  >/tmp/opencode/chromium-flatpak.log 2>&1 &
```

Point browser-harness at `BU_CDP_URL=http://127.0.0.1:9225` — an HTTP endpoint, resolved through `/json/version`. Pick a free port: leia's stack owns 9222-9224, 9226, and 9333 (port table below). In the leia repo, `leia-ctl up --chrome-bin <wrapper>` automates the profile and the teardown.

## Launch from an agent shell

Agent shells strip `DBUS_SESSION_BUS_ADDRESS`, `XDG_RUNTIME_DIR`, and `WAYLAND_DISPLAY` from directly spawned GUI binaries. A wrapper script that re-exports them fixes the scrub. Node `child_process` spawns are unaffected.

## Chromium activation recipe (cua-driver)

Chromium is invisible to AT-SPI, and therefore to cua-driver, until both parts of the recipe exist:

1. `org.a11y.Status.ScreenReaderEnabled=true` on the real session bus before the browser process starts. The property is read at process start; post-spawn changes do nothing:
   ```sh
   busctl --user set-property org.a11y.Bus /org/a11y/bus org.a11y.Status ScreenReaderEnabled b true
   ```
2. `--force-renderer-accessibility` on the chromium command line. Without it the AT-SPI tree stays shallow and never fills in.

Restore the flag on teardown only if you flipped it, and never while a live cua daemon answers: the daemon sets the flag first and re-asserts it at startup, so restoring false under it breaks the next launch's AT-SPI visibility. Run everything on the real session bus (the one-bus rule): daemon, browser, and driver share it. A private `dbus-run-session` bus fails on a developer desktop because the daemon is anchored to the real bus; it works in CI only when every participant shares that one private bus.

Run the smoke probe before depending on the tree: poll `cua-driver call list_windows --arguments '{"pid": <pid>}'` for 2 s. A wedged AT-SPI registry reads as a silent 30 s timeout; `systemctl --user restart at-spi-dbus-bus.service` revives it.

## Browser Use family

`browser-harness`, `browser-harness-mcp`, and the `browser-use` Python package are Browser Use projects (MIT). The `browser-use` CLI ships the same harness code — `browser-use --version` prints the harness version (0.1.13 here), not the Python package version — so the CLI, the MCP server, and the Python agent reach a browser through one CDP layer:

- Attach, never spawn (flatpak rule 4): `BU_CDP_URL=http://127.0.0.1:<port>` for the CLI, the MCP server, and the agent alike. A dedicated automation profile (not the default profile) avoids Chrome's per-connection remote-debugging popup and the default-profile lockdown.
- CLI and MCP: `echo 'print(page_info())' | browser-use` runs raw Python in the persistent session; `--mcp` serves the helpers to MCP clients; `--reload` restarts the daemon. The CLI's 3.0 rewrite removed `--code` and `--cdp-url`: pipe Python on stdin and set `BU_CDP_URL` instead.
- Python agent, for open-ended tasks: `Browser(cdp_url=...)` plus an LLM, or `Browser(use_cloud=True)` for a cloud browser after `browser-harness auth login`. Keep deterministic steps in the harness's stdin code mode; the agent is LLM-driven.
- `BU_CDP_URL` also blocks cloud auto-bootstrap by design, so a local attach on a machine with cloud auth never silently starts a billed cloud browser.
- Limits: CDP only — native browser chrome stays with cua-driver; Chromium only — Firefox stays with firefox-devtools MCP.

## leia lanes and ports

| Port | Owner |
|---|---|
| 9222 | Firefox for the firefox-devtools MCP launch above, or the Chrome Web Store dashboard Chrome with the `leia-cws` profile — never both at once |
| 9223 | leia Firefox adapter (WebDriver BiDi default) |
| 9224 | leia-ctl Chromium CDP (`leia up`, `cli/chrome.js`) |
| 9226 | leia e2e Chromium (`LEIA_E2E_PORT`) — dies with the test run |
| 9333 | leia WS bridge (the extension CSP allows only this port) |

- Extension QA: attach the Browser Use family to 9224 while `leia-ctl up` runs and the harness lists the extension's `chrome-extension://<id>/harness/harness.html` tab (verified 2026-10-17, flatpak Chromium 155). The e2e Chromium on 9226 is throwaway: it lives only for the run.
- Store dashboards: the Chrome Web Store console runs Chrome on 9222 with a dedicated profile (`store/publishing/chrome.md`); `node scripts/cdp-drive.mjs` is its deterministic driver. Use agent lanes for inspection and selector discovery; drive Submit and Publish steps deterministically after reading the dashboard state.

## Teardown

Kill the browser's whole process group (`detached: true` plus `process.kill(-pid)`). Killing only the leader leaves at-spi launcher and registry children behind. For flatpak instances, apply flatpak rule 1.

Per-tool gotchas, the Wayland boundaries, and the failure taxonomy: [REFERENCE.md](REFERENCE.md). Distilled from leia's `docs/cua-e2e.md`, `cli/chrome.js`, `store/publishing/chrome.md`, and Browser Use's README/docs; attach paths verified live 2026-10-17.
