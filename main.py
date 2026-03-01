import os
import time

import pandas as pd
import requests
import streamlit as st

# Configure page
st.set_page_config(
    page_title="Project AEGIS - Real-Time Dashboard",
    page_icon="🚑",
    layout="wide",
)

# API config
ORCHESTRATOR_URL = os.getenv("ORCHESTRATOR_URL", "http://localhost:8000")


def fetch_fleet():
    try:
        response = requests.get(f"{ORCHESTRATOR_URL}/fleet", timeout=5)
        response.raise_for_status()
        return response.json()
    except Exception:
        return None


def fetch_emergencies():
    try:
        response = requests.get(f"{ORCHESTRATOR_URL}/emergencies", timeout=5)
        response.raise_for_status()
        return response.json()
    except Exception:
        return None


def main():
    st.title("🚑 Project AEGIS - City Operations Dashboard")
    st.markdown(
        "Real-time visualization of emergency vehicles, orchestrator actions, and city scenarios."
    )

    # Top level metrics
    fleet_data = fetch_fleet()
    emergencies = fetch_emergencies()

    if fleet_data:
        summary = fleet_data.get("summary", {})
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Vehicles", summary.get("total_vehicles", 0))
        col2.metric("Available", summary.get("available_vehicles", 0))
        col3.metric("On Mission", summary.get("on_mission", 0))
        col4.metric("Active Alerts", summary.get("vehicles_with_alerts", 0))
    else:
        st.warning(
            f"Could not connect to Orchestrator API at {ORCHESTRATOR_URL}. Make sure it is running."
        )

    st.markdown("---")

    col_map, col_list = st.columns([2, 1])

    with col_map:
        st.subheader("🗺️ City Map (Live)")
        map_data = []

        # Add vehicles to map
        if fleet_data and "vehicles" in fleet_data:
            for v in fleet_data["vehicles"]:
                loc = v.get("location")
                if loc:
                    # Color coding: Green (available), Blue (on mission), Red (alert)
                    color = "#00FF00"
                    if v.get("operational_status") != "idle":
                        color = "#0000FF"
                    if v.get("has_active_alert"):
                        color = "#FF0000"

                    map_data.append(
                        {
                            "lat": loc["latitude"],
                            "lon": loc["longitude"],
                            "type": f"Vehicle: {v['vehicle_id']}",
                            "color": color,
                            "size": 100,
                        }
                    )

        # Add emergencies to map
        if emergencies:
            for e in emergencies:
                if e.get("status") != "resolved":
                    # Orange for emergencies
                    map_data.append(
                        {
                            "lat": e["latitude"],
                            "lon": e["longitude"],
                            "type": f"Emergency: {e['emergency_type']}",
                            "color": "#FFA500",
                            "size": 250,
                        }
                    )

        if map_data:
            df_map = pd.DataFrame(map_data)
            st.map(df_map, latitude="lat", longitude="lon", color="color", size="size")
        else:
            st.info("No location data available for map.")

    with col_list:
        st.subheader("🚨 Active Scenarios & Crimes")
        if emergencies:
            active_emergencies = [e for e in emergencies if e.get("status") != "resolved"]
            if active_emergencies:
                for e in active_emergencies:
                    with st.expander(
                        f"{e['emergency_type'].upper()} - {e['status']}", expanded=True
                    ):
                        st.write(f"**Severity:** {e['severity']}")
                        st.write(f"**Description:** {e['description']}")
                        st.write(
                            f"**Assigned Vehicles:** {', '.join(e.get('assigned_vehicles', [])) or 'None'}"
                        )
            else:
                st.success("No active emergencies in the city.")
        else:
            st.info("No emergency data available.")

        st.subheader("⏱️ Emergency Timeline")
        if emergencies:
            # Sort by created_at descending to show latest first
            sorted_em = sorted(emergencies, key=lambda x: x.get("created_at", ""), reverse=True)
            for e in sorted_em[:10]:  # show last 10
                created = str(e.get("created_at", ""))[:19].replace("T", " ")
                status = e.get("status", "unknown")
                icon = "✅" if status == "resolved" else ("🚨" if status == "pending" else "🚙")

                st.markdown(f"**{created}** {icon} {e['emergency_type'].upper()} ({status})")
                if e.get("dispatched_at") and status != "resolved":
                    st.text(f"    → Dispatched {len(e.get('assigned_vehicles', []))} units")
        else:
            st.info("No timeline events yet.")

    st.markdown("---")
    st.subheader("🚓 Agents (Vehicles)")
    if fleet_data and "vehicles" in fleet_data:
        df_vehicles = pd.DataFrame(fleet_data["vehicles"])
        if not df_vehicles.empty:
            display_cols = [
                "vehicle_id",
                "vehicle_type",
                "operational_status",
                "is_available",
                "battery_voltage",
                "fuel_level_percent",
                "has_active_alert",
            ]

            def highlight_alerts(row):
                if row.get("has_active_alert"):
                    return ["background-color: rgba(255, 0, 0, 0.2)"] * len(row)
                return [""] * len(row)

            st.dataframe(
                df_vehicles[display_cols].style.apply(highlight_alerts, axis=1),
                use_container_width=True,
            )
        else:
            st.info("No vehicles active.")

    # Auto-refresh
    time.sleep(2)
    st.rerun()


if __name__ == "__main__":
    main()
