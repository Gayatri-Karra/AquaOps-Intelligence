
-- AquaOps Intelligence
-- Migration 001: Initial database schema
-- PostgreSQL

BEGIN;

-- 1. Treatment plants
CREATE TABLE treatment_plants (
    plant_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    plant_name VARCHAR(150) NOT NULL,
    location VARCHAR(255),
    design_capacity_mld NUMERIC(12, 3)
        CHECK (design_capacity_mld > 0),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 2. Equipment registry
CREATE TABLE equipment (
    equipment_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    plant_id BIGINT NOT NULL
        REFERENCES treatment_plants(plant_id),
    equipment_name VARCHAR(150) NOT NULL,
    equipment_type VARCHAR(60) NOT NULL,
    installation_date DATE,
    status VARCHAR(20) NOT NULL DEFAULT 'active'
        CHECK (status IN ('active', 'inactive', 'maintenance')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (plant_id, equipment_name)
);

-- 3. Sensor registry
CREATE TABLE sensors (
    sensor_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    plant_id BIGINT NOT NULL
        REFERENCES treatment_plants(plant_id),
    equipment_id BIGINT
        REFERENCES equipment(equipment_id),
    sensor_name VARCHAR(150) NOT NULL,
    parameter_name VARCHAR(50) NOT NULL,
    unit VARCHAR(30) NOT NULL,
    installed_at TIMESTAMPTZ,
    status VARCHAR(20) NOT NULL DEFAULT 'active'
        CHECK (status IN ('active', 'inactive', 'faulty')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (plant_id, sensor_name)
);

-- 4. Time-series water quality readings
CREATE TABLE water_quality_readings (
    reading_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    sensor_id BIGINT NOT NULL
        REFERENCES sensors(sensor_id),
    measured_at TIMESTAMPTZ NOT NULL,
    value NUMERIC(14, 5) NOT NULL,
    ingested_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    source VARCHAR(50) NOT NULL DEFAULT 'sensor',
    CONSTRAINT uq_sensor_measurement
        UNIQUE (sensor_id, measured_at)
);

-- 5. Maintenance history
CREATE TABLE maintenance_records (
    maintenance_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    equipment_id BIGINT NOT NULL
        REFERENCES equipment(equipment_id),
    maintenance_type VARCHAR(30) NOT NULL
        CHECK (maintenance_type IN ('preventive', 'corrective', 'inspection')),
    description TEXT NOT NULL,
    reported_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    scheduled_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    status VARCHAR(20) NOT NULL DEFAULT 'open'
        CHECK (status IN ('open', 'scheduled', 'in_progress', 'completed', 'cancelled')),
    priority VARCHAR(20) NOT NULL DEFAULT 'medium'
        CHECK (priority IN ('low', 'medium', 'high', 'critical'))
);

-- Indexes for common monitoring and maintenance queries
CREATE INDEX idx_equipment_plant
    ON equipment(plant_id);

CREATE INDEX idx_sensors_plant
    ON sensors(plant_id);

CREATE INDEX idx_sensors_equipment
    ON sensors(equipment_id);

CREATE INDEX idx_readings_sensor_time
    ON water_quality_readings(sensor_id, measured_at DESC);

CREATE INDEX idx_maintenance_equipment_status
    ON maintenance_records(equipment_id, status);

CREATE INDEX idx_maintenance_open_priority
    ON maintenance_records(priority, reported_at DESC)
    WHERE status IN ('open', 'scheduled', 'in_progress');

COMMIT;
