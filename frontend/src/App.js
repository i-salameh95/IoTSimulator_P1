import React, { useState, useEffect } from 'react';
import './App.css';
import Dashboard from './components/Dashboard';
import SensorChart from './components/SensorChart';
import SimulationControl from './components/SimulationControl';
import ActuatorStatus from './components/ActuatorStatus';
import LogsDisplay from './components/LogsDisplay';
import { fetchHistoricalData, fetchMeasurements } from './services/api';

function App() {
  const [measurements, setMeasurements] = useState([]);
  const [selectedMeasurement, setSelectedMeasurement] = useState(null);
  const [historicalData, setHistoricalData] = useState([]);
  const [loading, setLoading] = useState(false);
  const [refreshKey, setRefreshKey] = useState(0);

  useEffect(() => {
    loadMeasurements();
  }, []);

  useEffect(() => {
    if (selectedMeasurement) {
      loadHistoricalData(selectedMeasurement);
    }
  }, [selectedMeasurement, refreshKey]);

  const handleDataGenerated = () => {
    // Refresh the chart when new data is generated
    setRefreshKey(prev => prev + 1);
  };

  const loadMeasurements = async () => {
    try {
      const data = await fetchMeasurements();
      setMeasurements(data);
      if (data.length > 0) {
        setSelectedMeasurement(data[0]);
      }
    } catch (error) {
      console.error('Error loading measurements:', error);
    }
  };

  const loadHistoricalData = async (measurement) => {
    setLoading(true);
    try {
      const data = await fetchHistoricalData(measurement);
      setHistoricalData(data);
    } catch (error) {
      console.error('Error loading historical data:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>IoT Simulator Dashboard</h1>
        <p>Real-time Sensor Data Visualization</p>
      </header>
      
      <main className="App-main">
        <SimulationControl onSimulationRun={handleDataGenerated} />
        
        <div className="dashboard-grid">
          <ActuatorStatus />
          <Dashboard />
        </div>
        
        <LogsDisplay />
        
        <div className="chart-section">
          <div className="measurement-selector">
            <label htmlFor="measurement-select">Select Measurement: </label>
            <select
              id="measurement-select"
              value={selectedMeasurement || ''}
              onChange={(e) => setSelectedMeasurement(e.target.value)}
            >
              {measurements.map((m) => (
                <option key={m} value={m}>
                  {m.charAt(0).toUpperCase() + m.slice(1)}
                </option>
              ))}
            </select>
            <button
              className="refresh-button"
              onClick={() => {
                if (selectedMeasurement) {
                  loadHistoricalData(selectedMeasurement);
                }
              }}
              disabled={loading || !selectedMeasurement}
            >
              {loading ? 'Loading...' : '🔄 Refresh Chart'}
            </button>
          </div>
          
          {selectedMeasurement && (
            <SensorChart
              measurement={selectedMeasurement}
              data={historicalData}
              loading={loading}
            />
          )}
        </div>
      </main>
    </div>
  );
}

export default App;

