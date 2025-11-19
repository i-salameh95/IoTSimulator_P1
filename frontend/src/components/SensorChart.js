import React from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer
} from 'recharts';
import './SensorChart.css';
import { format } from 'date-fns';

const SensorChart = ({ measurement, data, loading }) => {
  // Transform data for Recharts
  const chartData = data.map(item => ({
    time: format(new Date(item.time), 'HH:mm:ss'),
    value: item.value,
    device: item.device_id
  }));

  if (loading) {
    return (
      <div className="chart-loading">
        <p>Loading chart data...</p>
      </div>
    );
  }

  if (chartData.length === 0) {
    return (
      <div className="chart-empty">
        <p>No data available for {measurement}. Run a simulation cycle to generate sensor data!</p>
      </div>
    );
  }

  return (
    <div className="sensor-chart">
      <div className="chart-header">
        <h3>{measurement.charAt(0).toUpperCase() + measurement.slice(1)} Over Time</h3>
        <span className="data-count">{chartData.length} data points</span>
      </div>
      <ResponsiveContainer width="100%" height={400}>
        <LineChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis
            dataKey="time"
            label={{ value: 'Time', position: 'insideBottom', offset: -5 }}
          />
          <YAxis
            label={{ value: 'Value', angle: -90, position: 'insideLeft' }}
          />
          <Tooltip />
          <Legend />
          <Line
            type="monotone"
            dataKey="value"
            stroke="#4CAF50"
            strokeWidth={2}
            dot={{ r: 3 }}
            name={measurement}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
};

export default SensorChart;

