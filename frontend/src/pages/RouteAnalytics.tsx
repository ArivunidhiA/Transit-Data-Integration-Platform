import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { apiClient } from '../lib/api';
import { TrendingDown, TrendingUp } from 'lucide-react';

export default function RouteAnalytics() {
  const [selectedRoute, setSelectedRoute] = useState<string>('Red');
  const [timeRange, setTimeRange] = useState<number>(24);

  const { data: vehicles } = useQuery({
    queryKey: ['vehicles'],
    queryFn: () => apiClient.getVehicles(),
    refetchInterval: 10000, // 10 seconds for real-time updates
    staleTime: 5000,
  });

  const { data: delays, isLoading: delaysLoading } = useQuery({
    queryKey: ['route-delays', selectedRoute, timeRange],
    queryFn: () => apiClient.getRouteDelays(selectedRoute, timeRange),
    enabled: !!selectedRoute,
    refetchInterval: 15000, // 15 seconds for delay analytics (less frequent)
    staleTime: 10000,
  });

  const { data: headway, isLoading: headwayLoading } = useQuery({
    queryKey: ['headway', selectedRoute],
    queryFn: () => apiClient.getHeadwayAnalysis(selectedRoute),
    enabled: !!selectedRoute,
    refetchInterval: 15000, // 15 seconds for headway analytics (less frequent)
    staleTime: 10000,
  });

  const uniqueRoutes = Array.from(new Set(vehicles?.map(v => v.route_id).filter(Boolean) || []));

  // Format delay data for chart
  const delayChartData = delays?.delays.map(d => ({
    hour: d.hour_of_day,
    delay: d.avg_delay_minutes.toFixed(1),
    samples: d.sample_count,
  })).sort((a, b) => a.hour - b.hour) || [];

  // Calculate route stats
  const routeStats = vehicles
    ? vehicles
        .filter(v => v.route_id === selectedRoute)
        .reduce(
          (acc, v) => {
            acc.count++;
            if (v.speed !== null) acc.totalSpeed += v.speed;
            return acc;
          },
          { count: 0, totalSpeed: 0 }
        )
    : { count: 0, totalSpeed: 0 };

  const avgDelay = delayChartData.length > 0
    ? delayChartData.reduce((sum, d) => sum + parseFloat(d.delay), 0) / delayChartData.length
    : 0;

  const peakHour = delayChartData.length > 0
    ? delayChartData.reduce((max, d) => parseFloat(d.delay) > parseFloat(max.delay) ? d : max, delayChartData[0])
    : null;

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-3xl font-bold mb-2">Route Analytics</h2>
        <p className="text-gray-400">Delay patterns and performance metrics by route</p>
      </div>

      {/* Controls */}
      <div className="bg-gray-900 border border-gray-800 rounded-lg p-4 flex flex-wrap gap-4">
        <div className="flex items-center space-x-2">
          <label className="text-sm text-gray-400">Route:</label>
          <select
            value={selectedRoute || ''}
            onChange={(e) => setSelectedRoute(e.target.value)}
            className="bg-black border border-gray-700 rounded px-3 py-1 text-sm text-white focus:outline-none focus:border-green-500"
          >
            {uniqueRoutes.map(route => (
              <option key={route} value={route}>{route}</option>
            ))}
          </select>
        </div>

        <div className="flex items-center space-x-2">
          <label className="text-sm text-gray-400">Time Range:</label>
          <select
            value={timeRange}
            onChange={(e) => setTimeRange(Number(e.target.value))}
            className="bg-black border border-gray-700 rounded px-3 py-1 text-sm text-white focus:outline-none focus:border-green-500"
          >
            <option value={24}>Last 24 Hours</option>
            <option value={48}>Last 48 Hours</option>
            <option value={168}>Last 7 Days</option>
          </select>
        </div>
      </div>

      {/* Route Performance Summary */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-gray-900 border border-gray-800 rounded-lg p-4">
          <div className="text-gray-400 text-sm mb-2">Average Delay</div>
          <div className="text-2xl font-bold flex items-center">
            {avgDelay.toFixed(1)}
            <span className="text-sm text-gray-500 ml-1">min</span>
          </div>
          <div className={`text-xs mt-1 flex items-center ${
            avgDelay > 5 ? 'text-red-400' : avgDelay > 3 ? 'text-yellow-400' : 'text-green-400'
          }`}>
            {avgDelay > 5 ? <TrendingUp className="h-3 w-3 mr-1" /> : <TrendingDown className="h-3 w-3 mr-1" />}
            {avgDelay > 5 ? 'Above threshold' : 'Within threshold'}
          </div>
        </div>

        <div className="bg-gray-900 border border-gray-800 rounded-lg p-4">
          <div className="text-gray-400 text-sm mb-2">Peak Delay Hour</div>
          <div className="text-2xl font-bold">
            {peakHour ? `${peakHour.hour}:00` : 'N/A'}
          </div>
          <div className="text-xs text-gray-500 mt-1">
            {peakHour ? `${parseFloat(peakHour.delay).toFixed(1)} min avg` : 'No data'}
          </div>
        </div>

        <div className="bg-gray-900 border border-gray-800 rounded-lg p-4">
          <div className="text-gray-400 text-sm mb-2">Active Vehicles</div>
          <div className="text-2xl font-bold">{routeStats.count}</div>
          <div className="text-xs text-gray-500 mt-1">Currently tracked</div>
        </div>

        <div className="bg-gray-900 border border-gray-800 rounded-lg p-4">
          <div className="text-gray-400 text-sm mb-2">Avg Speed</div>
          <div className="text-2xl font-bold">
            {routeStats.count > 0
              ? (routeStats.totalSpeed / routeStats.count).toFixed(1)
              : '0'}
            <span className="text-sm text-gray-500 ml-1">mph</span>
          </div>
        </div>
      </div>

      {/* Delay Pattern Chart */}
      <div className="bg-gray-900 border border-gray-800 rounded-lg p-6">
        <h3 className="text-xl font-semibold mb-4">Delay Pattern by Hour of Day</h3>
        {delaysLoading ? (
          <div className="flex items-center justify-center h-64">
            <div className="text-gray-400">Loading delay data...</div>
          </div>
        ) : delayChartData.length > 0 ? (
          <ResponsiveContainer width="100%" height={400}>
            <LineChart data={delayChartData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
              <XAxis 
                dataKey="hour" 
                stroke="#9ca3af"
                label={{ value: 'Hour of Day', position: 'insideBottom', offset: -5, fill: '#9ca3af' }}
              />
              <YAxis 
                stroke="#9ca3af"
                label={{ value: 'Avg Delay (minutes)', angle: -90, position: 'insideLeft', fill: '#9ca3af' }}
              />
              <Tooltip 
                contentStyle={{ backgroundColor: '#1f2937', border: '1px solid #374151', borderRadius: '8px' }}
                labelStyle={{ color: '#fff' }}
              />
              <Legend />
              <Line 
                type="monotone" 
                dataKey="delay" 
                stroke="#10b981" 
                strokeWidth={2}
                name="Avg Delay (min)"
                dot={{ fill: '#10b981', r: 4 }}
              />
            </LineChart>
          </ResponsiveContainer>
        ) : (
          <div className="flex items-center justify-center h-64">
            <div className="text-gray-400">No delay data available for this route</div>
          </div>
        )}
      </div>

      {/* Headway Analysis */}
      {headway && headway.analysis && Object.keys(headway.analysis).length > 0 && (
        <div className="bg-gray-900 border border-gray-800 rounded-lg p-6">
          <h3 className="text-xl font-semibold mb-4">Headway Analysis</h3>
          {headwayLoading ? (
            <div className="text-gray-400">Loading headway data...</div>
          ) : (
            <div className="space-y-4">
              {Object.entries(headway.analysis).map(([routeId, data]) => (
                <div key={routeId} className="bg-black border border-gray-800 rounded-lg p-4">
                  <div className="flex justify-between items-center mb-2">
                    <span className="font-semibold">Route {routeId}</span>
                    <span className="text-sm text-gray-400">{data.count} headway measurements</span>
                  </div>
                  <div className="grid grid-cols-3 gap-4 text-sm">
                    <div>
                      <div className="text-gray-400">Average</div>
                      <div className="text-lg font-semibold">{data.avg_minutes.toFixed(1)} min</div>
                    </div>
                    <div>
                      <div className="text-gray-400">Minimum</div>
                      <div className="text-lg font-semibold">{data.min_minutes.toFixed(1)} min</div>
                    </div>
                    <div>
                      <div className="text-gray-400">Maximum</div>
                      <div className="text-lg font-semibold">{data.max_minutes.toFixed(1)} min</div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
