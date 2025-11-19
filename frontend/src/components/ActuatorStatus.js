import React, { useState, useEffect } from 'react';
import './ActuatorStatus.css';
import { getCurrentActuatorStates } from '../services/api';

const ActuatorStatus = () => {
  const [actuators, setActuators] = useState([]);
  const [loading, setLoading] = useState(false);

  const loadActuatorStates = async () => {
    setLoading(true);
    try {
      const data = await getCurrentActuatorStates();
      setActuators(data);
    } catch (error) {
      console.error('Error loading actuator states:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadActuatorStates();
    // Refresh every 2 seconds
    const interval = setInterval(loadActuatorStates, 2000);
    return () => clearInterval(interval);
  }, []);

  const getActuatorIcon = (type) => {
    switch (type.toLowerCase()) {
      case 'fan':
        return '🌀';
      case 'light':
        return '💡';
      case 'alarm':
        return '🚨';
      default:
        return '⚙️';
    }
  };

  if (loading && actuators.length === 0) {
    return (
      <div className="actuator-status">
        <h2>Actuator Status</h2>
        <p>Loading...</p>
      </div>
    );
  }

  return (
    <div className="actuator-status">
      <div className="actuator-header">
        <h2>Actuator Status</h2>
        <button onClick={loadActuatorStates} className="refresh-btn" disabled={loading}>
          {loading ? '🔄' : '🔄'} Refresh
        </button>
      </div>
      
      {actuators.length === 0 ? (
        <p className="no-actuators">No actuators active. Run a simulation cycle to see actuator states.</p>
      ) : (
        <div className="actuator-grid">
          {actuators.map((actuator) => (
            <div key={actuator.actuator_id} className="actuator-card">
              <div className="actuator-icon">{getActuatorIcon(actuator.actuator_type)}</div>
              <div className="actuator-info">
                <h3>{actuator.actuator_type.toUpperCase()}</h3>
                <p className="actuator-id">{actuator.actuator_id}</p>
                <div className={`actuator-state ${actuator.state.toLowerCase()}`}>
                  {actuator.state}
                </div>
                {actuator.value !== null && actuator.value !== undefined && (
                  <p className="actuator-value">Value: {actuator.value}</p>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default ActuatorStatus;

