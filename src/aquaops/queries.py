
"""SQL queries for AquaOps monitoring and maintenance."""

from sqlalchemy import create_engine, text

from aquaops.config import get_settings
from functools import lru_cache

@lru_cache(maxsize=1)
def get_engine():
    """Return a shared database engine."""
    return create_engine(
        get_settings().database_url,
        pool_pre_ping=True,
    )


def get_plant_summary():
    """Return plant-wise equipment and sensor counts."""
    query = text("""
        SELECT
            p.plant_id,
            p.plant_name,
            p.location,
            p.design_capacity_mld,
            COUNT(DISTINCT e.equipment_id) AS equipment_count,
            COUNT(DISTINCT s.sensor_id) AS sensor_count
        FROM treatment_plants p
        LEFT JOIN equipment e ON e.plant_id = p.plant_id
        LEFT JOIN sensors s ON s.plant_id = p.plant_id
        GROUP BY p.plant_id
        ORDER BY p.plant_name;
    """)

    with get_engine().connect() as conn:
        return [dict(row) for row in conn.execute(query).mappings()]


def get_latest_readings():
    """Return the most recent reading for each sensor."""
    query = text("""
        SELECT DISTINCT ON (s.sensor_id)
            p.plant_name,
            s.sensor_name,
            s.parameter_name,
            s.unit,
            r.value,
            r.measured_at
        FROM sensors s
        JOIN treatment_plants p ON p.plant_id = s.plant_id
        JOIN water_quality_readings r ON r.sensor_id = s.sensor_id
        ORDER BY s.sensor_id, r.measured_at DESC;
    """)

    with get_engine().connect() as conn:
        return [dict(row) for row in conn.execute(query).mappings()]


def get_average_readings(hours: int = 24):
    """Return average sensor values over the specified time window."""
    if hours <= 0:
        raise ValueError("hours must be positive")

    query = text("""
        SELECT
            p.plant_name,
            s.parameter_name,
            s.unit,
            ROUND(AVG(r.value), 3) AS average_value,
            MIN(r.value) AS minimum_value,
            MAX(r.value) AS maximum_value,
            COUNT(*) AS reading_count
        FROM water_quality_readings r
        JOIN sensors s ON s.sensor_id = r.sensor_id
        JOIN treatment_plants p ON p.plant_id = s.plant_id
        WHERE r.measured_at >= NOW() - (:hours * INTERVAL '1 hour')
        GROUP BY p.plant_name, s.parameter_name, s.unit
        ORDER BY p.plant_name, s.parameter_name;
    """)

    with get_engine().connect() as conn:
        return [
            dict(row)
            for row in conn.execute(query, {"hours": hours}).mappings()
        ]


def get_open_maintenance():
    """Return maintenance tasks that are not finished or cancelled."""
    query = text("""
        SELECT
            p.plant_name,
            e.equipment_name,
            e.equipment_type,
            m.maintenance_type,
            m.description,
            m.priority,
            m.status,
            m.reported_at,
            m.scheduled_at
        FROM maintenance_records m
        JOIN equipment e ON e.equipment_id = m.equipment_id
        JOIN treatment_plants p ON p.plant_id = e.plant_id
        WHERE m.status IN ('open', 'scheduled', 'in_progress')
        ORDER BY
            CASE m.priority
                WHEN 'critical' THEN 1
                WHEN 'high' THEN 2
                WHEN 'medium' THEN 3
                ELSE 4
            END,
            m.reported_at DESC;
    """)

    with get_engine().connect() as conn:
        return [dict(row) for row in conn.execute(query).mappings()]


def get_equipment_summary():
    """Return equipment counts by plant and status."""
    query = text("""
        SELECT
            p.plant_name,
            e.status,
            COUNT(*) AS equipment_count
        FROM equipment e
        JOIN treatment_plants p ON p.plant_id = e.plant_id
        GROUP BY p.plant_name, e.status
        ORDER BY p.plant_name, e.status;
    """)

    with get_engine().connect() as conn:
        return [dict(row) for row in conn.execute(query).mappings()]
