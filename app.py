import streamlit as st
import pandas as pd
import plotly.express as px

from scheduler import calculate_machine_plan
from simulator import FactorySimulator
from what_if import calculate_plan_metrics, calculate_savings
from order_scheduler import generate_schedule


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
    "M1": {"production": 20, "energy": 30, "risk": 5},
    "M2": {"production": 50, "energy": 90, "risk": 10},
    "M3": {"production": 25, "energy": 35, "risk": 7},
}


# ============================================================
# SESSION STATE
# ============================================================

defaults = {
    "simulation_data": [],
    "factory": FactorySimulator(machines),
    "active_machines": [],
    "last_plan": None,
    "order_result": None,
    "demo_loaded": False,
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def load_demo_values():
    """Load one repeatable hackathon demo scenario."""
    st.session_state["order_quantity"] = 300
    st.session_state["deadline_hours"] = 8

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

    for i, demand in enumerate(demo_grid):
        st.session_state[f"grid_select_{i}"] = demand

    st.session_state["demo_loaded"] = True
    st.session_state["order_result"] = None


def reset_factory():
    st.session_state.factory = FactorySimulator(machines)
    st.session_state.simulation_data = []
    st.session_state.active_machines = []
    st.session_state.last_plan = None
    st.session_state.order_result = None
    st.session_state.demo_loaded = False


def show_machine_plan(plan, current_grid):
    selected = " + ".join(plan["machines"])

    st.success(f"🤖 AI Selected: **{selected}**")

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("Production", f"{plan['production']} units/hr")
    c2.metric("Energy", f"{plan['energy']} kWh")
    c3.metric("Risk", f"{plan['risk']}%")
    c4.metric("Grid", current_grid)

    st.info(
        f"""
**AI reasoning**

Current grid demand is **{current_grid}**.

The scheduler evaluated possible machine combinations and selected
**{selected}** to satisfy the production target while considering
energy use, risk and excess production.
"""
    )


# ============================================================
# HEADER
# ============================================================

st.title("🏭 FactoryMind AI")
st.subheader("AI Digital Twin + Autonomous Production Scheduler")

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
    options=["Low", "Medium", "High"],
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

k1.metric("Grid Demand", grid_demand)
k2.metric("Production Target", f"{production_target} units/hr")
k3.metric("Simulation Time", f"{st.session_state.factory.time_elapsed} hr")
k4.metric("Active Machines", len(st.session_state.active_machines))


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
            "❌ No machine combination can satisfy the current "
            "production target."
        )
        st.session_state.active_machines = []
        st.session_state.last_plan = None
    else:
        st.session_state.active_machines = list(plan["machines"])
        st.session_state.last_plan = plan


st.divider()
st.header("🤖 Machine AI Recommendation")

if st.session_state.last_plan is not None:
    show_machine_plan(
        st.session_state.last_plan,
        grid_demand,
    )
else:
    st.info("Click **Run AI Scheduler** to generate a machine plan.")


# ============================================================
# VIRTUAL FACTORY / DIGITAL TWIN
# ============================================================

st.divider()
st.header("🏭 Virtual Factory")

st.caption(
    "Each machine is represented as a virtual asset. "
    "The green state shows the machines selected by the AI."
)

machine_columns = st.columns(3)

for index, (machine_name, machine) in enumerate(machines.items()):
    with machine_columns[index]:
        is_active = machine_name in st.session_state.active_machines
        status = "🟢 RUNNING" if is_active else "🔴 OFF"

        st.subheader(f"⚙️ {machine_name}")
        st.write(f"**Status:** {status}")

        m1, m2, m3 = st.columns(3)

        m1.metric(
            "Capacity",
            f"{machine['production']} u/hr",
        )

        m2.metric(
            "Energy",
            f"{machine['energy']} kWh",
        )

        m3.metric(
            "Risk",
            f"{machine['risk']}%",
        )


# ============================================================
# LIVE SIMULATION
# ============================================================

if run_simulation:
    if not st.session_state.active_machines:
        st.warning("⚠️ Run the AI Scheduler first.")
    else:
        result = st.session_state.factory.run_step(
            st.session_state.active_machines,
            duration=1,
        )

        st.session_state.simulation_data.append(result)

st.divider()
st.header("📈 Live Factory Simulation")

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
        "No simulation data yet. Run the AI Scheduler and then "
        "click **Run Simulation Step**."
    )


# ============================================================
# AUTONOMOUS PRODUCTION ORDER AI
# ============================================================

st.divider()
st.header("📦 Autonomous Production Order AI")

st.write(
    "Give the factory an order and a deadline. FactoryMind AI "
    "creates an hour-by-hour production strategy while considering "
    "changing grid demand."
)

demo_col1, demo_col2 = st.columns([1, 3])

with demo_col1:
    if st.button(
        "🎬 Load Demo Scenario",
        use_container_width=True,
    ):
        load_demo_values()
        st.rerun()

with demo_col2:
    st.caption(
        "Demo: 300 units in 8 hours with changing grid demand "
        "from Low → Medium → High → Low."
    )


order_col1, order_col2 = st.columns(2)

with order_col1:
    order_quantity = st.number_input(
        "Order Quantity (units)",
        min_value=1,
        max_value=5000,
        value=st.session_state.get("order_quantity", 300),
        key="order_quantity",
    )

with order_col2:
    deadline_hours = st.number_input(
        "Deadline (hours)",
        min_value=1,
        max_value=24,
        value=st.session_state.get("deadline_hours", 8),
        key="deadline_hours",
    )

deadline_hours = int(deadline_hours)

st.subheader("⚡ Grid Demand Profile")

grid_options = ["Low", "Medium", "High"]
grid_profile = []

# Show up to 8 hours per row so the layout stays clean.
for start in range(0, deadline_hours, 8):
    row_hours = range(
        start,
        min(start + 8, deadline_hours),
    )

    profile_columns = st.columns(len(list(row_hours)))

    for column, hour_index in zip(profile_columns, row_hours):
        with column:
            demand = st.selectbox(
                f"H{hour_index + 1}",
                grid_options,
                key=f"grid_select_{hour_index}",
            )
            grid_profile.append(demand)

generate_order = st.button(
    "🧠 Generate AI Production Plan",
    use_container_width=True,
)

if generate_order:
    result = generate_schedule(
        machines,
        int(order_quantity),
        deadline_hours,
        grid_profile,
    )

    st.session_state.order_result = result


# ============================================================
# ORDER RESULT
# ============================================================

if st.session_state.order_result is not None:
    result = st.session_state.order_result

    st.subheader("📋 Order Status")

    if result["completed"]:
        st.success("🎉 Production order completed within the deadline!")
    else:
        st.warning(
            f"Order incomplete. Remaining: {result['remaining']} units."
        )

    r1, r2, r3, r4 = st.columns(4)

    r1.metric(
        "Status",
        "✅ Completed" if result["completed"] else "❌ Incomplete",
    )

    r2.metric(
        "Production",
        f"{result['total_production']} units",
    )

    r3.metric(
        "Energy",
        f"{result['total_energy']} kWh",
    )

    r4.metric(
        "Remaining",
        f"{result['remaining']} units",
    )

    if not result["completed"]:
        st.error(
            result.get(
                "reason",
                "Order could not be completed.",
            )
        )

    # --------------------------------------------------------
    # HOURLY TIMELINE
    # --------------------------------------------------------

    st.subheader("🧭 AI Decision Timeline")

    timeline = result["schedule"]

    if timeline:
        timeline_cols = st.columns(len(timeline))

        for column, hour in zip(timeline_cols, timeline):
            with column:
                machines_used = " + ".join(hour["machines"])

                st.markdown(
                    f"**H{hour['hour']}**  \n"
                    f"{hour['grid_demand']} grid  \n"
                    f"⚙️ {machines_used}"
                )

                st.caption(
                    f"{hour['production']} units · "
                    f"{hour['energy']} kWh"
                )

    # --------------------------------------------------------
    # HOURLY TABLE
    # --------------------------------------------------------

    st.subheader("🤖 Hour-by-Hour AI Production Plan")

    schedule_rows = []

    for hour in result["schedule"]:
        schedule_rows.append(
            {
                "Hour": hour["hour"],
                "Grid": hour["grid_demand"],
                "Machines": " + ".join(hour["machines"]),
                "Production": hour["production"],
                "Energy (kWh)": hour["energy"],
                "Required / Hour": hour["required_per_hour"],
                "Remaining": hour["remaining"],
                "AI Reason": hour["reason"],
            }
        )

    schedule_df = pd.DataFrame(schedule_rows)

    st.dataframe(
        schedule_df,
        use_container_width=True,
        hide_index=True,
    )

    # --------------------------------------------------------
    # PRODUCTION / ENERGY CHART
    # --------------------------------------------------------

    if not schedule_df.empty:
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

    # --------------------------------------------------------
    # AI EXPLANATION
    # --------------------------------------------------------

    st.subheader("🧠 Why Did the AI Choose This?")

    for hour in result["schedule"]:
        machines_used = " + ".join(hour["machines"])

        with st.expander(
            f"Hour {hour['hour']} — "
            f"{hour['grid_demand']} Grid — "
            f"{machines_used}"
        ):
            e1, e2, e3 = st.columns(3)

            e1.metric(
                "Production",
                f"{hour['production']} units",
            )

            e2.metric(
                "Energy",
                f"{hour['energy']} kWh",
            )

            e3.metric(
                "Remaining",
                f"{hour['remaining']} units",
            )

            st.info(
                f"🤖 {hour['reason']}"
            )


# ============================================================
# WHAT-IF FACTORY SIMULATOR
# ============================================================

st.divider()
st.header("🔮 What-If Factory Simulator")

st.write(
    "Compare a simple all-machine operating strategy with "
    "the AI-selected strategy."
)

if st.session_state.last_plan is not None:
    ai_plan = st.session_state.last_plan
    ai_machines = list(ai_plan["machines"])

    current_machines = list(machines.keys())

    current_metrics = calculate_plan_metrics(
        machines,
        current_machines,
    )

    ai_metrics = calculate_plan_metrics(
        machines,
        ai_machines,
    )

    energy_savings = calculate_savings(
        current_metrics["energy"],
        ai_metrics["energy"],
    )

    compare_col1, compare_col2 = st.columns(2)

    with compare_col1:
        st.subheader("🏭 Current Factory")

        st.metric(
            "Machines Running",
            current_metrics["machine_count"],
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
        st.subheader("🤖 AI Factory")

        st.metric(
            "Machines Running",
            ai_metrics["machine_count"],
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
    st.subheader("⚡ AI Impact")

    impact1, impact2, impact3 = st.columns(3)

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
        current_metrics["machine_count"]
        - ai_metrics["machine_count"],
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
        "Run the **AI Scheduler** above to activate the "
        "What-If comparison."
    )


# ============================================================
# PROJECT SUMMARY
# ============================================================

st.divider()
st.header("💡 FactoryMind AI — How It Works")

summary1, summary2, summary3 = st.columns(3)

with summary1:
    st.subheader("1️⃣ Sense")
    st.write(
        "The digital twin receives production targets, "
        "grid demand, machine capacity, energy use and risk."
    )

with summary2:
    st.subheader("2️⃣ Decide")
    st.write(
        "The scheduler evaluates machine combinations and "
        "selects a production strategy for the current situation."
    )

with summary3:
    st.subheader("3️⃣ Adapt")
    st.write(
        "For production orders, the AI recalculates the plan "
        "hour by hour as demand and deadline pressure change."
    )

st.caption(
    "FactoryMind AI is a simulation and decision-support prototype. "
    "It does not directly control physical factory equipment or the electricity grid."
)
