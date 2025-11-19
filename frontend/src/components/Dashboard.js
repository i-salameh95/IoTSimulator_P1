import React from 'react';
import './Dashboard.css';

const Dashboard = () => {
  return (
    <div className="dashboard">
      <div className="dashboard-card">
        <h2>System Status</h2>
        <div className="status-grid">
          <div className="status-item">
            <span className="status-label">Backend API:</span>
            <span className="status-value online">Online</span>
          </div>
          <div className="status-item">
            <span className="status-label">MongoDB:</span>
            <span className="status-value online">Connected</span>
          </div>
          <div className="status-item">
            <span className="status-label">Redis:</span>
            <span className="status-value online">Connected</span>
          </div>
        </div>
        <div className="info-box">
          <p><strong>Smart Home IoT Simulator</strong></p>
          <p>This system simulates a smart home environment with:</p>
          <ul>
            <li><strong>Sensors:</strong> Temperature (15-40°C), Light (0-100), Motion (0/1)</li>
            <li><strong>Actuators:</strong> Fan, Light, Alarm</li>
            <li><strong>Rules:</strong> Temp &gt; 30°C → Fan ON | Motion + Light &lt; 20 → Light ON | Motion + Temp &gt;= 37°C → Alarm ON</li>
          </ul>
          <p>Use the "Simulation Control" section above to run simulation cycles.</p>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;

