import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, Area, AreaChart } from 'recharts';
import { apiClient, APIError, Vehicle } from '../lib/api';
import { Download, AlertCircle } from 'lucide-react';
import { exportTimeSeries } from '../utils/exportData';
import { ChartSkeleton } from '../components/SkeletonLoader';

export default function TimeSeriesExplorer() {
  const [selectedVehicle, setSelectedVehicle] = useState<string>('all');
  const [selectedRoute, setSelectedRoute] = useState<string>('all');
  const [metric, setMetric] = useState<'speed' | 'position'>('speed');
  const [exportFormat, setExportFormat] = useState<'csv' | 'json'>('csv');

  const { data: vehicles, isLoading: vehiclesLoading, error: vehiclesError } = useQuery({
    queryKey: ['vehicles', selectedRoute === 'all' ? undefined : selectedRoute],
    queryFn: () => apiClient.getVehicles(selectedRoute === 'all' ? undefined : selectedRoute),
    refetchInterval: 10000, // 10 seconds for real-time updates
    staleTime: 5000,
    retry: 2,
  });

  const uniqueRoutes = Array.from(new Set(vehicles?.map(v => v.route_id).filter(Boolean) || []));
  const uniqueVehicles = Array.from(new Set(vehicles?.map(v => v.vehicle_id) || []));

  // Generate time-series data for demonstration
  const generateTimeSeriesData = () => {
    if (!vehicles || vehicles.length === 0) return [];

    const selected = selectedVehicle === 'all' 
      ? vehicles[0]
      : vehicles.find(v => v.vehicle_id === selectedVehicle);

    if (!selected) return [];

    const data = [];
    const now = new Date();
    
    for (let i = 23; i >= 0; i--) {
      const timestamp = new Date(now.getTime() - i * 60 * 60 * 1000);
      data.push({
        time: timestamp.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' }),
        timestamp: timestamp.toISOString(),
        speed: selected.speed ? selected.speed + (Math.random() * 10 - 5) : 0,
        latitude: selected.latitude ? selected.latitude + (Math.random() * 0.01 - 0.005) : 0,
        longitude: selected.longitude ? selected.longitude + (Math.random() * 0.01 - 0.005) : 0,
      });
    }

    return data;
  };

  const timeSeriesData = generateTimeSeriesData();

  const handleExport = () => {
    if (timeSeriesData.length === 0) return;
    exportTimeSeries(timeSeriesData, {
      format: exportFormat,
      filename: `telemetry-${selectedVehicle || 'all'}-${new Date().toISOString().split('T')[0]}.${exportFormat}`
    });
  };

  if (vehiclesLoading) {
    return (
      <div className="space-y-6">
        <div>
          <h2 className="text-3xl font-bold mb-2">Time-Series Explorer</h2>
          <p className="text-gray-400">Explore historical telemetry data for vehicles and routes</p>
        </div>
        <ChartSkeleton />
      </div>
    );
  }

  if (vehiclesError) {
    const errorMessage = vehiclesError instanceof APIError ? vehiclesError.message : 'Failed to load vehicle data';
    return (
      <div className="space-y-6">
        <div>
          <h2 className="text-3xl font-bold mb-2">Time-Series Explorer</h2>
        </div>
        <div className="bg-red-900/20 border border-red-800 rounded-lg p-6">
          <div className="flex items-center">
            <AlertCircle className="h-5 w-5 text-red-500 mr-3" />
            <div>
              <h3 className="text-lg font-semibold text-red-300">Error Loading Data</h3>
              <p className="text-gray-400 text-sm mt-1">{errorMessage}</p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-3xl font-bold mb-2">Time-Series Explorer</h2>
        <p className="text-gray-400">Explore historical telemetry data for vehicles and routes</p>
      </div>

      {/* Controls */}
      <div className="bg-gray-900 border border-gray-800 rounded-lg p-4 flex flex-wrap gap-4">
        <div className="flex items-center space-x-2">
          <label className="text-sm text-gray-400">Route:</label>
          <select
            value={selectedRoute}
            onChange={(e) => setSelectedRoute(e.target.value)}
            className="bg-black border border-gray-700 rounded px-3 py-1 text-sm text-white focus:outline-none focus:border-green-500"
          >
            <option value="all">All Routes</option>
            {uniqueRoutes.map(route => (
              <option key={route} value={route}>{route}</option>
            ))}
          </select>
        </div>

        <div className="flex items-center space-x-2">
          <label className="text-sm text-gray-400">Vehicle:</label>
          <select
            value={selectedVehicle}
            onChange={(e) => setSelectedVehicle(e.target.value)}
            className="bg-black border border-gray-700 rounded px-3 py-1 text-sm text-white focus:outline-none focus:border-green-500"
          >
            <option value="all">All Vehicles</option>
            {uniqueVehicles.slice(0, 20).map(vehicleId => (
              <option key={vehicleId} value={vehicleId}>{vehicleId}</option>
            ))}
          </select>
        </div>

        <div className="flex items-center space-x-2">
          <label className="text-sm text-gray-400">Metric:</label>
          <select
            value={metric}
            onChange={(e) => setMetric(e.target.value as 'speed' | 'position')}
            className="bg-black border border-gray-700 rounded px-3 py-1 text-sm text-white focus:outline-none focus:border-green-500"
          >
            <option value="speed">Speed</option>
            <option value="position">Position</option>
          </select>
        </div>

        <div className="flex items-center space-x-2 ml-auto">
          <select
            value={exportFormat}
            onChange={(e) => setExportFormat(e.target.value as 'csv' | 'json')}
            className="bg-black border border-gray-700 rounded px-2 py-1 text-sm text-white focus:outline-none focus:border-green-500"
          >
            <option value="csv">CSV</option>
            <option value="json">JSON</option>
          </select>
          <button
            onClick={handleExport}
            disabled={timeSeriesData.length === 0}
            className="flex items-center space-x-2 bg-green-600 hover:bg-green-700 disabled:bg-gray-700 disabled:cursor-not-allowed text-white px-4 py-1 rounded text-sm transition-colors"
          >
            <Download className="h-4 w-4" />
            <span>Export {exportFormat.toUpperCase()}</span>
          </button>
        </div>
      </div>

      {/* Time-Series Chart */}
      <div className="bg-gray-900 border border-gray-800 rounded-lg p-6">
        <h3 className="text-xl font-semibold mb-4">
          {metric === 'speed' ? 'Speed Over Time' : 'Position Changes Over Time'}
        </h3>
        
        {timeSeriesData.length > 0 ? (
          <ResponsiveContainer width="100%" height={400}>
            {metric === 'speed' ? (
              <AreaChart data={timeSeriesData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                <XAxis 
                  dataKey="time" 
                  stroke="#9ca3af"
                  label={{ value: 'Time', position: 'insideBottom', offset: -5, fill: '#9ca3af' }}
                />
                <YAxis 
                  stroke="#9ca3af"
                  label={{ value: 'Speed (mph)', angle: -90, position: 'insideLeft', fill: '#9ca3af' }}
                />
                <Tooltip 
                  contentStyle={{ backgroundColor: '#1f2937', border: '1px solid #374151', borderRadius: '8px' }}
                  labelStyle={{ color: '#fff' }}
                />
                <Area 
                  type="monotone" 
                  dataKey="speed" 
                  stroke="#10b981" 
                  fill="#10b981"
                  fillOpacity={0.3}
                  name="Speed (mph)"
                />
              </AreaChart>
            ) : (
              <LineChart data={timeSeriesData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                <XAxis 
                  dataKey="time" 
                  stroke="#9ca3af"
                  label={{ value: 'Time', position: 'insideBottom', offset: -5, fill: '#9ca3af' }}
                />
                <YAxis 
                  stroke="#9ca3af"
                  label={{ value: 'Coordinate', angle: -90, position: 'insideLeft', fill: '#9ca3af' }}
                />
                <Tooltip 
                  contentStyle={{ backgroundColor: '#1f2937', border: '1px solid #374151', borderRadius: '8px' }}
                  labelStyle={{ color: '#fff' }}
                />
                <Legend />
                <Line 
                  type="monotone" 
                  dataKey="latitude" 
                  stroke="#3b82f6" 
                  strokeWidth={2}
                  name="Latitude"
                  dot={false}
                />
                <Line 
                  type="monotone" 
                  dataKey="longitude" 
                  stroke="#ef4444" 
                  strokeWidth={2}
                  name="Longitude"
                  dot={false}
                />
              </LineChart>
            )}
          </ResponsiveContainer>
        ) : (
          <div className="flex items-center justify-center h-64">
            <div className="text-gray-400">No time-series data available</div>
          </div>
        )}
      </div>

      {/* Event Timeline */}
      <div className="bg-gray-900 border border-gray-800 rounded-lg p-6">
        <h3 className="text-xl font-semibold mb-4">Recent Status Changes</h3>
        <div className="space-y-2 max-h-64 overflow-y-auto">
          {vehicles && vehicles.length > 0 ? (
            vehicles
              .filter(v => v.current_status)
              .slice(0, 10)
              .map((vehicle) => (
                <div 
                  key={vehicle.id} 
                  className="flex items-center justify-between p-3 bg-black border border-gray-800 rounded"
                >
                  <div className="flex items-center">
                    <div className="h-2 w-2 bg-green-500 rounded-full mr-3"></div>
                    <span className="text-sm">
                      Vehicle <span className="font-semibold">{vehicle.vehicle_id}</span> -{' '}
                      {vehicle.current_status?.replace(/_/g, ' ').toLowerCase()}
                      {vehicle.route_name && ` on ${vehicle.route_name}`}
                    </span>
                  </div>
                  <span className="text-xs text-gray-500">
                    {new Date(vehicle.last_updated).toLocaleTimeString()}
                  </span>
                </div>
              ))
          ) : (
            <div className="text-gray-400 text-center py-8">No recent events</div>
          )}
        </div>
      </div>
    </div>
  );
}