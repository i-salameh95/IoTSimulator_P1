import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: `${API_URL}/api/v1`,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Sensor data ingestion
export const ingestSensorData = async (reading) => {
  const response = await api.post('/sensors/ingest', reading);
  return response.data;
};

// Batch sensor data ingestion
export const ingestSensorDataBatch = async (readings) => {
  const response = await api.post('/sensors/ingest/batch', readings);
  return response.data;
};

// Generate and ingest simulated data (legacy - use runSimulationCycle instead)
export const ingestSimulatedData = async () => {
  // Use the new simulation cycle endpoint
  return await runSimulationCycle();
};

// Get historical data
export const fetchHistoricalData = async (measurement, deviceId = null, sensorId = null) => {
  const response = await api.post('/sensors/query/historical', {
    measurement,
    device_id: deviceId,
    sensor_id: sensorId,
    limit: 1000,
  });
  return response.data;
};

// Get aggregated data
export const fetchAggregatedData = async (measurement, window = '1h', aggregate = 'mean') => {
  const response = await api.post('/sensors/query/aggregated', {
    measurement,
    window,
    aggregate,
  });
  return response.data;
};

// Get available measurements
export const fetchMeasurements = async () => {
  const response = await api.get('/sensors/measurements');
  return response.data;
};

// Get available devices
export const fetchDevices = async () => {
  const response = await api.get('/sensors/devices');
  return response.data;
};

// Simulation endpoints
export const runSimulationCycle = async () => {
  const response = await api.post('/simulation/run-cycle');
  return response.data;
};

export const runSimulation = async (numCycles = 20, delaySeconds = 1.0) => {
  const response = await api.post(`/simulation/run?num_cycles=${numCycles}&delay_seconds=${delaySeconds}`);
  return response.data;
};

// Actuator endpoints
export const getActuatorStates = async (limit = 100) => {
  const response = await api.get('/actuators/states', {
    params: { limit }
  });
  return response.data;
};

export const getCurrentActuatorStates = async () => {
  const response = await api.get('/actuators/states/current');
  return response.data;
};

export const controlActuator = async (actuatorData) => {
  const response = await api.post('/actuators/control', actuatorData);
  return response.data;
};

// Logs endpoints
export const getLogs = async (level = null, source = null, deviceId = null, limit = 100) => {
  const params = { limit };
  if (level) params.level = level;
  if (source) params.source = source;
  if (deviceId) params.device_id = deviceId;
  
  const response = await api.get('/logs/', { params });
  return response.data;
};

