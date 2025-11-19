import React, { useState } from 'react';
import './SimulationControl.css';
import { runSimulationCycle, runSimulation } from '../services/api';

const SimulationControl = ({ onSimulationRun }) => {
  const [isRunning, setIsRunning] = useState(false);
  const [isRunningCycle, setIsRunningCycle] = useState(false);
  const [simulationStatus, setSimulationStatus] = useState('');
  const [numCycles, setNumCycles] = useState(20);
  const [delaySeconds, setDelaySeconds] = useState(1.0);

  const handleRunCycle = async () => {
    setIsRunningCycle(true);
    setSimulationStatus('Running cycle...');
    
    try {
      const result = await runSimulationCycle();
      setSimulationStatus(`✓ Cycle ${result.cycle} completed! ${result.sensor_readings} sensor readings, ${result.decisions_made} decisions made`);
      
      if (onSimulationRun) {
        onSimulationRun();
      }
    } catch (error) {
      setSimulationStatus(`✗ Error: ${error.message || 'Failed to run cycle'}`);
    } finally {
      setIsRunningCycle(false);
    }
  };

  const handleRunSimulation = async () => {
    setIsRunning(true);
    setSimulationStatus(`Running ${numCycles} cycles...`);
    
    try {
      const result = await runSimulation(numCycles, delaySeconds);
      setSimulationStatus(`✓ Simulation completed! ${result.total_cycles} cycles run`);
      
      if (onSimulationRun) {
        onSimulationRun();
      }
    } catch (error) {
      setSimulationStatus(`✗ Error: ${error.message || 'Failed to run simulation'}`);
    } finally {
      setIsRunning(false);
    }
  };

  return (
    <div className="simulation-control">
      <h2>Simulation Control</h2>
      <p>Run simulation cycles: Sensors → Controller → Actuators</p>
      
      <div className="simulation-buttons">
        <button
          onClick={handleRunCycle}
          disabled={isRunningCycle || isRunning}
          className="cycle-button"
        >
          {isRunningCycle ? 'Running...' : 'Run Single Cycle'}
        </button>
        
        <div className="simulation-settings">
          <div className="setting-item">
            <label htmlFor="num-cycles">Number of Cycles:</label>
            <input
              id="num-cycles"
              type="number"
              min="1"
              max="100"
              value={numCycles}
              onChange={(e) => setNumCycles(parseInt(e.target.value) || 20)}
              disabled={isRunning}
            />
          </div>
          
          <div className="setting-item">
            <label htmlFor="delay">Delay (seconds):</label>
            <input
              id="delay"
              type="number"
              min="0.1"
              max="10"
              step="0.1"
              value={delaySeconds}
              onChange={(e) => setDelaySeconds(parseFloat(e.target.value) || 1.0)}
              disabled={isRunning}
            />
          </div>
          
          <button
            onClick={handleRunSimulation}
            disabled={isRunning || isRunningCycle}
            className="simulate-button"
          >
            {isRunning ? `Running ${numCycles} cycles...` : `Run ${numCycles} Cycles`}
          </button>
        </div>
      </div>
      
      {simulationStatus && (
        <p className={`status-message ${simulationStatus.includes('✓') ? 'success' : simulationStatus.includes('✗') ? 'error' : ''}`}>
          {simulationStatus}
        </p>
      )}
      
      <div className="info-box">
        <p><strong>Simulation Flow:</strong></p>
        <ol>
          <li>Sensors generate readings (temperature, light, motion)</li>
          <li>Central computer analyzes and makes decisions</li>
          <li>Actuators respond (fan, light, alarm)</li>
          <li>All actions are logged</li>
        </ol>
      </div>
    </div>
  );
};

export default SimulationControl;

