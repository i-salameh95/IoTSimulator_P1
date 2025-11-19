import React, { useState, useEffect } from 'react';
import './LogsDisplay.css';
import { getLogs } from '../services/api';

const LogsDisplay = () => {
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(false);
  const [filterLevel, setFilterLevel] = useState('');
  const [filterSource, setFilterSource] = useState('');

  const loadLogs = async () => {
    setLoading(true);
    try {
      const data = await getLogs(filterLevel || null, filterSource || null, null, 100);
      setLogs(data);
    } catch (error) {
      console.error('Error loading logs:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadLogs();
    // Refresh every 2 seconds
    const interval = setInterval(loadLogs, 2000);
    return () => clearInterval(interval);
  }, [filterLevel, filterSource]);

  const getLogLevelClass = (level) => {
    switch (level) {
      case 'DEBUG':
        return 'log-debug';
      case 'INFO':
        return 'log-info';
      case 'WARNING':
        return 'log-warning';
      case 'ERROR':
        return 'log-error';
      case 'CRITICAL':
        return 'log-critical';
      default:
        return '';
    }
  };

  const formatTime = (timeString) => {
    try {
      const date = new Date(timeString);
      return date.toLocaleTimeString();
    } catch {
      return timeString;
    }
  };

  return (
    <div className="logs-display">
      <div className="logs-header">
        <h2>System Logs</h2>
        <div className="logs-filters">
          <select
            value={filterLevel}
            onChange={(e) => setFilterLevel(e.target.value)}
            className="filter-select"
          >
            <option value="">All Levels</option>
            <option value="DEBUG">DEBUG</option>
            <option value="INFO">INFO</option>
            <option value="WARNING">WARNING</option>
            <option value="ERROR">ERROR</option>
            <option value="CRITICAL">CRITICAL</option>
          </select>
          
          <select
            value={filterSource}
            onChange={(e) => setFilterSource(e.target.value)}
            className="filter-select"
          >
            <option value="">All Sources</option>
            <option value="sensor">Sensor</option>
            <option value="controller">Controller</option>
            <option value="actuator">Actuator</option>
            <option value="simulation">Simulation</option>
          </select>
          
          <button onClick={loadLogs} className="refresh-btn" disabled={loading}>
            {loading ? '🔄' : '🔄'} Refresh
          </button>
        </div>
      </div>
      
      <div className="logs-container">
        {logs.length === 0 ? (
          <p className="no-logs">No logs available. Run a simulation to generate logs.</p>
        ) : (
          <div className="logs-list">
            {logs.map((log, index) => (
              <div key={index} className={`log-entry ${getLogLevelClass(log.level)}`}>
                <div className="log-time">{formatTime(log.time)}</div>
                <div className="log-level">{log.level}</div>
                <div className="log-source">{log.source}</div>
                <div className="log-message">{log.message}</div>
                {log.device_id && (
                  <div className="log-meta">Device: {log.device_id}</div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default LogsDisplay;

