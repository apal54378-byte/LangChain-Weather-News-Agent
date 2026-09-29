# The Meridian

A LangChain practice project: a city desk that reports current weather and recent
news for any city, exposed both as a Streamlit web app and a terminal agent.

Model: `openai/gpt-oss-20b` via Groq. Tools: OpenWeatherMap + Tavily.

---

## Quick start

```bash
# 1. install
python -m venv .venv
.venv\Scripts\activate            # Windows
# source .venv/bin/activate       # macOS / Linux
pip install -r requirements.txt

# 2. create .env in the project root
#    GROQ_API_KEY=...
#    TAVILY_API_KEY=...
#    OPENWEATHER_API_KEY=...

# 3. run the web app
streamlit run app.py
```

The app opens at http://localhost:8501.

## Requirements

Python 3.13 (tested on 3.13.15).

| Package | Version | Why |
|---|---|---|
| `langchain` | 1.4.2 | `create_agent` |
| `langchain-core` | 1.6.5 | messages, runnables, prompts |
| `langchain-groq` | 1.1.3 | Groq chat model |
| `langchain-community` | 0.4.2 | `TavilySearchResults` (see caveat) |
| `tavily-python` | 0.8.4 | Tavily client |
| `streamlit` | 1.64.0 | web UI |
| `python-dotenv` | 1.2.3 | loads `.env` |
| `requests` | 2.34.2 | OpenWeather HTTP calls |

## Project layout

```
Rag_Practice/
├── app.py                 Streamlit entry point — start here
├── tools.py               shared tools + agent factory (imported by app & CLI)
├── Agent.py               terminal version of the same agent
├── main.py                raw OpenWeather request
├── demo.py                raw Tavily search
├── Custom_tool.py         defining and calling a @tool
├── Pre_built_tool.py      TavilySearchResults + LCEL chain
├── Sequence_runnable.py   prompt | llm | parser
├── Parallel_runnable.py   RunnableParallel fan-out
├── RunnablePassthrough.py RunnablePassthrough.assign
├── .streamlit/config.toml "The Broadsheet" theme
└── requirements.txt
```

`tools.py` is the single source of truth for the tools and the agent, so `app.py`
and `Agent.py` never drift apart.

## Scripts

| Command | What it demonstrates |
|---|---|
| `streamlit run app.py` | Full UI: chat, tool-call ledger, streaming |
| `python Agent.py` | Same agent, interactive terminal prompts |
| `python Sequence_runnable.py` | LCEL sequence: `prompt \| llm \| parser` |
| `python Parallel_runnable.py` | `RunnableParallel` — two prompts, one input |
| `python RunnablePassthrough.py` | `assign()` passes input through, adds a key |
| `python Custom_tool.py` | `@tool` decorator + manual tool-call loop |
| `python Pre_built_tool.py` | Prebuilt `TavilySearchResults` piped into a chain |
| `python main.py` | Plain `requests.get` against OpenWeather |
| `python demo.py` | Plain `TavilyClient.search` |

## The web app

`app.py` uses `langchain.agents.create_agent`, which owns the tool-calling loop,
so there is no hand-written dispatch code.

**Features**

- Chat interface with token-by-token streaming (`st.write_stream`)
- Tool calls rendered as an expanded "wire log" — each call shows its arguments
  and the raw response
- Reasoning suppressed from the transcript; `gpt-oss-20b` emits a long
  `reasoning_content` preamble that would otherwise flood the answer
- Sidebar scope switch (news / weather / both), temperature, tool-log toggle
- Suggestion chips on an empty session
- "New conversation" button clears the thread

**Known limitation.** Replayed history sends your prompts and the model's final
answers, but not the raw tool results. A follow-up question re-fetches rather than
recalls. Fine for short sessions; move to a `checkpointer` if you need real
persistence.

## The theme

`.streamlit/config.toml` defines **Aurora** — a dark glassmorphism palette: midnight
`#0A0A12` base, violet primary `#7C3AED`, cyan and magenta accents, large radii.
Colours sit in `config.toml`; ~300 lines of CSS in `app.py` handle structure.

What's in the CSS:

- **Animated aurora backdrop** — four blurred radial blobs (violet, cyan, magenta,
  lime) drifting on independent 26–38s loops. The app container is forced
  transparent so the backdrop shows through the glass.
- **Glass surfaces** — `backdrop-filter: blur(22px) saturate(150%)` on the
  sidebar, chat bubbles, composer, buttons and status pills.
- **Role-coloured chat glow** — assistant bubbles glow violet
  (`rgba(167,139,250,.32)`), user bubbles glow cyan (`rgba(34,211,238,.26)`).
  Done with `:has()` on a `.voice` marker.
- **Gradient hero** — clipped gradient text on the title.
- **Live service pills** — Groq / OpenWeather / Tavily, each with a glowing dot
  that turns red if the key is missing.
- **Gradient scrollbar** and a focus ring on the composer.

All colour pairs meet WCAG AA: body text 16.5:1, violet 7.3:1, cyan 10.9:1,
white-on-violet buttons 5.7:1, section labels 4.8:1.

Animations respect `prefers-reduced-motion`.

### Tool-call log

Every tool call is rendered identically whether you just sent it or reloaded the
page — one `wire_log` path is used for both, so a turn never changes appearance.
The log is expanded by default and shows the call, its arguments, and the raw
response in a nested expander. Turn off **Show tool calls** in the sidebar to hide
it and get plain answers.

## Notes and caveats

- **`langchain-community` is deprecated upstream.** `Pre_built_tool.py` is the
  only file that imports it, and it prints a deprecation warning. Everything else
  uses first-party packages. Migrate that one file to a standalone integration
  package when one ships.
- **Tool call history is not replayed** in the UI — see the limitation above.
- **`.env` holds live keys.** It is gitignored. For a shared deployment, move the
  keys to `.streamlit/secrets.toml` and read them with `st.secrets` instead.
- **The CSS uses `:has()`** to tint chat bubbles by role. Very old browsers lose
  the violet/cyan distinction; layout is unaffected.

## Troubleshooting

**`GroqError: The api_key client option must be set`** — `.env` is missing or
`GROQ_API_KEY` is not loaded. Confirm the file sits in the project root and that
the script calls `load_dotenv()` before constructing the model.

**OpenWeather returns 401** — the key is missing, not yet activated, or was built
for a different host. New keys can take a few minutes to activate.

**"Missing keys in .env" banner in the app** — the sidebar lists exactly which of
the three keys is absent.

**Tavily returns no news** — a valid key with no remaining quota returns an empty
result set rather than an error.
