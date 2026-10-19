#!/usr/bin/env python3
"""Print a compact report of an opencode session: applied model, tool calls, text.

Reads the JSON from `opencode api get /api/session/<id>/message` on stdin, or
a file path as argv[1]. Message records put parts in `content` (not `parts`),
and the assistant record carries the applied provider/model/variant + cost.
"""

import json
import sys

path = sys.argv[1] if len(sys.argv) > 1 else None
raw = open(path).read() if path else sys.stdin.read()
data = json.loads(raw)

msgs = data.get("data", data)
if isinstance(msgs, dict):
    msgs = msgs.get("messages", [])

served = None
texts = []
tools = []
for m in msgs:
    if m.get("type") == "assistant":
        md = m.get("model") or {}
        served = f"{md.get('providerID')}/{md.get('id')} variant={md.get('variant')} cost={m.get('cost', '?')}"
    for c in m.get("content") or []:
        t = c.get("type")
        if t == "text":
            texts.append(c.get("text", ""))
        elif t == "tool":
            state = c.get("state") or {}
            out = state.get("output")
            if isinstance(out, dict):
                out = out.get("output") or out.get("stdout") or json.dumps(out)[:300]
            tools.append(
                {
                    "tool": c.get("tool") or c.get("name"),
                    "status": state.get("status"),
                    "input": str(c.get("input"))[:200],
                    "output": str(out)[:400],
                }
            )
        elif t == "reasoning":
            texts.append("[reasoning] " + str(c.get("text", ""))[:200])

print("served:", served)
print("tool_calls:", len(tools))
for t in tools:
    print(
        "  TOOL",
        t["tool"],
        t["status"],
        "| in:",
        t["input"][:120],
        "| out:",
        t["output"][:250].replace("\n", " "),
    )
print("text:", " / ".join(x.strip() for x in texts if x.strip())[:600])
