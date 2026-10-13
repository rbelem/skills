---
name: desktop-browser-automation
description: Drive real browsers on this Linux desktop (KWin/Wayland, flatpak installs) with browser-harness, jev-ultrafast, or cua-driver, and pick the right tool per surface. Use when a task needs browser automation — page clicks, typing, or extraction on Chrome, an agentic browser loop, native browser chrome such as permission bubbles or extension e2e, Firefox or Chromium running from flatpak, a browser invisible to AT-SPI, or a browser an MCP cannot spawn.
---

# Desktop browser automation

Route the task to one tool, then drive it through the recipes below. Every
browser on this machine ships as a flatpak, so the flatpak rules apply to
every launch and every teardown.

## Pick the tool

| Surface | Tool |
|---|---|
| Public page, plain read | curl or the fetch tool. Leave the browser alone. |
| Chrome or Chromium page content (click, type, extract, JS) | browser-harness over CDP |
| Goal-driven loop over a page | jev-ultrafast, which rides browser-harness |
| Browser-process chrome: permission bubbles, native dialogs, extension e2e | cua-driver over AT-SPI. CDP cannot see this surface. |
| Firefox page content | firefox-devtools MCP against port 9222. cua-driver typed mutation does not support Firefox. |

One browser lane at a time. A browser-harness daemon is a connection to the
whole Chrome instance, so serialize browser work across agents instead of
creating named daemons.

## Flatpak rules

1. **The sandbox outlives the wrapper pid.** A process that execs
   `flatpak run <app-id>` hands control to a sandbox the pid does not cover.
   Teardown is surgical: list `flatpak ps -j`, match the row by `application`
   plus `pid` or `child-pid`, run `flatpak kill <instanceId>`, then verify the
   debug port is closed. Never guess among several instances of the app.
2. **The sandbox has a private /tmp.** A browser profile under /tmp dies with
   the sandbox tmpfs while the browser still runs. Put the profile under a
   home-granted path such as `~/.local/share/<tool>/profiles`.
3. **An unpacked extension needs a Flatseal grant.** Grant the extension
   directory's filesystem access to the flatpak before loading it.
4. **An MCP cannot spawn a flatpak browser.** `flatpak run` is not a binary
   path. Launch it from the shell, then connect the tool to the port.

## Launch flatpak Firefox for the devtools MCP

```sh
nohup flatpak run org.mozilla.firefox --marionette --remote-debugging-port=9222 \
  >/tmp/opencode/firefox-flatpak.log 2>&1 &
```

The firefox-devtools MCP connects to port 9222.

## Chromium activation recipe (cua-driver)

Chromium is invisible to AT-SPI, and therefore to cua-driver, until both
parts of the recipe exist:

1. `org.a11y.Status.ScreenReaderEnabled=true` on the real session bus before
   the browser process starts. The property is read at process start.
   Post-spawn changes do nothing.
   ```sh
   busctl --user set-property org.a11y.Bus /org/a11y/bus org.a11y.Status \
     ScreenReaderEnabled b true
   ```
2. `--force-renderer-accessibility` on the chromium command line. Without it
   the AT-SPI tree stays shallow and never fills in.

Restore the prior flag value on teardown. Run everything on the real session
bus (the one-bus rule): daemon, browser, and driver share it. A private
`dbus-run-session` bus fails on a developer desktop because the daemon is
anchored to the real bus; it works in CI only when every participant shares
that one private bus.

Run the smoke probe before depending on the tree: poll
`cua-driver call list_windows --arguments '{"pid": <pid>}'` for 2 s. A wedged
AT-SPI registry reads as a silent 30 s timeout;
`systemctl --user restart at-spi-dbus-bus.service` revives it.

## Teardown

Kill the browser's whole process group (`detached: true` plus
`process.kill(-pid)`). Killing only the leader leaves at-spi launcher and
registry children behind. For flatpak instances, apply flatpak rule 1.

Agent shells strip `DBUS_SESSION_BUS_ADDRESS`, `XDG_RUNTIME_DIR`, and
`WAYLAND_DISPLAY` from directly spawned GUI binaries. A wrapper script that
re-exports them works around the scrub. Node `child_process` spawns are
unaffected.

Per-tool gotchas, the Wayland boundaries, and the failure taxonomy:
[REFERENCE.md](REFERENCE.md). Distilled from leia's `docs/cua-e2e.md` and
`cli/chrome.js`.
