import streamlit as st
import pandas as pd
import plotly.express as px

from scheduler import calculate_machine_plan
from simulator import FactorySimulator
from what_if import calculate_plan_metrics, calculate_savings
from order_scheduler import generate_schedule
from machine_health import get_machine_risks, get_numeric_machine_risks


# ============================================================
# GLASSMORPHISM UI THEME — VISUAL ONLY
# ============================================================
st.markdown("""
<style>
/* ---------- App background ---------- */
.stApp {
    background:
        radial-gradient(circle at 10% 10%, rgba(99,102,241,.18), transparent 28%),
        radial-gradient(circle at 90% 8%, rgba(14,165,233,.16), transparent 26%),
        radial-gradient(circle at 80% 90%, rgba(168,85,247,.13), transparent 30%),
        linear-gradient(135deg, #07111f 0%, #0b1324 48%, #101827 100%);
    color: #edf4ff;
}

.stApp > header {
    background: transparent !important;
}

.main .block-container {
    max-width: 1500px;
    padding-top: 2rem;
    padding-bottom: 4rem;
}

/* ---------- Global typography ---------- */
h1, h2, h3 {
    letter-spacing: -0.025em;
}

h1 {
    font-weight: 800 !important;
    text-shadow: 0 8px 30px rgba(56,189,248,.14);
}

h2, h3 {
    font-weight: 750 !important;
}

/* ---------- Glass containers ---------- */
div[data-testid="stVerticalBlockBorderWrapper"],
div[data-testid="stExpander"],
div[data-testid="stMetric"],
div[data-testid="stAlert"],
div[data-testid="stDataFrame"],
div[data-testid="stPlotlyChart"],
div[data-testid="stElementContainer"] .stMarkdown {
    border-radius: 18px;
}

div[data-testid="stMetric"] {
    background: rgba(255,255,255,.055);
    border: 1px solid rgba(255,255,255,.10);
    box-shadow: 0 12px 35px rgba(0,0,0,.20);
    backdrop-filter: blur(18px);
    -webkit-backdrop-filter: blur(18px);
    padding: 10px 14px;
    transition: transform .2s ease, border-color .2s ease, box-shadow .2s ease;
}

div[data-testid="stMetric"]:hover {
    transform: translateY(-2px);
    border-color: rgba(125,211,252,.30);
    box-shadow: 0 18px 42px rgba(0,0,0,.28);
}

div[data-testid="stMetricLabel"] {
    color: #9fb2ca !important;
}

div[data-testid="stMetricValue"] {
    color: #f5f9ff !important;
    font-weight: 800;
}

/* ---------- Sidebar ---------- */
section[data-testid="stSidebar"] {
    background:
        linear-gradient(180deg, rgba(10,20,36,.92), rgba(7,14,27,.96));
    border-right: 1px solid rgba(255,255,255,.10);
    box-shadow: 18px 0 45px rgba(0,0,0,.18);
}

section[data-testid="stSidebar"] > div {
    background: transparent;
}

section[data-testid="stSidebar"] .stButton > button,
section[data-testid="stSidebar"] .stRadio > div {
    border-radius: 14px;
}

/* ---------- Buttons ---------- */
.stButton > button {
    border: 1px solid rgba(125,211,252,.22);
    border-radius: 13px;
    background: linear-gradient(135deg, rgba(59,130,246,.24), rgba(99,102,241,.16));
    color: #f5f9ff;
    font-weight: 700;
    box-shadow: 0 8px 25px rgba(0,0,0,.16);
    backdrop-filter: blur(14px);
    transition: all .2s ease;
}

.stButton > button:hover {
    border-color: rgba(125,211,252,.55);
    background: linear-gradient(135deg, rgba(59,130,246,.38), rgba(99,102,241,.28));
    transform: translateY(-1px);
    box-shadow: 0 12px 30px rgba(37,99,235,.18);
}

/* ---------- Inputs ---------- */
div[data-baseweb="select"] > div,
div[data-baseweb="input"] > div,
div[data-testid="stNumberInput"] > div,
div[data-testid="stTextInput"] > div {
    background: rgba(255,255,255,.055) !important;
    border: 1px solid rgba(255,255,255,.12) !important;
    border-radius: 12px !important;
    backdrop-filter: blur(12px);
}

div[data-baseweb="select"] > div:hover,
div[data-baseweb="input"] > div:hover {
    border-color: rgba(125,211,252,.38) !important;
}

/* ---------- Alerts ---------- */
div[data-testid="stAlert"] {
    border: 1px solid rgba(255,255,255,.10);
    box-shadow: 0 10px 28px rgba(0,0,0,.14);
    backdrop-filter: blur(14px);
}

/* ---------- Expanders ---------- */
div[data-testid="stExpander"] {
    background: rgba(255,255,255,.045);
    border: 1px solid rgba(255,255,255,.10);
    box-shadow: 0 12px 30px rgba(0,0,0,.14);
    backdrop-filter: blur(16px);
}

/* ---------- Dataframe ---------- */
div[data-testid="stDataFrame"] {
    overflow: hidden;
    border: 1px solid rgba(255,255,255,.10);
    box-shadow: 0 14px 35px rgba(0,0,0,.18);
}

/* ---------- Plotly charts ---------- */
div[data-testid="stPlotlyChart"] {
    background: rgba(255,255,255,.035);
    border: 1px solid rgba(255,255,255,.08);
    padding: 8px;
    box-shadow: 0 14px 35px rgba(0,0,0,.16);
}

/* ---------- Dividers ---------- */
hr {
    border: 0 !important;
    height: 1px !important;
    background: linear-gradient(
        90deg,
        transparent,
        rgba(148,163,184,.30),
        transparent
    ) !important;
    margin: 1.5rem 0 !important;
}

/* ---------- Radio navigation ---------- */
section[data-testid="stSidebar"] [role="radiogroup"] label {
    border-radius: 12px;
    padding: 7px 10px;
    transition: background .2s ease;
}

section[data-testid="stSidebar"] [role="radiogroup"] label:hover {
    background: rgba(255,255,255,.06);
}

/* ---------- Subtle glass sheen ---------- */
.main .block-container::before {
    content: "";
    position: fixed;
    top: 0;
    left: 18%;
    width: 45vw;
    height: 14rem;
    background: radial-gradient(
        ellipse,
        rgba(125,211,252,.08),
        transparent 68%
    );
    pointer-events: none;
    z-index: -1;
}

/* ---------- Mobile refinement ---------- */
@media (max-width: 900px) {
    .main .block-container {
        padding-left: 1rem;
        padding-right: 1rem;
    }
    h1 {
        font-size: 2rem !important;
    }
}
</style>
""", unsafe_allow_html=True)

st.set_page_config(
    page_title="FactoryMind AI",
    page_icon="🏭",
    layout="wide",
)

# ============================================================
# FACTORYMIND AI — SIDEBAR
# ============================================================

with st.sidebar:

    st.title("🏭 FactoryMind AI")

    st.caption(
        "Autonomous Smart Manufacturing"
    )

    st.divider()

    page = st.radio(
        "Navigation",
        [
            "📊 Dashboard",
            "🧠 AI Scheduler",
            "🏭 Digital Twin",
            "🔧 Machine Health",
            "🔮 What-If Simulator",
            "📈 AI Impact",
        ],
    )

    st.divider()

    st.caption(
        "Prototype • Yuva Yodha Hackathon 2026"
    )

# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="FactoryMind AI",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# FACTORY DATA
# ============================================================

machines = {
    "M1": {
        "production": 20,
        "energy": 30,
        "risk": 5,
    },
    "M2": {
        "production": 50,
        "energy": 90,
        "risk": 10,
    },
    "M3": {
        "production": 25,
        "energy": 35,
        "risk": 7,
    },
}


# ============================================================
# SESSION STATE
# ============================================================

def initialize_session_state():

    defaults = {
        "simulation_data": [],
        "factory": None,
        "active_machines": [],
        "last_plan": None,
        "order_result": None,
        "demo_loaded": False,
        "order_quantity": 300,
        "deadline_hours": 8,
    }

    for key, value in defaults.items():

        if key not in st.session_state:
            st.session_state[key] = value

    if st.session_state.factory is None:
        st.session_state.factory = FactorySimulator(machines)


initialize_session_state()


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def load_demo_values():
    """
    Load a repeatable hackathon demo scenario.
    """

    st.session_state.order_quantity = 300
    st.session_state.deadline_hours = 8

    demo_grid = [
        "Low",
        "Low",
        "Medium",
        "High",
        "High",
        "Medium",
        "Low",
        "Low",
    ]

    for index, demand in enumerate(demo_grid):

        st.session_state[
            f"grid_select_{index}"
        ] = demand

    st.session_state.demo_loaded = True
    st.session_state.order_result = None


def reset_factory():

    st.session_state.factory = FactorySimulator(machines)

    st.session_state.simulation_data = []

    st.session_state.active_machines = []

    st.session_state.last_plan = None

    st.session_state.order_result = None

    st.session_state.demo_loaded = False


def show_machine_plan(plan, current_grid):

    selected = " + ".join(
        plan["machines"]
    )

    st.success(
        f"🤖 AI Selected: **{selected}**"
    )

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        "Production",
        f"{plan['production']} units/hr",
    )

    c2.metric(
        "Energy",
        f"{plan['energy']} kWh",
    )

    c3.metric(
        "Base Risk",
        f"{plan['risk']}%",
    )

    c4.metric(
        "Grid",
        current_grid,
    )

    st.info(
        f"""
**AI reasoning**

Current grid demand is **{current_grid}**.

The scheduler evaluated possible machine combinations and selected
**{selected}** to satisfy the production target while considering
energy use, machine risk and excess production.
"""
    )


# ============================================================
# HEADER
# ============================================================

st.title("🏭 FactoryMind AI")

st.subheader(
    "AI Digital Twin + Autonomous Production Scheduler"
)

st.write(
    "A software-only intelligent factory simulator that dynamically "
    "optimizes machine operation using production requirements, "
    "grid demand, energy consumption, machine risk and deadlines."
)

st.caption(
    "🎯 Hackathon concept: simulate how a smart factory can adapt "
    "production scheduling to changing grid conditions without "
    "controlling the physical grid."
)

st.divider()


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.header("⚙️ Factory Controls")


production_target = st.sidebar.slider(
    "Production Target (units/hour)",
    min_value=10,
    max_value=100,
    value=40,
    step=5,
)


grid_demand = st.sidebar.select_slider(
    "Current Grid Demand",
    options=[
        "Low",
        "Medium",
        "High",
    ],
    value="Medium",
)


st.sidebar.divider()


run_ai = st.sidebar.button(
    "🤖 Run AI Scheduler",
    use_container_width=True,
)


run_simulation = st.sidebar.button(
    "▶️ Run Simulation Step",
    use_container_width=True,
)


reset_button = st.sidebar.button(
    "🔄 Reset Factory",
    use_container_width=True,
)


if reset_button:

    reset_factory()

    st.rerun()


# ============================================================
# TOP KPI STATUS
# ============================================================

st.header("📊 Factory Status")


k1, k2, k3, k4 = st.columns(4)


k1.metric(
    "Grid Demand",
    grid_demand,
)


k2.metric(
    "Production Target",
    f"{production_target} units/hr",
)


k3.metric(
    "Simulation Time",
    f"{st.session_state.factory.time_elapsed} hr",
)


k4.metric(
    "Active Machines",
    len(
        st.session_state.active_machines
    ),
)


# ============================================================
# MACHINE AI SCHEDULER
# ============================================================

if run_ai:

    plan = calculate_machine_plan(
        machines,
        production_target,
        grid_demand,
    )

    if plan is None:

        st.error(
            "❌ No machine combination can satisfy "
            "the current production target."
        )

        st.session_state.active_machines = []

        st.session_state.last_plan = None

    else:

        st.session_state.active_machines = list(
            plan["machines"]
        )

        st.session_state.last_plan = plan


st.divider()

st.header(
    "🤖 Machine AI Recommendation"
)


if st.session_state.last_plan is not None:

    show_machine_plan(
        st.session_state.last_plan,
        grid_demand,
    )

else:

    st.info(
        "Click **Run AI Scheduler** "
        "to generate a machine plan."
    )


# ============================================================
# DIGITAL TWIN — VIRTUAL FACTORY
# ============================================================

st.divider()

st.header("🏭 Digital Twin — Virtual Factory")

st.write(
    "FactoryMind AI creates a virtual representation of the factory "
    "and continuously shows which machines are operating, their "
    "energy usage and predicted health risk."
)


# ------------------------------------------------------------
# Get latest machine health information
# ------------------------------------------------------------

try:
    digital_twin_risks = get_machine_risks()

except Exception:
    digital_twin_risks = {}


# ------------------------------------------------------------
# Factory Floor
# ------------------------------------------------------------

st.subheader("🏭 Factory Floor")


factory_columns = st.columns(3)


for index, (
    machine_name,
    machine
) in enumerate(machines.items()):

    with factory_columns[index]:

        # Check whether AI selected this machine
        is_running = (
            machine_name
            in st.session_state.active_machines
        )


        # Get ML risk
        health = digital_twin_risks.get(
            machine_name,
            {
                "risk": 0.0,
                "label": "Unknown",
            },
        )


        risk = health.get(
            "risk",
            0.0,
        )

        risk_label = health.get(
            "label",
            "Unknown",
        )


        # ----------------------------------------------------
        # Machine Header
        # ----------------------------------------------------

        if is_running:

            st.success(
                f"🟢 {machine_name} — RUNNING"
            )

        else:

            st.error(
                f"🔴 {machine_name} — OFF"
            )


        # ----------------------------------------------------
        # Machine Metrics
        # ----------------------------------------------------

        st.metric(
            "Production Capacity",
            f"{machine['production']} units/hr",
        )


        st.metric(
            "Energy Consumption",
            f"{machine['energy']} kWh",
        )


        st.metric(
            "ML Breakdown Risk",
            f"{risk}%",
        )


        # ----------------------------------------------------
        # Risk Status
        # ----------------------------------------------------

        if risk_label == "Low":

            st.success(
                "🟢 Machine Health: Low Risk"
            )

        elif risk_label == "Medium":

            st.warning(
                "🟡 Machine Health: Medium Risk"
            )

        elif risk_label == "High":

            st.error(
                "🔴 Machine Health: High Risk"
            )

        else:

            st.info(
                "⚪ Machine Health: Unknown"
            )


# ------------------------------------------------------------
# AI Factory Decision
# ------------------------------------------------------------

st.divider()

st.subheader("🧠 AI Factory Decision")


if st.session_state.last_plan is not None:

    selected_machines = (
        st.session_state.last_plan["machines"]
    )

    selected_text = " + ".join(
        selected_machines
    )


    decision_col1, decision_col2, decision_col3 = (
        st.columns(3)
    )


    with decision_col1:

        st.metric(
            "AI Selected Machines",
            selected_text,
        )


    with decision_col2:

        st.metric(
            "Expected Production",
            f"{st.session_state.last_plan['production']} units/hr",
        )


    with decision_col3:

        st.metric(
            "Expected Energy",
            f"{st.session_state.last_plan['energy']} kWh",
        )


    st.info(
        f"""
🤖 **FactoryMind AI Decision**

The AI selected **{selected_text}**.

The decision considers:

• Production requirement  
• Current grid demand  
• Machine energy consumption  
• Machine operating risk  
• Production efficiency  

The selected machines are now represented in the
virtual factory above.
"""
    )

else:

    st.info(
        "Run the **AI Scheduler** to activate the "
        "Digital Twin machine selection."
    )


# ------------------------------------------------------------
# Factory Energy Overview
# ------------------------------------------------------------

st.divider()

st.subheader("⚡ Factory Energy Overview")


total_factory_energy = sum(
    machine["energy"]
    for machine in machines.values()
)


active_factory_energy = sum(
    machines[machine_name]["energy"]
    for machine_name
    in st.session_state.active_machines
)


energy_col1, energy_col2, energy_col3 = (
    st.columns(3)
)


energy_col1.metric(
    "Maximum Factory Energy",
    f"{total_factory_energy} kWh",
)


energy_col2.metric(
    "AI Selected Energy",
    f"{active_factory_energy} kWh",
)


if total_factory_energy > 0:

    energy_reduction = (
        (
            total_factory_energy
            - active_factory_energy
        )
        / total_factory_energy
    ) * 100

else:

    energy_reduction = 0


energy_col3.metric(
    "Energy Reduction",
    f"{energy_reduction:.1f}%",
)


# ------------------------------------------------------------
# Factory State Summary
# ------------------------------------------------------------

st.divider()

st.subheader("📡 Digital Twin Status")


status_col1, status_col2, status_col3, status_col4 = (
    st.columns(4)
)


status_col1.metric(
    "Total Machines",
    len(machines),
)


status_col2.metric(
    "Running",
    len(
        st.session_state.active_machines
    ),
)


status_col3.metric(
    "Stopped",
    len(machines)
    - len(
        st.session_state.active_machines
    ),
)


if st.session_state.active_machines:

    status_col4.success(
        "🟢 Factory Active"
    )

else:

    status_col4.warning(
        "⚪ Factory Idle"
    )

# ============================================================
# LIVE GRID ADAPTATION
# ============================================================

st.divider()

st.header("⚡ Live Grid Adaptation")

st.write(
    "FactoryMind AI continuously adapts factory production "
    "according to changing grid conditions."
)


grid_col1, grid_col2 = st.columns(2)


with grid_col1:

    live_grid = st.selectbox(
        "Current Grid Demand",
        [
            "Low",
            "Medium",
            "High",
        ],
        key="live_grid_demand",
    )


with grid_col2:

    live_target = st.number_input(
        "Production Target (units/hr)",
        min_value=1,
        max_value=200,
        value=50,
        step=5,
        key="live_production_target",
    )


# ------------------------------------------------------------
# Calculate AI response
# ------------------------------------------------------------

live_plan = calculate_machine_plan(
    machines,
    live_target,
    live_grid,
)


if live_plan:

    st.subheader("🤖 AI Response")


    live_col1, live_col2, live_col3, live_col4 = (
        st.columns(4)
    )


    with live_col1:

        st.metric(
            "Selected Machines",
            " + ".join(
                live_plan["machines"]
            ),
        )


    with live_col2:

        st.metric(
            "Production",
            f"{live_plan['production']} units/hr",
        )


    with live_col3:

        st.metric(
            "Energy",
            f"{live_plan['energy']} kWh",
        )


    with live_col4:

        st.metric(
            "Risk",
            f"{live_plan['risk']}%",
        )


    # --------------------------------------------------------
    # Grid response explanation
    # --------------------------------------------------------

    if live_grid == "Low":

        st.success(
            "🟢 Grid demand is low. "
            "AI can prioritise efficient production "
            "while meeting the target."
        )

    elif live_grid == "Medium":

        st.warning(
            "🟡 Grid demand is medium. "
            "AI is balancing production and energy usage."
        )

    else:

        st.error(
            "🔴 Grid demand is high. "
            "AI is applying stronger energy-saving "
            "pressure while maintaining the production target."
        )


    # --------------------------------------------------------
    # Machine status visualization
    # --------------------------------------------------------

    st.subheader("🏭 Live Factory State")


    live_machine_cols = st.columns(
        len(machines)
    )


    for index, machine_name in enumerate(
        machines
    ):

        with live_machine_cols[index]:

            if machine_name in live_plan["machines"]:

                st.success(
                    f"🟢 {machine_name}\n\n"
                    "AI: ACTIVE"
                )

            else:

                st.info(
                    f"⚪ {machine_name}\n\n"
                    "AI: STANDBY"
                )


    # --------------------------------------------------------
    # AI explanation
    # --------------------------------------------------------

    st.info(
        f"""
🧠 **FactoryMind AI Decision**

Grid condition: **{live_grid}**

Required production: **{live_target} units/hr**

AI selected:

**{" + ".join(live_plan["machines"])}**

Expected production:

**{live_plan["production"]} units/hr**

Expected energy:

**{live_plan["energy"]} kWh**

The scheduler evaluates possible machine combinations
instead of simply turning every machine ON.
"""
    )

else:

    st.error(
        "No machine combination can satisfy "
        "the requested production target."
    )

# ============================================================
# ML RISK-AWARE AI PRODUCTION SCHEDULER
# ============================================================

st.divider()

st.header("🧠 ML Risk-Aware Production Scheduler")

st.write(
    "FactoryMind AI combines machine health prediction "
    "with production scheduling to avoid unnecessary "
    "machine breakdown risk."
)


# ------------------------------------------------------------
# Inputs
# ------------------------------------------------------------

risk_col1, risk_col2 = st.columns(2)


with risk_col1:

    order_quantity = st.number_input(
        "Production Order Quantity",
        min_value=10,
        max_value=1000,
        value=300,
        step=10,
        key="risk_order_quantity",
    )


with risk_col2:

    deadline_hours = st.number_input(
        "Deadline (hours)",
        min_value=1,
        max_value=24,
        value=8,
        step=1,
        key="risk_deadline",
    )


st.subheader("⚡ Grid Demand Profile")

grid_profile = []

profile_cols = st.columns(
    min(deadline_hours, 8)
)

for hour in range(deadline_hours):

    column = profile_cols[
        hour % len(profile_cols)
    ]

    with column:

        demand = st.selectbox(
            f"Hour {hour + 1}",
            [
                "Low",
                "Medium",
                "High",
            ],
            key=f"risk_grid_{hour}",
        )

        grid_profile.append(demand)


# ------------------------------------------------------------
# Machine Health
# ------------------------------------------------------------

st.subheader("🔧 ML Machine Health")

machine_risk_data = get_machine_risks()

machine_risks = {
    machine: data["risk"]
    for machine, data
    in machine_risk_data.items()
}


health_cols = st.columns(
    len(machines)
)


for index, machine_name in enumerate(
    machines
):

    with health_cols[index]:

        risk = machine_risk_data[
            machine_name
        ]["risk"]

        label = machine_risk_data[
            machine_name
        ]["label"]


        st.metric(
            machine_name,
            f"{risk}%",
        )


        if label == "Low":

            st.success(
                "🟢 Low Risk"
            )

        elif label == "Medium":

            st.warning(
                "🟡 Medium Risk"
            )

        else:

            st.error(
                "🔴 High Risk"
            )


# ------------------------------------------------------------
# Generate AI Schedule
# ------------------------------------------------------------

if st.button(
    "🚀 Generate Risk-Aware AI Plan",
    key="generate_risk_plan",
):

    schedule_result = generate_schedule(
        machines=machines,
        order_quantity=order_quantity,
        deadline_hours=deadline_hours,
        grid_profile=grid_profile,
        machine_risks=machine_risks,
    )


    st.session_state[
        "risk_schedule"
    ] = schedule_result


# ------------------------------------------------------------
# Display Schedule
# ------------------------------------------------------------

if (
    "risk_schedule"
    in st.session_state
):

    result = st.session_state[
        "risk_schedule"
    ]


    if result["completed"]:

        st.success(
            "✅ Production order can be completed "
            "within the deadline."
        )

    else:

        st.error(
            "⚠️ Production order cannot be completed "
            "within the available capacity."
        )


    # --------------------------------------------------------
    # Overall KPIs
    # --------------------------------------------------------

    st.subheader(
        "📊 AI Production Plan"
    )


    kpi1, kpi2, kpi3, kpi4 = (
        st.columns(4)
    )


    kpi1.metric(
        "Total Production",
        f"{result['total_production']:.0f}",
    )


    kpi2.metric(
        "Total Energy",
        f"{result['total_energy']:.0f} kWh",
    )


    kpi3.metric(
        "Remaining",
        f"{result['remaining']:.0f}",
    )


    kpi4.metric(
        "Deadline",
        f"{deadline_hours} hrs",
    )


    # --------------------------------------------------------
    # Hour-by-hour schedule
    # --------------------------------------------------------

    st.subheader(
        "🗓️ Hour-by-Hour AI Schedule"
    )


    for row in result["schedule"]:

        machines_used = " + ".join(
            row["machines"]
        )


        with st.container():

            st.markdown(
                f"### Hour {row['hour']} — "
                f"{row['grid_demand']} Grid"
            )


            schedule_cols = st.columns(5)


            schedule_cols[0].metric(
                "Machines",
                machines_used,
            )


            schedule_cols[1].metric(
                "Production",
                f"{row['production']:.0f}",
            )


            schedule_cols[2].metric(
                "Energy",
                f"{row['energy']} kWh",
            )


            schedule_cols[3].metric(
                "ML Risk",
                f"{row['ml_risk']}%",
            )


            schedule_cols[4].metric(
                "Remaining",
                f"{row['remaining']:.0f}",
            )


            st.caption(
                f"🤖 {row['reason']}"
            )


    # --------------------------------------------------------
    # Final AI Explanation
    # --------------------------------------------------------

    st.info(
        """
🧠 **How FactoryMind AI makes the decision**

The scheduler evaluates different machine combinations.

For every possible combination it considers:

• Production capacity  
• Energy consumption  
• Grid demand  
• Existing machine risk  
• ML-predicted breakdown risk  
• Remaining production requirement  
• Deadline urgency  

The AI then selects the feasible plan with the
lowest overall optimisation score.
"""
    )


# ============================================================
# LIVE SIMULATION
# ============================================================

if run_simulation:

    if not st.session_state.active_machines:

        st.warning(
            "⚠️ Run the AI Scheduler first."
        )

    else:

        simulation_result = (
            st.session_state.factory.run_step(
                st.session_state.active_machines,
                duration=1,
            )
        )

        st.session_state.simulation_data.append(
            simulation_result
        )


st.divider()

st.header(
    "📈 Live Factory Simulation"
)


if st.session_state.simulation_data:

    simulation_df = pd.DataFrame(
        st.session_state.simulation_data
    )

    s1, s2, s3 = st.columns(3)

    s1.metric(
        "Total Production",
        f"{st.session_state.factory.total_production:.2f} units",
    )

    s2.metric(
        "Total Energy",
        f"{st.session_state.factory.total_energy:.2f} kWh",
    )

    s3.metric(
        "Simulation Hours",
        f"{st.session_state.factory.time_elapsed}",
    )


    production_chart = px.line(
        simulation_df,
        x="time",
        y="total_production",
        markers=True,
        title="Cumulative Production",
    )

    production_chart.update_layout(
        xaxis_title="Simulation Time (hours)",
        yaxis_title="Production (units)",
    )

    st.plotly_chart(
        production_chart,
        use_container_width=True,
    )


    energy_chart = px.line(
        simulation_df,
        x="time",
        y="total_energy",
        markers=True,
        title="Cumulative Energy Consumption",
    )

    energy_chart.update_layout(
        xaxis_title="Simulation Time (hours)",
        yaxis_title="Energy (kWh)",
    )

    st.plotly_chart(
        energy_chart,
        use_container_width=True,
    )

else:

    st.info(
        "No simulation data yet. Run the AI Scheduler "
        "and then click **Run Simulation Step**."
    )


# ============================================================
# AUTONOMOUS PRODUCTION ORDER AI
# ============================================================

st.divider()

st.header(
    "📦 Autonomous Production Order AI"
)

st.write(
    "Give the factory an order and a deadline. "
    "FactoryMind AI creates an hour-by-hour production "
    "strategy while considering changing grid demand "
    "and predicted machine breakdown risk."
)


demo_col1, demo_col2 = st.columns(
    [1, 3]
)


with demo_col1:

    if st.button(
        "🎬 Load Demo Scenario",
        use_container_width=True,
    ):

        load_demo_values()

        st.rerun()


with demo_col2:

    st.caption(
        "Demo: 300 units in 8 hours with changing "
        "grid demand from Low → Medium → High → Low."
    )


# ============================================================
# ORDER INPUTS
# ============================================================

order_col1, order_col2 = st.columns(2)


with order_col1:

    order_quantity = st.number_input(
        "Order Quantity (units)",
        min_value=1,
        max_value=5000,
        value=int(
            st.session_state.get(
                "order_quantity",
                300,
            )
        ),
        step=1,
        key="order_quantity",
    )


with order_col2:

    deadline_hours = st.number_input(
        "Deadline (hours)",
        min_value=1,
        max_value=24,
        value=int(
            st.session_state.get(
                "deadline_hours",
                8,
            )
        ),
        step=1,
        key="deadline_hours",
    )


order_quantity = int(
    order_quantity
)

deadline_hours = int(
    deadline_hours
)


# ============================================================
# GRID DEMAND PROFILE
# ============================================================

st.subheader(
    "⚡ Grid Demand Profile"
)


grid_options = [
    "Low",
    "Medium",
    "High",
]


grid_profile = []


for start in range(
    0,
    deadline_hours,
    8,
):

    end = min(
        start + 8,
        deadline_hours,
    )

    row_hours = list(
        range(
            start,
            end,
        )
    )

    profile_columns = st.columns(
        len(row_hours)
    )


    for column, hour_index in zip(
        profile_columns,
        row_hours,
    ):

        with column:

            demand = st.selectbox(
                f"H{hour_index + 1}",
                grid_options,
                key=f"grid_select_{hour_index}",
            )

            grid_profile.append(
                demand
            )


# ============================================================
# GENERATE ORDER
# ============================================================

generate_order = st.button(
    "🧠 Generate AI Production Plan",
    use_container_width=True,
)


# IMPORTANT:
# result must remain INSIDE this block.
# Otherwise Streamlit will try to use an undefined
# variable during normal page reruns.

if generate_order:

    try:

        # Get latest ML-predicted machine risks.
        machine_risks = (
            get_numeric_machine_risks()
        )


        result = generate_schedule(
            machines=machines,
            order_quantity=order_quantity,
            deadline_hours=deadline_hours,
            grid_profile=grid_profile,
            machine_risks=machine_risks,
        )


        # Store only after successful generation.
        st.session_state.order_result = result


    except Exception as error:

        st.session_state.order_result = None

        st.error(
            "❌ Could not generate the AI production plan."
        )

        st.exception(error)


# ============================================================
# ORDER RESULT
# ============================================================

if st.session_state.order_result is not None:

    result = (
        st.session_state.order_result
    )


    st.subheader(
        "📋 Order Status"
    )


    if result.get(
        "completed",
        False,
    ):

        st.success(
            "🎉 Production order completed "
            "within the deadline!"
        )

    else:

        st.warning(
            f"Order incomplete. Remaining: "
            f"{result.get('remaining', 0)} units."
        )


    r1, r2, r3, r4 = st.columns(4)


    r1.metric(
        "Status",
        (
            "✅ Completed"
            if result.get(
                "completed",
                False,
            )
            else "❌ Incomplete"
        ),
    )


    r2.metric(
        "Production",
        f"{result.get('total_production', 0)} units",
    )


    r3.metric(
        "Energy",
        f"{result.get('total_energy', 0)} kWh",
    )


    r4.metric(
        "Remaining",
        f"{result.get('remaining', 0)} units",
    )


    if not result.get(
        "completed",
        False,
    ):

        st.error(
            result.get(
                "reason",
                "Order could not be completed.",
            )
        )


    # ========================================================
    # AI DECISION TIMELINE
    # ========================================================

    st.subheader(
        "🧭 AI Decision Timeline"
    )


    timeline = result.get(
        "schedule",
        [],
    )


    if timeline:

        # Keep the timeline readable for 24-hour orders.
        for start in range(
            0,
            len(timeline),
            8,
        ):

            row = timeline[
                start:start + 8
            ]

            timeline_cols = st.columns(
                len(row)
            )


            for column, hour in zip(
                timeline_cols,
                row,
            ):

                with column:

                    machines_used = (
                        " + ".join(
                            hour.get(
                                "machines",
                                (),
                            )
                        )
                    )


                    st.markdown(
                        f"**H{hour.get('hour', '?')}**  \n"
                        f"{hour.get('grid_demand', 'Unknown')} grid  \n"
                        f"⚙️ {machines_used}"
                    )


                    st.caption(
                        f"{hour.get('production', 0)} units · "
                        f"{hour.get('energy', 0)} kWh"
                    )


                    st.caption(
                        f"ML Risk: "
                        f"{hour.get('ml_risk', 0)}%"
                    )


    # ========================================================
    # HOURLY TABLE
    # ========================================================

    st.subheader(
        "🤖 Hour-by-Hour AI Production Plan"
    )


    schedule_rows = []


    for hour in timeline:

        schedule_rows.append(
            {
                "Hour": hour.get(
                    "hour"
                ),

                "Grid": hour.get(
                    "grid_demand"
                ),

                "Machines": " + ".join(
                    hour.get(
                        "machines",
                        (),
                    )
                ),

                "Production": hour.get(
                    "production",
                    0,
                ),

                "Energy (kWh)": hour.get(
                    "energy",
                    0,
                ),

                "ML Risk": (
                    f"{hour.get('ml_risk', 0)}%"
                ),

                "Required / Hour": hour.get(
                    "required_per_hour",
                    0,
                ),

                "Remaining": hour.get(
                    "remaining",
                    0,
                ),

                "AI Reason": hour.get(
                    "reason",
                    "No explanation available.",
                ),
            }
        )


    schedule_df = pd.DataFrame(
        schedule_rows
    )


    if not schedule_df.empty:

        st.dataframe(
            schedule_df,
            use_container_width=True,
            hide_index=True,
        )


        # ====================================================
        # CHARTS
        # ====================================================

        chart_col1, chart_col2 = st.columns(2)


        with chart_col1:

            production_fig = px.bar(
                schedule_df,
                x="Hour",
                y="Production",
                title="Production by Hour",
                text="Production",
            )


            production_fig.update_layout(
                xaxis_title="Hour",
                yaxis_title="Production (units)",
            )


            st.plotly_chart(
                production_fig,
                use_container_width=True,
            )


        with chart_col2:

            energy_fig = px.bar(
                schedule_df,
                x="Hour",
                y="Energy (kWh)",
                title="Energy Use by Hour",
                text="Energy (kWh)",
            )


            energy_fig.update_layout(
                xaxis_title="Hour",
                yaxis_title="Energy (kWh)",
            )


            st.plotly_chart(
                energy_fig,
                use_container_width=True,
            )


    # ========================================================
    # AI EXPLANATION
    # ========================================================

    st.subheader(
        "🧠 Why Did the AI Choose This?"
    )


    for hour in timeline:

        machines_used = (
            " + ".join(
                hour.get(
                    "machines",
                    (),
                )
            )
        )


        with st.expander(
            f"Hour {hour.get('hour', '?')} — "
            f"{hour.get('grid_demand', 'Unknown')} Grid — "
            f"{machines_used}"
        ):

            e1, e2, e3, e4 = st.columns(4)


            e1.metric(
                "Production",
                f"{hour.get('production', 0)} units",
            )


            e2.metric(
                "Energy",
                f"{hour.get('energy', 0)} kWh",
            )


            e3.metric(
                "ML Risk",
                f"{hour.get('ml_risk', 0)}%",
            )


            e4.metric(
                "Remaining",
                f"{hour.get('remaining', 0)} units",
            )


            st.info(
                f"🤖 {hour.get('reason', 'No explanation available.')}"
            )


# ============================================================
# WHAT-IF FACTORY SIMULATOR
# ============================================================

st.divider()

st.header(
    "🔮 What-If Factory Simulator"
)

st.write(
    "Compare a simple all-machine operating strategy "
    "with the AI-selected strategy."
)


if st.session_state.last_plan is not None:

    ai_plan = (
        st.session_state.last_plan
    )

    ai_machines = list(
        ai_plan["machines"]
    )

    current_machines = list(
        machines.keys()
    )


    current_metrics = (
        calculate_plan_metrics(
            machines,
            current_machines,
        )
    )


    ai_metrics = (
        calculate_plan_metrics(
            machines,
            ai_machines,
        )
    )


    energy_savings = (
        calculate_savings(
            current_metrics["energy"],
            ai_metrics["energy"],
        )
    )


    compare_col1, compare_col2 = (
        st.columns(2)
    )


    with compare_col1:

        st.subheader(
            "🏭 Current Factory"
        )

        st.metric(
            "Machines Running",
            current_metrics[
                "machine_count"
            ],
        )

        st.metric(
            "Production",
            f"{current_metrics['production']} units/hr",
        )

        st.metric(
            "Energy",
            f"{current_metrics['energy']} kWh",
        )


    with compare_col2:

        st.subheader(
            "🤖 AI Factory"
        )

        st.metric(
            "Machines Running",
            ai_metrics[
                "machine_count"
            ],
        )

        st.metric(
            "Production",
            f"{ai_metrics['production']} units/hr",
        )

        st.metric(
            "Energy",
            f"{ai_metrics['energy']} kWh",
        )


    st.divider()

    st.subheader(
        "⚡ AI Impact"
    )


    impact1, impact2, impact3 = (
        st.columns(3)
    )


    impact1.metric(
        "Energy Saved",
        f"{energy_savings}%",
    )


    impact2.metric(
        "Energy Reduction",
        f"{current_metrics['energy'] - ai_metrics['energy']} kWh",
    )


    impact3.metric(
        "Machines Avoided",
        current_metrics[
            "machine_count"
        ]
        - ai_metrics[
            "machine_count"
        ],
    )


    comparison_data = pd.DataFrame(
        {
            "Strategy": [
                "Current Factory",
                "AI Factory",
            ],

            "Energy": [
                current_metrics["energy"],
                ai_metrics["energy"],
            ],

            "Production": [
                current_metrics["production"],
                ai_metrics["production"],
            ],
        }
    )


    fig = px.bar(
        comparison_data,
        x="Strategy",
        y="Energy",
        title="Energy Consumption Comparison",
        text="Energy",
    )


    fig.update_layout(
        xaxis_title="Strategy",
        yaxis_title="Energy (kWh)",
    )


    st.plotly_chart(
        fig,
        use_container_width=True,
    )


else:

    st.info(
        "Run the **AI Scheduler** above to activate "
        "the What-If comparison."
    )

# ============================================================
# BEFORE vs AFTER AI COMPARISON
# ============================================================

st.divider()

st.header("📊 AI Impact — Before vs After")

st.write(
    "Compare factory operation before and after "
    "FactoryMind AI optimisation."
)


# ------------------------------------------------------------
# Calculate baseline factory values
# ------------------------------------------------------------

baseline_production = sum(
    machine["production"]
    for machine in machines.values()
)

baseline_energy = sum(
    machine["energy"]
    for machine in machines.values()
)

baseline_risk = sum(
    machine["risk"]
    for machine in machines.values()
)


# ------------------------------------------------------------
# Determine AI values
# ------------------------------------------------------------

if st.session_state.last_plan:

    ai_plan = st.session_state.last_plan

    ai_production = ai_plan["production"]
    ai_energy = ai_plan["energy"]
    ai_risk = ai_plan["risk"]

    ai_machines = ai_plan["machines"]

else:

    # Default AI calculation for demonstration
    ai_plan = calculate_machine_plan(
        machines,
        50,
        "Medium",
    )

    if ai_plan:

        ai_production = ai_plan["production"]
        ai_energy = ai_plan["energy"]
        ai_risk = ai_plan["risk"]
        ai_machines = ai_plan["machines"]

    else:

        ai_production = 0
        ai_energy = 0
        ai_risk = 0
        ai_machines = ()


# ------------------------------------------------------------
# Comparison table
# ------------------------------------------------------------

comparison_data = {
    "Metric": [
        "Production Capacity",
        "Energy Consumption",
        "Machine Risk",
        "Machines Operating",
    ],

    "Traditional Factory": [
        f"{baseline_production} units/hr",
        f"{baseline_energy} kWh",
        f"{baseline_risk}%",
        f"{len(machines)}",
    ],

    "FactoryMind AI": [
        f"{ai_production} units/hr",
        f"{ai_energy} kWh",
        f"{ai_risk}%",
        f"{len(ai_machines)}",
    ],
}


st.table(
    comparison_data
)


# ------------------------------------------------------------
# Impact calculations
# ------------------------------------------------------------

if baseline_energy > 0:

    energy_saving = (
        (
            baseline_energy
            - ai_energy
        )
        / baseline_energy
    ) * 100

else:

    energy_saving = 0


if baseline_production > 0:

    production_change = (
        (
            ai_production
            - baseline_production
        )
        / baseline_production
    ) * 100

else:

    production_change = 0


# ------------------------------------------------------------
# KPI cards
# ------------------------------------------------------------

impact_col1, impact_col2, impact_col3 = (
    st.columns(3)
)


with impact_col1:

    st.metric(
        "Energy Difference",
        f"{energy_saving:.1f}%",
    )


with impact_col2:

    st.metric(
        "AI Production",
        f"{ai_production} units/hr",
    )


with impact_col3:

    st.metric(
        "Machines Selected",
        len(ai_machines),
    )


# ------------------------------------------------------------
# AI Summary
# ------------------------------------------------------------

st.info(
    f"""
🧠 **FactoryMind AI Summary**

The AI evaluated the available machine combinations
instead of automatically operating every machine.

**Selected machines:**
{' + '.join(ai_machines) if ai_machines else 'None'}

**Production:**
{ai_production} units/hr

**Energy:**
{ai_energy} kWh

**Machine risk:**
{ai_risk}%

The purpose of the optimisation is to meet the
production requirement while considering energy
consumption, machine risk and grid conditions.
"""
)


# ============================================================
# WHAT-IF AI SIMULATOR
# ============================================================

st.divider()

st.header("🔮 What-If AI Simulator")

st.write(
    "Test how FactoryMind AI reacts when factory conditions "
    "suddenly change."
)


whatif_machine = st.selectbox(
    "Select Machine to Simulate",
    list(machines.keys()),
    key="whatif_machine",
)


whatif_event = st.selectbox(
    "Simulate Event",
    [
        "Normal Operation",
        "High Breakdown Risk",
        "Machine Failure",
        "Energy Consumption Increase",
    ],
    key="whatif_event",
)


# ------------------------------------------------------------
# Create modified factory state
# ------------------------------------------------------------

whatif_machines = {
    name: data.copy()
    for name, data in machines.items()
}


whatif_risks = get_numeric_machine_risks()


# ------------------------------------------------------------
# Apply simulated event
# ------------------------------------------------------------

if whatif_event == "High Breakdown Risk":

    whatif_risks[
        whatif_machine
    ] = 85


elif whatif_event == "Machine Failure":

    whatif_machines[
        whatif_machine
    ]["production"] = 0

    whatif_risks[
        whatif_machine
    ] = 100


elif whatif_event == "Energy Consumption Increase":

    whatif_machines[
        whatif_machine
    ]["energy"] *= 1.5


# ------------------------------------------------------------
# Show simulated machine state
# ------------------------------------------------------------

st.subheader("🧪 Simulated Factory State")


whatif_cols = st.columns(
    len(whatif_machines)
)


for index, machine_name in enumerate(
    whatif_machines
):

    with whatif_cols[index]:

        machine = whatif_machines[
            machine_name
        ]

        risk = whatif_risks[
            machine_name
        ]


        st.metric(
            machine_name,
            f"{machine['production']} units/hr",
        )

        st.caption(
            f"Energy: {machine['energy']:.1f} kWh"
        )

        st.caption(
            f"ML Risk: {risk}%"
        )


        if risk >= 60:

            st.error(
                "🔴 HIGH RISK"
            )

        elif risk >= 30:

            st.warning(
                "🟡 MEDIUM RISK"
            )

        else:

            st.success(
                "🟢 LOW RISK"
            )


# ------------------------------------------------------------
# Run What-If AI
# ------------------------------------------------------------

st.subheader("🤖 AI Response")


whatif_target = st.number_input(
    "Required Production (units/hr)",
    min_value=1,
    max_value=200,
    value=50,
    step=5,
    key="whatif_target",
)


whatif_grid = st.selectbox(
    "Grid Demand",
    [
        "Low",
        "Medium",
        "High",
    ],
    key="whatif_grid",
)


if st.button(
    "🚀 Run What-If Simulation",
    key="run_whatif",
):

    normal_plan = calculate_machine_plan(
        machines,
        whatif_target,
        whatif_grid,
    )


    simulated_plan = calculate_machine_plan(
        whatif_machines,
        whatif_target,
        whatif_grid,
    )


    # --------------------------------------------------------
    # Normal plan
    # --------------------------------------------------------

    st.markdown(
        "### Before Event"
    )


    if normal_plan:

        st.write(
            f"Machines: "
            f"**{' + '.join(normal_plan['machines'])}**"
        )

        st.write(
            f"Production: "
            f"**{normal_plan['production']} units/hr**"
        )

        st.write(
            f"Energy: "
            f"**{normal_plan['energy']} kWh**"
        )


    # --------------------------------------------------------
    # Simulated plan
    # --------------------------------------------------------

    st.markdown(
        "### After Event"
    )


    if simulated_plan:

        st.write(
            f"Machines: "
            f"**{' + '.join(simulated_plan['machines'])}**"
        )

        st.write(
            f"Production: "
            f"**{simulated_plan['production']} units/hr**"
        )

        st.write(
            f"Energy: "
            f"**{simulated_plan['energy']} kWh**"
        )


        # ----------------------------------------------------
        # AI explanation
        # ----------------------------------------------------

        if whatif_event == "Machine Failure":

            st.warning(
                f"""
⚠️ **Machine failure detected**

{whatif_machine} is no longer available.

FactoryMind AI recalculated the production plan
using the remaining machines.
"""
            )


        elif whatif_event == "High Breakdown Risk":

            st.warning(
                f"""
⚠️ **High breakdown risk detected**

{whatif_machine} now has an estimated risk of
{whatif_risks[whatif_machine]}%.

FactoryMind AI can consider alternative
machines when they can still satisfy the
production requirement.
"""
            )


        elif whatif_event == "Energy Consumption Increase":

            st.info(
                f"""
⚡ **Energy consumption changed**

{whatif_machine}'s simulated energy consumption
has increased.

FactoryMind AI recalculated the machine
combination using the updated energy data.
"""
            )


        else:

            st.success(
                "No abnormal event simulated. "
                "FactoryMind AI is operating normally."
            )


    else:

        st.error(
            "❌ The simulated factory cannot meet "
            "the requested production target."
        )



# ============================================================
# PROJECT SUMMARY
# ============================================================

st.divider()

st.header(
    "💡 FactoryMind AI — How It Works"
)


summary1, summary2, summary3 = (
    st.columns(3)
)


with summary1:

    st.subheader(
        "1️⃣ Sense"
    )

    st.write(
        "The digital twin receives production targets, "
        "grid demand, machine capacity, energy use "
        "and machine health data."
    )


with summary2:

    st.subheader(
        "2️⃣ Decide"
    )

    st.write(
        "The scheduler evaluates machine combinations "
        "and selects a production strategy while "
        "considering energy, deadline pressure and "
        "predicted breakdown risk."
    )


with summary3:

    st.subheader(
        "3️⃣ Adapt"
    )

    st.write(
        "For production orders, the AI recalculates "
        "the plan hour by hour as grid demand and "
        "deadline pressure change."
    )


st.caption(
    "FactoryMind AI is a simulation and decision-support "
    "prototype. It does not directly control physical "
    "factory equipment or the electricity grid."
)
