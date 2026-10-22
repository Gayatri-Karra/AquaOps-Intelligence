
BEGIN;

-- 1. Treatment plants
INSERT INTO treatment_plants
    (plant_name, location, design_capacity_mld)
VALUES
    ('Plant Alpha', 'Hyderabad', 50.000),
    ('Plant Beta', 'Secunderabad', 35.000);

-- 2. Equipment
INSERT INTO equipment
    (plant_id, equipment_name, equipment_type, installation_date)
SELECT p.plant_id, v.equipment_name, v.equipment_type, v.installation_date
FROM treatment_plants p
CROSS JOIN (
    VALUES
        ('Raw Water Pump 01', 'pump', DATE '2023-01-15'),
        ('Sand Filter 01', 'filter', DATE '2022-08-10'),
        ('Chlorination Unit 01', 'chlorination', DATE '2024-02-01')
) AS v(equipment_name, equipment_type, installation_date)
WHERE p.plant_name = 'Plant Alpha'
ON CONFLICT (plant_id, equipment_name) DO NOTHING;

INSERT INTO equipment
    (plant_id, equipment_name, equipment_type, installation_date)
SELECT p.plant_id, v.equipment_name, v.equipment_type, v.installation_date
FROM treatment_plants p
CROSS JOIN (
    VALUES
        ('Raw Water Pump 01', 'pump', DATE '2023-03-12'),
        ('Sand Filter 01', 'filter', DATE '2022-11-05')
) AS v(equipment_name, equipment_type, installation_date)
WHERE p.plant_name = 'Plant Beta'
ON CONFLICT (plant_id, equipment_name) DO NOTHING;

-- 3. Sensors for Plant Alpha
INSERT INTO sensors
    (plant_id, equipment_id, sensor_name, parameter_name, unit)
SELECT p.plant_id, e.equipment_id, v.sensor_name, v.parameter_name, v.unit
FROM treatment_plants p
JOIN equipment e ON e.plant_id = p.plant_id
CROSS JOIN (
    VALUES
        ('Alpha pH Sensor', 'pH', 'pH units', 'Raw Water Pump 01'),
        ('Alpha Turbidity Sensor', 'turbidity', 'NTU', 'Sand Filter 01'),
        ('Alpha Flow Sensor', 'flow', 'm3/h', 'Raw Water Pump 01')
) AS v(sensor_name, parameter_name, unit, equipment_name)
WHERE p.plant_name = 'Plant Alpha'
  AND e.equipment_name = v.equipment_name
ON CONFLICT (plant_id, sensor_name) DO NOTHING;

-- 4. Sensors for Plant Beta
INSERT INTO sensors
    (plant_id, equipment_id, sensor_name, parameter_name, unit)
SELECT p.plant_id, e.equipment_id, v.sensor_name, v.parameter_name, v.unit
FROM treatment_plants p
JOIN equipment e ON e.plant_id = p.plant_id
CROSS JOIN (
    VALUES
        ('Beta pH Sensor', 'pH', 'pH units', 'Raw Water Pump 01'),
        ('Beta Turbidity Sensor', 'turbidity', 'NTU', 'Sand Filter 01')
) AS v(sensor_name, parameter_name, unit, equipment_name)
WHERE p.plant_name = 'Plant Beta'
  AND e.equipment_name = v.equipment_name
ON CONFLICT (plant_id, sensor_name) DO NOTHING;

-- 5. Generate 7 days of hourly sensor readings
-- Synthetic demo readings, not real operational measurements.
INSERT INTO water_quality_readings
    (sensor_id, measured_at, value, source)
SELECT
    s.sensor_id,
    t.measured_at,
    CASE s.parameter_name
        WHEN 'pH' THEN
            ROUND((7.2 + 0.25 * SIN(EXTRACT(EPOCH FROM t.measured_at) / 18000.0)
             + (RANDOM() - 0.5) * 0.15)::NUMERIC, 5)
        WHEN 'turbidity' THEN
            ROUND((2.5 + ABS(SIN(EXTRACT(EPOCH FROM t.measured_at) / 36000.0))
             + RANDOM() * 0.8)::NUMERIC, 5)
        WHEN 'flow' THEN
            ROUND((120 + RANDOM() * 15)::NUMERIC, 5)
    END,
    'synthetic_demo'
FROM sensors s
CROSS JOIN generate_series(
    NOW() - INTERVAL '7 days',
    NOW(),
    INTERVAL '1 hour'
) AS t(measured_at)
ON CONFLICT (sensor_id, measured_at) DO NOTHING;

-- 6. Sample maintenance records
INSERT INTO maintenance_records
    (equipment_id, maintenance_type, description, status, priority)
SELECT e.equipment_id, v.maintenance_type, v.description,
       v.status, v.priority
FROM equipment e
JOIN treatment_plants p ON p.plant_id = e.plant_id
CROSS JOIN (
    VALUES
        ('corrective', 'Pump vibration above normal range',
         'open', 'high', 'Raw Water Pump 01'),
        ('preventive', 'Scheduled filter inspection',
         'scheduled', 'medium', 'Sand Filter 01'),
        ('inspection', 'Routine equipment condition inspection',
         'completed', 'low', 'Chlorination Unit 01')
) AS v(maintenance_type, description, status, priority, equipment_name)
WHERE p.plant_name = 'Plant Alpha'
  AND e.equipment_name = v.equipment_name
  AND NOT EXISTS (
      SELECT 1
      FROM maintenance_records mr
      WHERE mr.equipment_id = e.equipment_id
        AND mr.description = v.description
  );

COMMIT;
