
"""AquaOps Intelligence monitoring dashboard."""

import pandas as pd
import plotly.express as px
import streamlit as st
from sqlalchemy import create_engine, text

from aquaops.config import get_settings
from aquaops import queries


st.set_page_config(
    page_title="AquaOps Intelligence",
    page_icon="💧",
    layout="wide",
)

# Reuse the database connection pool.
@st.cache_resource
def get_db_engine():
    return create_engine(
        get_settings().database_url,
        pool_pre_ping=True,
    )


def load_trend_data(hours: int) -> pd.DataFrame:
    """Load readings for time-series visualization."""
    query = text("""
        SELECT
            p.plant_name,
            s.sensor_name,
            s.parameter_name,
            s.unit,
            r.measured_at,
            r.value
        FROM water_quality_readings r
        JOIN sensors s ON s.sensor_id = r.sensor_id
        JOIN treatment_plants p ON p.plant_id = s.plant_id
        WHERE r.measured_at >= NOW() - (:hours * INTERVAL '1 hour')
        ORDER BY r.measured_at;
    """)

    with get_db_engine().connect() as conn:
        return pd.read_sql(
            query,
            conn,
            params={"hours": hours},
        )


st.title("💧 AquaOps Intelligence")
st.caption("Smart Water Treatment Monitoring & Predictive Maintenance")

with st.sidebar:
    st.header("Dashboard Controls")

    hours = st.selectbox(
        "Monitoring window",
        options=[6, 12, 24, 48, 72, 168],
        index=2,
        format_func=lambda x: (
            f"{x} hours" if x < 168 else "7 days"
        ),
    )

    refresh = st.button(
        "Refresh dashboard",
        use_container_width=True,
    )

    st.divider()
    st.caption("AquaOps Intelligence | Demo Environment")
    st.caption("Readings may contain synthetic demo data.")

if refresh:
    st.cache_data.clear()

try:
    with st.spinner("Loading monitoring data..."):
        plants = queries.get_plant_summary()
        latest = queries.get_latest_readings()
        maintenance = queries.get_open_maintenance()
        equipment = queries.get_equipment_summary()
        trends = load_trend_data(hours)

    plants_df = pd.DataFrame(plants)
    latest_df = pd.DataFrame(latest)
    maintenance_df = pd.DataFrame(maintenance)
    equipment_df = pd.DataFrame(equipment)


except Exception as exc:
    st.error(
        "Unable to load dashboard data. Check PostgreSQL, "
        "database credentials, schema migration, and sample data."
    )
    st.exception(exc)
    st.stop()



# ---------------- Overview KPIs ----------------

total_plants = len(plants_df)

total_equipment = (
    int(plants_df["equipment_count"].sum())
    if not plants_df.empty else 0
)

total_sensors = (
    int(plants_df["sensor_count"].sum())
    if not plants_df.empty else 0
)

open_work_orders = len(maintenance_df)

st.subheader("Operations Overview")

k1, k2, k3, k4 = st.columns(4)

k1.metric("Treatment Plants", total_plants)
k2.metric("Equipment", total_equipment)
k3.metric("Sensors", total_sensors)
k4.metric("Open Work Orders", open_work_orders)

st.divider()


# ---------------- Plant Overview ----------------

st.subheader("Treatment Plant Overview")

if plants_df.empty:
    st.info("No treatment plants registered yet.")
else:
    display_plants = plants_df.rename(columns={
        "plant_name": "Plant",
        "location": "Location",
        "design_capacity_mld": "Capacity (MLD)",
        "equipment_count": "Equipment",
        "sensor_count": "Sensors",
    })

    st.dataframe(
        display_plants[
            [
                "Plant",
                "Location",
                "Capacity (MLD)",
                "Equipment",
                "Sensors",
            ]
        ],
        use_container_width=True,
        hide_index=True,
    )


st.divider()


# ---------------- Latest Readings ----------------

st.subheader("Latest Water Quality Readings")

if latest_df.empty:
    st.info("No sensor readings available.")
else:
    latest_display = latest_df.rename(columns={
        "plant_name": "Plant",
        "sensor_name": "Sensor",
        "parameter_name": "Parameter",
        "unit": "Unit",
        "value": "Latest Value",
        "measured_at": "Measured At",
    })

    st.dataframe(
        latest_display[
            [
                "Plant",
                "Sensor",
                "Parameter",
                "Latest Value",
                "Unit",
                "Measured At",
            ]
        ],
        use_container_width=True,
        hide_index=True,
    )


# ---------------- Trend Analysis ----------------

st.divider()
st.subheader("Water Quality & Sensor Trends")

if trends.empty:
    st.info("No readings available for this time window.")
else:
    parameter_options = sorted(
        trends["parameter_name"].dropna().unique().tolist()
    )

    selected_parameter = st.selectbox(
        "Select parameter",
        parameter_options,
    )

    parameter_data = trends[
        trends["parameter_name"] == selected_parameter
    ].copy()

    if not parameter_data.empty:
        parameter_data["sensor_label"] = (
            parameter_data["plant_name"]
            + " | "
            + parameter_data["sensor_name"]
        )

        fig = px.line(
            parameter_data,
            x="measured_at",
            y="value",
            color="sensor_label",
            markers=False,
            labels={
                "measured_at": "Time",
                "value": f"Reading ({parameter_data['unit'].iloc[0]})",
                "sensor_label": "Sensor",
            },
            title=f"{selected_parameter} Monitoring Trend",
        )

        fig.update_layout(
            hovermode="x unified",
            legend_title_text="Sensor",
        )

        st.plotly_chart(fig, use_container_width=True)


# ---------------- Equipment Analytics ----------------

st.divider()
st.subheader("Equipment Status")

if equipment_df.empty:
    st.info("No equipment records available.")
else:
    fig_equipment = px.bar(
        equipment_df,
        x="plant_name",
        y="equipment_count",
        color="status",
        barmode="stack",
        labels={
            "plant_name": "Treatment Plant",
            "equipment_count": "Equipment Count",
            "status": "Status",
        },
        title="Equipment Distribution by Plant",
    )

    st.plotly_chart(
        fig_equipment,
        use_container_width=True,
    )


# ---------------- Maintenance ----------------

st.divider()
st.subheader("Maintenance Work Orders")

if maintenance_df.empty:
    st.success("No open maintenance work orders.")
else:
    maintenance_display = maintenance_df.rename(columns={
        "plant_name": "Plant",
        "equipment_name": "Equipment",
        "equipment_type": "Equipment Type",
        "maintenance_type": "Maintenance Type",
        "description": "Description",
        "priority": "Priority",
        "status": "Status",
        "reported_at": "Reported At",
        "scheduled_at": "Scheduled At",
    })

    st.dataframe(
        maintenance_display[
            [
                "Plant",
                "Equipment",
                "Maintenance Type",
                "Description",
                "Priority",
                "Status",
                "Reported At",
                "Scheduled At",
            ]
        ],
        use_container_width=True,
        hide_index=True,
    )

st.caption(
    "AquaOps Intelligence | "
    "Monitoring dashboard | Development version"
)
