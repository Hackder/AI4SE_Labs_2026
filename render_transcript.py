#!/usr/bin/env python3
"""Render a Claude Code transcript (.jsonl) as a readable, self-contained HTML page.

Usage:
    python3 render_transcript.py path/to/transcript.jsonl [-o out.html] [--open]

User and assistant messages are shown as a chat; tool calls, tool results,
thinking and injected skill text are collapsible. Markdown is rendered in the
browser (falls back to plain text when offline).
"""

import argparse
import html
import json
import subprocess
import sys
from pathlib import Path

MAX_RESULT_CHARS = 20000


def load(path):
    records = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    records.append(json.loads(line))
                except json.JSONDecodeError:
                    pass
    return records


def result_text(content):
    if isinstance(content, str):
        return content
    parts = []
    for block in content or []:
        if block.get("type") == "text":
            parts.append(block.get("text", ""))
        elif block.get("type") == "image":
            parts.append("[image]")
        else:
            parts.append(f"[{block.get('type')}]")
    return "\n".join(parts)


def build_events(records):
    """Flatten records into a list of display events, in file order."""
    title = None
    results = {}
    for r in records:
        if r.get("type") == "custom-title":
            title = r.get("customTitle")
        if r.get("type") == "user" and isinstance(r["message"].get("content"), list):
            for b in r["message"]["content"]:
                if b.get("type") == "tool_result":
                    results[b["tool_use_id"]] = b

    events = []
    for r in records:
        t = r.get("type")
        if t not in ("user", "assistant") or r.get("isSidechain"):
            continue
        ts = r.get("timestamp", "")
        content = r["message"].get("content")
        if t == "user":
            if r.get("isCompactSummary"):
                events.append({"kind": "meta", "label": "Compacted context summary", "text": result_text(content), "ts": ts})
            elif isinstance(content, str):
                events.append({"kind": "user", "text": content, "ts": ts, "meta": bool(r.get("isMeta"))})
            else:
                for b in content:
                    if b.get("type") == "text":
                        text = b.get("text", "")
                        if r.get("isMeta") or text.startswith("Base directory for this skill"):
                            events.append({"kind": "meta", "label": "Injected context", "text": text, "ts": ts})
                        else:
                            events.append({"kind": "user", "text": text, "ts": ts})
        else:
            model = r["message"].get("model", "")
            for b in content or []:
                bt = b.get("type")
                if bt == "text" and b.get("text", "").strip():
                    events.append({"kind": "assistant", "text": b["text"], "ts": ts, "model": model})
                elif bt == "thinking" and b.get("thinking", "").strip():
                    events.append({"kind": "thinking", "text": b["thinking"], "ts": ts})
                elif bt == "tool_use":
                    res = results.get(b.get("id"), {})
                    out = result_text(res.get("content"))
                    if len(out) > MAX_RESULT_CHARS:
                        out = out[:MAX_RESULT_CHARS] + f"\n… [{len(out) - MAX_RESULT_CHARS} more chars truncated]"
                    events.append({
                        "kind": "tool",
                        "name": b.get("name", "?"),
                        "input": b.get("input", {}),
                        "output": out,
                        "error": bool(res.get("is_error")),
                        "ts": ts,
                    })
    return title, events


def tool_summary(name, inp):
    for key in ("description", "command", "file_path", "pattern", "query", "url", "prompt"):
        if isinstance(inp.get(key), str):
            return inp[key].splitlines()[0][:140]
    return ""


def esc(s):
    return html.escape(s or "")


def render(title, events, source):
    out = []
    stats = {"user": 0, "assistant": 0, "tool": 0}
    for e in events:
        k = e["kind"]
        time = esc(e["ts"][11:19]) if e.get("ts") else ""
        if k in stats:
            stats[k] += 1
        if k in ("user", "assistant"):
            who = "You" if k == "user" else "Claude"
            extra = f' <span class="model">{esc(e.get("model"))}</span>' if e.get("model") else ""
            out.append(
                f'<div class="msg {k}"><div class="who">{who}{extra}<span class="ts">{time}</span></div>'
                f'<div class="md">{esc(e["text"])}</div></div>'
            )
        elif k == "thinking":
            out.append(
                f'<details class="aux thinking"><summary>Thinking <span class="ts">{time}</span></summary>'
                f'<div class="md">{esc(e["text"])}</div></details>'
            )
        elif k == "meta":
            out.append(
                f'<details class="aux meta"><summary>{esc(e["label"])} <span class="ts">{time}</span></summary>'
                f'<div class="md">{esc(e["text"])}</div></details>'
            )
        elif k == "tool":
            summary = tool_summary(e["name"], e["input"])
            err = ' <span class="err">error</span>' if e["error"] else ""
            out.append(
                f'<details class="aux tool"><summary><code>{esc(e["name"])}</code> {esc(summary)}{err}'
                f'<span class="ts">{time}</span></summary>'
                f'<div class="label">Input</div><pre>{esc(json.dumps(e["input"], indent=2, ensure_ascii=False))}</pre>'
                f'<div class="label">Result</div><pre>{esc(e["output"])}</pre></details>'
            )

    page_title = esc(title or Path(source).stem)
    return TEMPLATE.format(
        title=page_title,
        source=esc(str(source)),
        stats=f'{stats["user"]} user messages · {stats["assistant"]} assistant messages · {stats["tool"]} tool calls',
        body="\n".join(out),
    )


TEMPLATE = """<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<style>
:root {{ --bg:#fafaf9; --fg:#1c1917; --muted:#78716c; --user:#e0ecff; --asst:#fff; --aux:#f5f5f4; --border:#e7e5e4; --accent:#c2410c; }}
@media (prefers-color-scheme: dark) {{
  :root {{ --bg:#1c1917; --fg:#e7e5e4; --muted:#a8a29e; --user:#1e3a5f; --asst:#292524; --aux:#24201e; --border:#44403c; --accent:#fb923c; }}
}}
body {{ background:var(--bg); color:var(--fg); font:15px/1.55 -apple-system, system-ui, sans-serif; margin:0; }}
main {{ max-width:860px; margin:0 auto; padding:24px 16px 80px; }}
header {{ border-bottom:1px solid var(--border); margin-bottom:20px; padding-bottom:12px; }}
h1 {{ font-size:22px; margin:0 0 4px; }}
.sub {{ color:var(--muted); font-size:13px; }}
.controls {{ margin-top:8px; font-size:13px; color:var(--muted); display:flex; gap:16px; flex-wrap:wrap; }}
.msg {{ border:1px solid var(--border); border-radius:10px; padding:10px 14px; margin:14px 0; overflow-wrap:anywhere; }}
.msg.user {{ background:var(--user); }}
.msg.assistant {{ background:var(--asst); }}
.who {{ font-weight:600; font-size:13px; margin-bottom:4px; }}
.model {{ font-weight:400; color:var(--muted); }}
.ts {{ float:right; font-weight:400; color:var(--muted); font-size:12px; margin-left:8px; }}
.aux {{ background:var(--aux); border:1px solid var(--border); border-radius:8px; margin:6px 0 6px 24px; font-size:13px; }}
.aux summary {{ cursor:pointer; padding:5px 10px; color:var(--muted); white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }}
.aux summary code {{ color:var(--accent); }}
.aux > :not(summary) {{ margin:0 10px 8px; }}
.label {{ font-size:11px; text-transform:uppercase; letter-spacing:.05em; color:var(--muted); }}
.err {{ color:#dc2626; font-weight:600; }}
pre {{ background:var(--bg); border:1px solid var(--border); border-radius:6px; padding:8px; overflow:auto; max-height:480px; font-size:12px; white-space:pre-wrap; }}
.md pre {{ max-height:none; }}
.md table {{ border-collapse:collapse; display:block; overflow-x:auto; }}
.md th, .md td {{ border:1px solid var(--border); padding:4px 8px; }}
.md p:first-child {{ margin-top:0; }} .md p:last-child {{ margin-bottom:0; }}
.md.plain {{ white-space:pre-wrap; }}
body.hide-tools .tool, body.hide-thinking .thinking, body.hide-meta .meta {{ display:none; }}
</style></head>
<body>
<main>
<header>
  <h1>{title}</h1>
  <div class="sub">{source}<br>{stats}</div>
  <div class="controls">
    <label><input type="checkbox" data-hide="hide-tools"> Hide tool calls</label>
    <label><input type="checkbox" data-hide="hide-thinking"> Hide thinking</label>
    <label><input type="checkbox" data-hide="hide-meta"> Hide injected context</label>
    <label><input type="checkbox" id="expand"> Expand all</label>
  </div>
</header>
{body}
</main>
<script src="https://cdn.jsdelivr.net/npm/marked@12.0.2/marked.min.js"></script>
<script>
document.querySelectorAll('[data-hide]').forEach(cb => cb.addEventListener('change', () =>
  document.body.classList.toggle(cb.dataset.hide, cb.checked)));
document.getElementById('expand').addEventListener('change', e =>
  document.querySelectorAll('details').forEach(d => d.open = e.target.checked));
document.querySelectorAll('.md').forEach(el => {{
  if (window.marked) el.innerHTML = marked.parse(el.textContent);
  else el.classList.add('plain');
}});
</script>
</body></html>
"""


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("jsonl", type=Path)
    ap.add_argument("-o", "--output", type=Path, help="output HTML (default: next to the jsonl)")
    ap.add_argument("--open", action="store_true", help="open the result in the browser")
    args = ap.parse_args()

    title, events = build_events(load(args.jsonl))
    output = args.output or args.jsonl.with_suffix(".html")
    output.write_text(render(title, events, args.jsonl), encoding="utf-8")
    print(f"Wrote {output} ({len(events)} events)")
    if args.open:
        subprocess.run(["open" if sys.platform == "darwin" else "xdg-open", str(output)])


if __name__ == "__main__":
    main()
