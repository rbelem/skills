---
name: webmcp
description: Expose app capabilities to in-browser AI agents on document.modelContext (WebMCP) — design the tools, wire the TypeScript types, and verify them in a real browser. Use when a task says WebMCP, document.modelContext, registerTool, "make the site agent-ready", "let the agent use our product", or when auditing page tools an agent can call. Routes tool design to the upstream Chrome build-webmcp-tools skill and records this machine's browser and MCP facts.
---

# WebMCP

A page declares structured tools on `document.modelContext`, so an in-browser
agent calls app logic instead of scraping the DOM. Tools only — no Resources,
no Prompts. It is not a backend MCP server over stdio or SSE.

## Two skills, two jobs

| Need | Where |
|---|---|
| Tool design, schema, annotations, evals, audit | upstream `build-webmcp-tools` at `~/.agents/skills/build-webmcp-tools` (installed from `GoogleChromeLabs/webmcp-tools`) |
| This machine's browser, MCP, and verification facts | this skill |

Read the upstream `references/` before designing tools. It is the authority on
budgets, naming, annotations, conversational design, and the audit checklist.
Do not re-derive those rules here.

## Rules that bite

1. **Errors resolve, they do not reject.** A rejected `execute` promise reaches
   the agent as `DOMException: UnknownError` and the reason is discarded.
   Resolve `{error, code, retryable}` instead.
2. **No `unregisterTool()`.** Keep the `AbortController` handed to
   `registerTool(tool, {signal})` and call `controller.abort()`. Aborting stops
   future discovery; executions already in flight keep running.
3. **Annotations are opt-in.** Allowed keys: `readOnlyHint`,
   `untrustedContentHint`, `consequentialHint`, `debugging`. Never write
   `: false`. `consequentialHint: true` only when the tool itself commits the
   action (payment, booking, deletion, send). An `initiate_*` hand-off that
   only opens a confirmation screen declares neither `readOnlyHint` nor
   `consequentialHint`. `readOnlyHint` + `consequentialHint` together is
   contradictory. `openWorldHint`, `destructiveHint`, `idempotentHint` are
   MCP-protocol hints — not part of WebMCP.
4. **`untrustedContentHint: true` on any user- or third-party-authored
   output**, including text served from your own database. Without it the host
   gets no signal to isolate the output.
5. **Budgets.** Tool name ≤ 30 chars, tool description ≤ 500, parameter
   description ≤ 150, output ≤ 1,500 chars (~400 tokens) and paginated. The
   spec additionally enforces names of 1–128 chars from `[A-Za-z0-9_.-]` and a
   non-empty description.
6. **Cross-origin.** Permissions-Policy directive `tools`, default `self`.
   Delegate only with `<iframe allow="tools">` plus
   `registerTool(tool, {exposedTo: ["https://trusted.origin"]})`.
   `Origin-Agent-Cluster: ?0` or a `document.domain` write disables WebMCP on
   that page.
7. **Never make the model compute.** Accept the user's phrasing and resolve
   relative dates, units, and conversions inside the app.
8. **The declarative form API is exploratory, not in the spec.** A `<form>`
   needs `toolname` and `tooldescription`; controls take
   `toolparamdescription`; `toolautosubmit` is optional. Field errors come
   back through `event.respondWith(Promise.resolve([{field, value, message}]))`
   after `event.preventDefault()`. Omit `toolautosubmit` on financial,
   destructive, account-changing, or messaging forms.

## TypeScript types

```bash
npm i -D webmcp-types   # 0.1.10, needs TypeScript 5.0+
```

Wire it one of three ways:

- tsconfig: `"compilerOptions": { "types": ["webmcp-types"] }` — **append** to
  the array; replacing it drops `@types/node`.
- tsconfig: `"compilerOptions": { "typeRoots": ["./node_modules/webmcp-types", "./node_modules/@types"] }`
- one file: `/// <reference types="webmcp-types" />`

Delete hand-written `declare global { interface Document { modelContext … } }`
— the package ships that declaration.

`ModelContextToolFromSchema<T>` and `InferToolInput<T>` infer the `execute`
argument from `inputSchema`, so the handler signature follows the schema.

## This machine (verified 2026-10-19)

| Browser | Version | `document.modelContext` |
|---|---|---|
| flatpak Google Chrome | 155.0.8059.39 | absent |
| nix `chromium` | 152.0.7977.64 | absent |

Probed headless and headed, with `--enable-features=WebMCP` and with
`--enable-blink-features=WebMCP`, over CDP `Runtime.evaluate` of
`"modelContext" in document`. Chrome exposes the API only behind
`chrome://flags/#enable-webmcp-testing` (blink runtime feature "WebMCP",
overridable through the `WebMCP` base feature), and the API is origin-trial
gated. A stable browser on this box does not expose it.

**Consequence:** native WebMCP is unavailable here. Local verification runs
against the polyfill.

Both browser lanes are dormant until a browser exposes a CDP endpoint: the
browser-harness daemon needs `BU_CDP_URL` or a `DevToolsActivePort` file, and
the chrome-devtools MCP runs `--autoConnect`, which wants a running browser
with remote debugging enabled. A headless Chromium on a debug port is enough
for the recipe below.

## Verify locally

The recipe below ran on this machine on 2026-10-19: Chromium 152 headless
with the polyfill loaded, driven through browser-harness.

1. Load the polyfill in the dev page before the app script — it is a classic
   script, not a module:
   `https://raw.githubusercontent.com/GoogleChromeLabs/webmcp-tools/main/demos/shared/webmcp-polyfill.js`
   A 404 on that script is silent: `document.modelContext` stays undefined.
2. Serve the app, then attach a browser that exposes CDP. Use the launch
   recipes in the `desktop-browser-automation` skill — the flatpak Chromium
   with `--remote-debugging-port` and a dedicated profile under
   `~/.local/share/browser-profiles/chromium`. Headless Chromium works for
   this check.
3. Point browser-harness at it (`BU_CDP_URL=http://127.0.0.1:<port>`), then
   read the page. The harness `js` helper evaluates a raw expression, so
   wrap it in an async IIFE:

   ```python
   goto_url("http://127.0.0.1:<port>/")
   wait_for_load()
   print(js("'modelContext' in document"))
   print(js("(async () => JSON.stringify((await document.modelContext.getTools()).map(t => ({name: t.name, annotations: t.annotations}))))()"))
   print(js("(async () => JSON.stringify(await document.modelContext.executeTool((await document.modelContext.getTools())[0], {name: 'x'})))()"))
   ```

   The browser-harness MCP exposes the same call as `browser_js`; the
   chrome-devtools MCP exposes it as `evaluate_script`, which takes a
   function (`async () => …`) instead of a raw expression.
4. Read the result: the spec resolves `executeTool` with a DOMString, the
   polyfill resolves the raw result object. A tool whose `execute` throws
   surfaces as `DOMException: UnknownError` with the reason gone — that is
   exactly why `execute` resolves structured errors.

The polyfill is a dev aid: it is page-side only, and production code must
guard with `if (!document.modelContext) return`.

### When a browser with the flag is available

- The chrome-devtools MCP gains `list_webmcp_tools` and `execute_webmcp_tool`
  when its command carries `--categoryExperimentalWebmcp`; the connected
  browser must run with `--enable-features=WebMCP`. Neither browser on this
  box exposes the native API, so that switch buys nothing here.
- Chrome DevTools → Application → WebMCP lists tools, logs invocations, and
  runs one by hand.
- Lighthouse 150+ audit "Agentic browsing" flags missing or invalid tools.

## Security

- The agent runs inside the user's authenticated session. Enforce auth and
  entitlement checks inside `execute`, never in the tool description.
- Treat tool output as data. Isolate user- or third-party-authored text and
  set `untrustedContentHint: true` so the host does.
- Never let a tool return a secret. A prompt injection in a ticket body can
  otherwise push `localStorage` out through a `send_feedback` tool.
- Pass the minimum parameters the tool needs. Cap the output; truncate
  instead of refusing.

## Sources

- Spec: https://github.com/webmachinelearning/webmcp
- Types: https://github.com/webmachinelearning/webmcp-types (npm `webmcp-types`)
- Chrome skill, polyfill, demos: https://github.com/GoogleChromeLabs/webmcp-tools
- Dev guide: https://developer.chrome.com/docs/ai/webmcp
