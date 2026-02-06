import asyncio
import os
import sys
import time

import pandas as pd
import plotly.express as px
import streamlit as st

# Ensure project root is in path
sys.path.append(os.getcwd())

from src.benchmarks.engine import BenchmarkEngine
from src.core.database import get_db_stats
from src.servers.manager import SERVER_MAP, ServerManager

st.set_page_config(
    page_title="Protocol Battle Arena",
    layout="wide",
    page_icon="⚔️",
    initial_sidebar_state="expanded",
)

# Custom Styling for "Visual Excellence"
st.markdown(
    """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&family=Inter:wght@300;400;600&display=swap');

    .main {
        background: radial-gradient(circle at top right, #1e293b, #0f172a);
        color: #f8fafc;
        font-family: 'Inter', sans-serif;
    }
    
    .stApp {
        background: transparent;
    }

    [data-testid="stHeader"] {
        background: rgba(15, 23, 42, 0.8);
        backdrop-filter: blur(10px);
    }

    .stMetric {
        background: rgba(30, 41, 59, 0.5);
        backdrop-filter: blur(16px);
        padding: 20px;
        border-radius: 12px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        box-shadow: 0 4px 30px rgba(0, 0, 0, 0.1);
    }
    
    h1 {
        font-family: 'Orbitron', sans-serif;
        background: linear-gradient(90deg, #60a5fa, #a855f7);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        letter-spacing: 2px;
        text-transform: uppercase;
        font-weight: 700;
        margin-bottom: 30px !important;
    }

    .status-active {
        color: #4ade80;
        font-weight: 600;
        text-shadow: 0 0 10px rgba(74, 222, 128, 0.3);
    }

    .status-offline {
        color: #f87171;
        opacity: 0.7;
    }

    /* Tabs styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
        background-color: transparent;
    }

    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: transparent;
        border-radius: 4px 4px 0px 0px;
        color: #94a3b8;
        font-weight: 600;
    }

    .stTabs [aria-selected="true"] {
        color: #60a5fa !important;
        border-bottom-color: #60a5fa !important;
    }

    /* Buttons */
    .stButton > button {
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.3s ease;
    }

    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(96, 165, 250, 0.2);
    }
</style>
""",
    unsafe_allow_html=True,
)

st.title("⚔️ Protocol Battle Arena")
st.markdown("---")

# Initialize Session State
if "active_servers" not in st.session_state:
    st.session_state.active_servers = set()

# --- Sidebar: Server Control ---
st.sidebar.title("🕹️ Control Tower")

for protocol, cfg in SERVER_MAP.items():
    with st.sidebar.container():
        is_open = ServerManager.is_port_open(cfg["port"])

        col1, col2 = st.columns([3, 1])
        col1.markdown(f"**{protocol}** (:{cfg['port']})")

        # Determine current state for toggle
        default_state = protocol in st.session_state.active_servers or is_open

        toggle = col2.toggle("", value=default_state, key=f"tg_{protocol}")

        if toggle:
            if not is_open:
                with st.sidebar:
                    with st.spinner(f"Igniting {protocol}..."):
                        ServerManager.start(protocol)
                        st.session_state.active_servers.add(protocol)
                        time.sleep(1)  # Small delay for port bind
                        st.rerun()

            # Show Stats if active
            stats = ServerManager.get_stats(protocol)
            if stats:
                st.sidebar.markdown(
                    f"<span class='status-active'>●</span> **Active** | CPU: **{stats['cpu']:.1f}%** | RAM: **{stats['memory_mb']:.1f}MB**",
                    unsafe_allow_html=True,
                )
            else:
                st.sidebar.caption("🟡 Searching for PID...")
        else:
            if is_open:
                with st.sidebar:
                    with st.spinner(f"Quenching {protocol}..."):
                        ServerManager.stop(protocol)
                        if protocol in st.session_state.active_servers:
                            st.session_state.active_servers.remove(protocol)
                        st.rerun()
            st.sidebar.markdown(
                "<span class='status-offline'>○</span> *Stationary*",
                unsafe_allow_html=True,
            )

# --- Main Dashboard ---
total_rows = asyncio.run(get_db_stats())

# --- Main Dashboard ---
total_rows = asyncio.run(get_db_stats())

st.markdown("### 📊 Global Arena Status")
col_stat1, col_stat2, col_stat3 = st.columns(3)
with col_stat1:
    st.metric("📦 Database Size", f"{total_rows:,} logs")
with col_stat2:
    active_count = len(
        [p for p in SERVER_MAP if ServerManager.is_port_open(SERVER_MAP[p]["port"])]
    )
    st.metric(
        "📡 Systems Online",
        active_count,
        delta=f"{active_count}/5",
        delta_color="normal",
    )
with col_stat3:
    st.metric("⚙️ CPU Pressure", f"{os.getloadavg()[0]:.2f}", delta="Load Avg")

st.markdown("<br>", unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(
    ["📊 Performance Bench", "⚡ Stress Testing", "🛠️ Engineering"]
)

with tab1:
    st.subheader("Latency Distribution (TTFB)")

    col_ctrl1, col_ctrl2 = st.columns([1, 4])
    num_reqs = col_ctrl1.number_input("Request Count", 10, max(total_rows, 1000000), 50)

    active_now = [
        p for p in SERVER_MAP if ServerManager.is_port_open(SERVER_MAP[p]["port"])
    ]

    if col_ctrl1.button("🚀 Start Benchmark", disabled=not active_now, type="primary"):
        engine = BenchmarkEngine()
        all_data = []

        with st.status("⚔️ Benchmarking...", expanded=True) as status:
            progress = st.progress(0)
            for i, p in enumerate(active_now):
                status.write(f"Testing {p}...")
                df = asyncio.run(
                    engine.run_latency_test(p, SERVER_MAP[p]["port"], n=num_reqs)
                )
                df["Protocol"] = p
                all_data.append(df)
                progress.progress((i + 1) / len(active_now))
            status.update(label="✅ Test Complete", state="complete")

        if all_data:
            final_df = pd.concat(all_data)
            fig = px.box(
                final_df,
                x="Protocol",
                y="Latency (ms)",
                color="Protocol",
                points="all",
                title="Protocol Latency Battle",
                template="plotly_dark",
            )
            st.plotly_chart(fig, use_container_width=True)

            st.markdown("#### Performance Summary")
            st.dataframe(
                final_df.groupby("Protocol")["Latency (ms)"].describe(),
                use_container_width=True,
            )

with tab2:
    st.subheader("Throughput Siege (RPS)")

    col_siege1, col_siege2 = st.columns([1, 4])
    siege_dur = col_siege1.slider("Duration (s)", 1, 10, 3)

    if col_siege1.button("💥 Launch Siege", disabled=not active_now, type="primary"):
        engine = BenchmarkEngine()
        rps_results = {}

        with st.status("🌪️ Sieging Servers...") as status:
            chart_spot = st.empty()
            for p in active_now:
                status.write(f"Saturation Test: {p}...")
                rps = asyncio.run(
                    engine.run_throughput_test(
                        p, SERVER_MAP[p]["port"], duration_sec=siege_dur
                    )
                )
                rps_results[p] = rps

                # Dynamic update
                res_df = pd.DataFrame(
                    list(rps_results.items()), columns=["Protocol", "RPS"]
                )
                fig = px.bar(
                    res_df,
                    x="Protocol",
                    y="RPS",
                    color="Protocol",
                    title="Requests Per Second Comparison",
                    template="plotly_dark",
                )
                chart_spot.plotly_chart(fig, use_container_width=True)
            status.update(label="🏁 Siege Finished", state="complete")

with tab3:
    st.subheader("Arena Maintenance")
    if st.button("🔄 Clean Re-Seed (100k Rows)"):
        with st.spinner("Processing..."):
            os.system("PYTHONPATH=. uv run python src/scripts/generate.py")
            st.success("Database Re-Hydrated!")
            st.rerun()

    st.markdown(
        """
    #### Architectural Notes
    - **REST**: FastAPI + SQLAlchemy (JSON over HTTP/1.1)
    - **GraphQL**: Strawberry + FastAPI (Flexible queries)
    - **gRPC**: HTTP/2 + Protobuf (Binary serialization)
    - **SSE**: Server-Sent Events (One-way streaming)
    - **WS**: WebSockets (Full-duplex streaming)
    """
    )

st.sidebar.markdown("---")
if st.sidebar.button("🛑 Force Stop All Servers"):
    ServerManager.stop_all()
    st.rerun()
