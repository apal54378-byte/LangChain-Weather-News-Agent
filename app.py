import time

import streamlit as st
from langchain_core.messages import (
    AIMessage,
    AIMessageChunk,
    HumanMessage,
    ToolMessage,
)

import tools

st.set_page_config(
    page_title="Meridian — city desk",
    page_icon=":material/newspaper:",
    layout="centered",
)

st.html(
    """
<style>
  /* ================= AURORA — dark glassmorphism ================= */

  :root {
    --bg:      #0A0A12;
    --violet:  #7C3AED;
    --violet-l:#A78BFA;
    --cyan:    #22D3EE;
    --magenta: #F472B6;
    --lime:    #A3E635;
    --glass:   rgba(255,255,255,0.045);
    --glass-2: rgba(255,255,255,0.075);
    --edge:    rgba(255,255,255,0.10);
    --edge-hi: rgba(255,255,255,0.22);
  }

  /* ---------- animated aurora backdrop ---------- */
  body { background: var(--bg); }

  .aurora {
    position: fixed;
    inset: 0;
    z-index: 0;
    overflow: hidden;
    pointer-events: none;
  }
  .aurora span {
    position: absolute;
    border-radius: 50%;
    filter: blur(90px);
    opacity: 0.55;
    will-change: transform;
  }
  .aurora .a1 {
    width: 46vw; height: 46vw; top: -12vw; left: -8vw;
    background: radial-gradient(circle, #7C3AED 0%, transparent 70%);
    animation: drift1 26s ease-in-out infinite;
  }
  .aurora .a2 {
    width: 40vw; height: 40vw; top: 6vh; right: -10vw;
    background: radial-gradient(circle, #22D3EE 0%, transparent 70%);
    animation: drift2 32s ease-in-out infinite;
  }
  .aurora .a3 {
    width: 44vw; height: 44vw; bottom: -16vw; left: 22vw;
    background: radial-gradient(circle, #F472B6 0%, transparent 70%);
    animation: drift3 38s ease-in-out infinite;
  }
  .aurora .a4 {
    width: 26vw; height: 26vw; bottom: 18vh; right: 18vw;
    background: radial-gradient(circle, #A3E635 0%, transparent 70%);
    opacity: 0.28;
    animation: drift2 29s ease-in-out infinite reverse;
  }

  @keyframes drift1 {
    0%,100% { transform: translate(0,0) scale(1); }
    50%     { transform: translate(8vw, 6vh) scale(1.18); }
  }
  @keyframes drift2 {
    0%,100% { transform: translate(0,0) scale(1.05); }
    50%     { transform: translate(-7vw, 9vh) scale(0.88); }
  }
  @keyframes drift3 {
    0%,100% { transform: translate(0,0) scale(0.95); }
    50%     { transform: translate(6vw, -8vh) scale(1.22); }
  }

  /* lift app content above the backdrop */
  [data-testid="stAppViewContainer"],
  .stApp,
  [data-testid="stHeader"] { background: transparent; }
  [data-testid="stAppViewContainer"] > .main { position: relative; z-index: 1; }
  header[data-testid="stHeader"] { background: transparent; }

  /* ---------- glass surfaces ---------- */
  .glass {
    background: var(--glass);
    border: 1px solid var(--edge);
    border-radius: 18px;
    backdrop-filter: blur(22px) saturate(150%);
    -webkit-backdrop-filter: blur(22px) saturate(150%);
    box-shadow: 0 8px 32px rgba(0,0,0,0.45);
  }

  /* ---------- hero ---------- */
  .hero {
    padding: 1.5rem 1.6rem 1.3rem;
    margin-bottom: 1.1rem;
  }
  .hero h1 {
    font-family: 'Space Grotesk', sans-serif;
    font-weight: 700;
    font-size: 3rem;
    line-height: 1.02;
    letter-spacing: -0.03em;
    margin: 0 0 0.35rem;
    background: linear-gradient(100deg, #FFFFFF 0%, #A78BFA 38%, #22D3EE 68%, #F472B6 100%);
    -webkit-background-clip: text;
    background-clip: text;
    -webkit-text-fill-color: transparent;
  }
  .hero p {
    margin: 0;
    color: #A5A5C4;
    font-size: 0.95rem;
    line-height: 1.5;
  }
  .hero .tagrow {
    display: flex;
    flex-wrap: wrap;
    gap: 0.4rem;
    margin-top: 0.9rem;
  }

  /* glowing service pills */
  .pill {
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
    font-size: 0.7rem;
    font-weight: 600;
    letter-spacing: 0.05em;
    padding: 0.28rem 0.7rem;
    border-radius: 999px;
    border: 1px solid var(--edge);
    background: var(--glass-2);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    color: #D6D6EC;
  }
  .pill .dot {
    width: 6px; height: 6px;
    border-radius: 50%;
    background: var(--lime);
    box-shadow: 0 0 8px var(--lime);
  }
  .pill.violet .dot { background: var(--violet-l); box-shadow: 0 0 8px var(--violet-l); }
  .pill.cyan   .dot { background: var(--cyan);    box-shadow: 0 0 8px var(--cyan); }
  .pill.down   .dot { background: #FB7185;          box-shadow: 0 0 8px #FB7185; }
  .pill.down   { color: #FDA4AF; border-color: rgba(251,113,133,0.35); }

  /* ---------- sidebar ---------- */
  [data-testid="stSidebar"] {
    background: rgba(13,13,23,0.72);
    backdrop-filter: blur(26px) saturate(150%);
    -webkit-backdrop-filter: blur(26px) saturate(150%);
    border-right: 1px solid var(--edge);
  }
  [data-testid="stSidebar"] [data-testid="stVerticalBlock"] > div {
    background: transparent;
  }

  /* ---------- chat ---------- */
  [data-testid="stChatMessage"] {
    background: var(--glass);
    border: 1px solid var(--edge);
    border-radius: 18px;
    padding: 0.85rem 1rem;
    margin-bottom: 0.75rem;
    backdrop-filter: blur(18px) saturate(140%);
    -webkit-backdrop-filter: blur(18px) saturate(140%);
    box-shadow: 0 6px 24px rgba(0,0,0,0.35);
  }
  /* assistant glows violet, user glows cyan */
  [data-testid="stChatMessage"]:has(.voice) {
    border-color: rgba(167,139,250,0.32);
    box-shadow: 0 6px 30px rgba(124,58,237,0.22);
  }
  [data-testid="stChatMessage"]:not(:has(.voice)) {
    border-color: rgba(34,211,238,0.26);
    box-shadow: 0 6px 30px rgba(34,211,238,0.14);
  }
  [data-testid="stChatMessage"] [data-testid="stChatMessageAvatar"] {
    display: none;
  }
  [data-testid="stChatMessage"] [data-testid="stChatMessageContent"] { gap: 0.5rem; }

  .voice {
    display: inline-block;
    font-size: 0.62rem;
    font-weight: 700;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    color: var(--violet-l);
    margin-bottom: 0.3rem;
    text-shadow: 0 0 14px rgba(167,139,250,0.6);
  }

  /* ---------- wire log ---------- */
  .wire {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.73rem;
    line-height: 1.6;
    color: #D6D6EC;
    background: rgba(34,211,238,0.06);
    border-left: 2px solid var(--cyan);
    border-radius: 0 10px 10px 0;
    padding: 0.4rem 0.7rem;
    margin: 0.15rem 0;
    box-shadow: inset 0 0 22px rgba(34,211,238,0.05);
  }
  .wire b { color: var(--cyan); font-weight: 500; }

  /* ---------- composer ---------- */
  [data-testid="stChatInput"] {
    background: var(--glass-2);
    border: 1px solid var(--edge-hi);
    border-radius: 999px;
    padding: 0.3rem 0.4rem;
    backdrop-filter: blur(22px) saturate(150%);
    -webkit-backdrop-filter: blur(22px) saturate(150%);
    box-shadow: 0 8px 32px rgba(0,0,0,0.5), 0 0 0 1px rgba(124,58,237,0.14);
    transition: box-shadow 0.25s ease, border-color 0.25s ease;
  }
  [data-testid="stChatInput"]:focus-within {
    border-color: rgba(167,139,250,0.55);
    box-shadow: 0 8px 34px rgba(0,0,0,0.5), 0 0 28px rgba(124,58,237,0.35);
  }
  [data-testid="stChatInput"] textarea { background: transparent; }
  [data-testid="stChatInput"] button {
    background: linear-gradient(135deg, #7C3AED, #22D3EE);
    border-radius: 999px;
    border: none;
    box-shadow: 0 0 18px rgba(124,58,237,0.5);
  }

  /* ---------- widgets ---------- */
  .section-label {
    font-size: 0.68rem;
    font-weight: 700;
    letter-spacing: 0.16em;
    text-transform: uppercase;
    color: #7A7A9C;
    margin: 0.3rem 0 0.5rem;
  }

  .stButton > button,
  [data-testid="stBaseButton-primary"],
  [data-testid="stBaseButton-secondary"] {
    border-radius: 999px;
    border: 1px solid var(--edge);
    background: var(--glass-2);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    font-weight: 600;
    letter-spacing: 0.01em;
    box-shadow: none;
    transition: transform 0.18s ease, box-shadow 0.18s ease, border-color 0.18s ease;
  }
  .stButton > button:hover,
  [data-testid="stBaseButton-primary"]:hover,
  [data-testid="stBaseButton-secondary"]:hover {
    transform: translateY(-1px);
    border-color: rgba(167,139,250,0.6);
    box-shadow: 0 0 22px rgba(124,58,237,0.35);
    color: #FFFFFF;
  }
  [data-testid="stBaseButton-primary"] {
    background: linear-gradient(135deg, #7C3AED, #5B21B6);
    border-color: transparent;
  }

  [data-testid="stTextInput"] input,
  [data-testid="stTextArea"] textarea {
    background: var(--glass);
    border-radius: 12px;
    border: 1px solid var(--edge);
  }

  [data-testid="stExpander"] {
    border: 1px solid var(--edge);
    border-radius: 14px;
    background: rgba(255,255,255,0.03);
    overflow: hidden;
  }
  [data-testid="stExpander"] summary:hover { color: var(--violet-l); }

  [data-testid="stStatusWidget"] details {
    border-radius: 999px;
    border: 1px solid var(--edge);
    background: var(--glass);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
  }

  /* suggestion chips */
  [data-testid="stBaseButton-secondary"] span p { font-weight: 500; }

  /* ---------- scrollbar ---------- */
  ::-webkit-scrollbar { width: 10px; height: 10px; }
  ::-webkit-scrollbar-track { background: transparent; }
  ::-webkit-scrollbar-thumb {
    background: linear-gradient(180deg, #7C3AED, #22D3EE);
    border-radius: 999px;
    border: 2px solid transparent;
    background-clip: padding-box;
  }
  ::-webkit-scrollbar-thumb:hover { background: linear-gradient(180deg, #A78BFA, #67E8F9); background-clip: padding-box; }

  ::selection { background: rgba(124,58,237,0.45); color: #fff; }

  /* respect users who don't want motion */
  @media (prefers-reduced-motion: reduce) {
    .aurora span { animation: none !important; }
    * { transition: none !important; }
  }
</style>

<div class="aurora" aria-hidden="true">
  <span class="a1"></span>
  <span class="a2"></span>
  <span class="a3"></span>
  <span class="a4"></span>
</div>
"""
)

# ---------------------------------------------------------------- helpers

ICON_FOR = {
    "get_weather": "thermostat",
    "get_city_news": "article",
}

SCOPE_HINT = {
    "News only": "Call get_city_news. Do not call get_weather.",
    "Weather only": "Call get_weather. Do not call get_city_news.",
    "News and weather": "Call get_city_news and get_weather.",
}

SUGGESTIONS = {
    "Weather and news for Bengaluru":
        "Give me the weather and the latest news for Bengaluru.",
    "Just the weather in Chennai":
        "What is the weather like in Chennai right now?",
    "News only for Mumbai":
        "What is happening in Mumbai? I only want the news.",
}


def text_of(message) -> str:
    content = message.content
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return "".join(
            block.get("text", "")
            for block in content
            if isinstance(block, dict) and block.get("type") == "text"
        )
    return ""


def wire_log(steps: list[dict]) -> None:
    for step in steps:
        icon = ICON_FOR.get(step["name"], "bolt")
        st.markdown(
            f'<div class="wire">'
            f'<b>{icon} {step["name"]}</b>'
            f'&nbsp;&rarr;&nbsp;{step["args"].get("city", "?")}'
            f'</div>',
            unsafe_allow_html=True,
        )
        if step.get("result"):
            with st.expander("Raw response", icon=":material/visibility:"):
                st.code(step["result"], language=None)


def render_turn(turn: dict) -> None:
    with st.chat_message(turn["role"]):
        if turn["role"] == "assistant":
            st.markdown(
                '<div class="voice">Meridian</div>',
                unsafe_allow_html=True,
            )
            st.markdown(turn["content"])
        else:
            st.markdown(turn["content"])
            if turn.get("scope"):
                st.caption(turn["scope"])

        steps = turn.get("steps") or []
        if steps:
            with st.status(
                f"{len(steps)} tool call{'s' if len(steps) > 1 else ''}",
                type="compact",
                state="complete",
                expanded=True,
            ):
                wire_log(steps)


def to_history(turns: list[dict]) -> list:
    history = []
    for turn in turns:
        if turn["role"] == "user":
            history.append(HumanMessage(content=turn["content"]))
        else:
            history.append(AIMessage(content=turn["content"]))
    return history


# ---------------------------------------------------------------- sidebar

missing = tools.missing_keys()
online = not missing

with st.sidebar:
    if st.button(
        "New conversation",
        icon=":material/add:",
        type="primary",
        width="stretch",
    ):
        for key in ("turns", "agent"):
            st.session_state.pop(key, None)
        st.rerun()

    st.space("small")

    scope = st.segmented_control(
        "What to fetch",
        ["News only", "Weather only", "News and weather"],
        default="News and weather",
        key="scope",
    )
    temperature = st.slider(
        "Temperature", 0.0, 1.0, 0.0, 0.1, key="temperature"
    )
    show_wire = st.toggle("Show tool calls", value=True, key="show_wire")

    st.space("medium")

    st.caption(
        "**Model** `openai/gpt-oss-20b` via Groq  \n"
        "**Tools** `get_weather`, `get_city_news`"
    )

# ---------------------------------------------------------------- hero

def service_pill(name: str, state: str, tone: str) -> str:
    cls = "pill" if state else "pill down"
    return (
        f'<span class="{cls} {tone}">'
        f'<span class="dot"></span>{name}</span>'
    )


status_line = "".join(
    [
        service_pill("Groq", online, "violet"),
        service_pill("OpenWeather", online, "cyan"),
        service_pill("Tavily", online, "cyan"),
    ]
)

st.html(
    f"""
<div class="glass hero">
  <h1>City desk</h1>
  <p>Live weather and breaking news for any city, gathered by an agent that
     calls real tools and shows its work.</p>
  <div class="tagrow">{status_line}</div>
</div>
"""
)

if missing:
    st.error(
        "Missing keys in .env: " + ", ".join(missing),
        icon=":material/key:",
    )

# ---------------------------------------------------------------- state

st.session_state.setdefault("turns", [])
st.session_state.setdefault("agent", None)

# ---------------------------------------------------------------- history

for turn in st.session_state.turns:
    render_turn(turn)

# ---------------------------------------------------------------- suggestions

if not st.session_state.turns:
    st.html(
        '<div class="section-label">Try one of these</div>'
    )
    picked = st.pills(
        "Try one of these",
        list(SUGGESTIONS.keys()),
        label_visibility="collapsed",
        key="suggestions",
    )
    if picked:
        st.session_state.turns.append(
            {"role": "user", "content": SUGGESTIONS[picked]}
        )
        st.rerun()
    st.space("medium")

# ---------------------------------------------------------------- composer

prompt = st.chat_input("Ask about any city", key="composer")

if prompt and not missing:
    st.session_state.turns.append(
        {"role": "user", "content": prompt, "scope": scope}
    )
    render_turn(st.session_state.turns[-1])

    if st.session_state.agent is None:
        with st.spinner("Connecting to Groq..."):
            st.session_state.agent = tools.build_agent(temperature)

    agent = st.session_state.agent

    history = to_history(st.session_state.turns[:-1])

    instruction = (
        f"{prompt}\n\n"
        f"Scope for this request: {scope or 'News and weather'}. "
        f"{SCOPE_HINT.get(scope or 'News and weather', '')}"
    )

    steps: list[dict] = []
    started = time.perf_counter()

    with st.chat_message("assistant"):
        st.markdown(
            '<div class="voice">Meridian</div>',
            unsafe_allow_html=True,
        )
        status_box = (
            st.status(":shimmer[Composing]", type="compact")
            if show_wire
            else None
        )

        def run():
            for mode, payload in agent.stream(
                {
                    "messages": [
                        *history,
                        HumanMessage(content=instruction),
                    ]
                },
                {"recursion_limit": 25},
                stream_mode=["messages", "updates"],
            ):
                if mode == "updates":
                    for update in payload.values():
                        for message in update.get("messages") or []:
                            for call in getattr(
                                message, "tool_calls", None
                            ) or []:
                                steps.append(
                                    {
                                        "id": call["id"],
                                        "name": call["name"],
                                        "args": call.get("args", {}),
                                        "result": None,
                                    }
                                )
                                # progress shows in the label; the full wire
                                # log is rendered once, after streaming, so the
                                # live view matches the replayed view exactly
                                status_box.update(
                                    label=f":shimmer[Calling "
                                    f"{call['name']}]",
                                    state="running",
                                )

                            if isinstance(message, ToolMessage):
                                for step in steps:
                                    if step["id"] == getattr(
                                        message, "tool_call_id", None
                                    ):
                                        step["result"] = text_of(message)
                else:
                    chunk = payload[0]
                    # "messages" mode also emits ToolMessage chunks —
                    # only the model's own text belongs in the answer.
                    if isinstance(chunk, AIMessageChunk):
                        piece = text_of(chunk)
                        if piece:
                            yield piece

        if not show_wire:
            with st.spinner("Composing..."):
                answer = agent.invoke(
                    {
                        "messages": [
                            *history,
                            HumanMessage(content=instruction),
                        ]
                    },
                    {"recursion_limit": 25},
                )
                final = text_of(answer["messages"][-1])
            st.write(final)
        else:
            final = st.write_stream(run())

            elapsed = time.perf_counter() - started
            with status_box:
                if steps:
                    wire_log(steps)
                status_box.update(
                    label=(
                        f"{len(steps)} tool call"
                        f"{'s' if len(steps) > 1 else ''} in {elapsed:.1f}s"
                        if steps
                        else f"Answered in {elapsed:.1f}s"
                    ),
                    state="complete",
                    expanded=True,
                )

    st.session_state.turns.append(
        {"role": "assistant", "content": final, "steps": steps}
    )
