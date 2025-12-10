import { useQuery } from '@tanstack/react-query';
import { apiClient, APIError } from '../lib/api';
import { Activity, Database, Clock, TrendingUp, AlertCircle } from 'lucide-react';
import { formatDistanceToNow } from 'date-fns';
import { MetricCardSkeleton } from '../components/SkeletonLoader';
import { isWithinSeconds } from '../utils/helpers';
import { useTheme } from '../hooks/useTheme';
import { getThemeClasses } from '../utils/themeClasses';

export default function Overview() {
  const { theme } = useTheme();
  const themeClasses = getThemeClasses(theme);
  
  const { data: health, isLoading: healthLoading, error: healthError } = useQuery({
    queryKey: ['health'],
    queryFn: () => apiClient.getHealth(),
    refetchInterval: 10000, // 10 seconds for real-time health status
    staleTime: 5000,
    retry: 2,
  });

  const { data: analytics, isLoading: analyticsLoading, error: analyticsError } = useQuery({
    queryKey: ['system-analytics'],
    queryFn: () => apiClient.getSystemAnalytics(),
    refetchInterval: 10000, // 10 seconds for real-time analytics
    staleTime: 5000,
    retry: 2,
  });

  const isLoading = healthLoading || analyticsLoading;
  const error = healthError || analyticsError;

  const getUptimePercentage = (uptimeSeconds: number) => {
    const days = uptimeSeconds / 86400;
    return days > 1 ? 99.9 : (uptimeSeconds / 86400) * 100;
  };

  if (isLoading) {
    return (
      <div className="space-y-6">
        <div>
          <h2 className={`text-3xl font-bold mb-2 ${themeClasses.textPrimary}`}>System Overview</h2>
          <p className={themeClasses.textSecondary}>Real-time telemetry monitoring dashboard</p>
        </div>
        <div className={`${themeClasses.bgCard} border ${themeClasses.borderCard} rounded-lg p-6 transition-colors duration-200`}>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {[1, 2, 3, 4].map((i) => (
              <MetricCardSkeleton key={i} />
            ))}
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    const errorMessage = error instanceof APIError ? error.message : 'Failed to load system status';
    return (
      <div className="space-y-6">
        <div>
          <h2 className={`text-3xl font-bold mb-2 ${themeClasses.textPrimary}`}>System Overview</h2>
        </div>
        <div className="bg-red-900/20 border border-red-800 rounded-lg p-6">
          <div className="flex items-center">
            <AlertCircle className="h-5 w-5 text-red-500 mr-3" />
            <div>
              <h3 className="text-lg font-semibold text-red-300">Error Loading Data</h3>
              <p className={`${themeClasses.textSecondary} text-sm mt-1`}>{errorMessage}</p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  const isHealthy = health?.status === 'healthy';
  const lastCollection = health?.last_collection
    ? new Date(health.last_collection)
    : null;
  const isLive = lastCollection && isWithinSeconds(lastCollection, 60); // Within last minute

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className={`text-3xl font-bold mb-2 ${themeClasses.textPrimary}`}>System Overview</h2>
          <p className={themeClasses.textSecondary}>Real-time telemetry monitoring dashboard</p>
        </div>
        {isLive && (
          <div className="flex items-center text-green-400 bg-green-900/20 px-3 py-1 rounded-full border border-green-800">
            <span className="h-2 w-2 bg-green-400 rounded-full mr-2 animate-pulse"></span>
            <span className="text-sm font-medium">Live</span>
          </div>
        )}
      </div>

      {/* System Status Card */}
      <div className={`${themeClasses.bgCard} border ${themeClasses.borderCard} rounded-lg p-6 transition-colors duration-200`}>
        <div className="flex items-center justify-between mb-4">
          <h3 className={`text-xl font-semibold flex items-center ${themeClasses.textPrimary}`}>
            <Activity className="h-5 w-5 mr-2 text-green-500" />
            System Status
          </h3>
          <div className="flex items-center space-x-2">
            {isLive && (
              <span className={`text-xs ${themeClasses.textSecondary}`}>
                Last updated: {lastCollection ? formatDistanceToNow(lastCollection, { addSuffix: true }) : 'Never'}
              </span>
            )}
            <div className={`px-3 py-1 rounded-full text-sm font-medium ${
              isHealthy ? 'bg-green-900 text-green-300' : 'bg-red-900 text-red-300'
            }`}>
              {isHealthy ? 'Healthy' : 'Unhealthy'}
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mt-6">
          <div className={`${themeClasses.bgInner} border ${themeClasses.borderCard} rounded-lg p-4 transition-colors duration-200`}>
            <div className="flex items-center justify-between mb-2">
              <span className={`${themeClasses.textSecondary} text-sm`}>Uptime</span>
              <TrendingUp className="h-4 w-4 text-green-500" />
            </div>
            <div className={`text-2xl font-bold ${themeClasses.textPrimary}`}>
              {health?.uptime_seconds
                ? `${getUptimePercentage(health.uptime_seconds).toFixed(1)}%`
                : 'N/A'}
            </div>
            <div className={`${themeClasses.textMuted} text-xs mt-1`}>
              {health?.uptime_seconds
                ? `${Math.floor(health.uptime_seconds / 3600)}h ${Math.floor((health.uptime_seconds % 3600) / 60)}m`
                : ''}
            </div>
          </div>

          <div className={`${themeClasses.bgInner} border ${themeClasses.borderCard} rounded-lg p-4 transition-colors duration-200`}>
            <div className="flex items-center justify-between mb-2">
              <span className={`${themeClasses.textSecondary} text-sm`}>Last Collection</span>
              <Clock className="h-4 w-4 text-blue-500" />
            </div>
            <div className={`text-2xl font-bold ${themeClasses.textPrimary}`}>
              {lastCollection
                ? formatDistanceToNow(lastCollection, { addSuffix: true })
                : 'Never'}
            </div>
            <div className={`${themeClasses.textMuted} text-xs mt-1`}>
              {lastCollection ? lastCollection.toLocaleTimeString() : ''}
            </div>
          </div>

          <div className={`${themeClasses.bgInner} border ${themeClasses.borderCard} rounded-lg p-4 transition-colors duration-200`}>
            <div className="flex items-center justify-between mb-2">
              <span className={`${themeClasses.textSecondary} text-sm`}>Vehicles Tracked</span>
              <Database className="h-4 w-4 text-purple-500" />
            </div>
            <div className={`text-2xl font-bold ${themeClasses.textPrimary}`}>{health?.vehicles_tracked || 0}</div>
            <div className={`${themeClasses.textMuted} text-xs mt-1`}>Real-time positions</div>
          </div>

          <div className={`${themeClasses.bgInner} border ${themeClasses.borderCard} rounded-lg p-4 transition-colors duration-200`}>
            <div className="flex items-center justify-between mb-2">
              <span className={`${themeClasses.textSecondary} text-sm`}>Collection Frequency</span>
              <Activity className="h-4 w-4 text-yellow-500" />
            </div>
            <div className="text-2xl font-bold">
              {analytics?.collection_frequency_seconds || 30}s
            </div>
            <div className={`${themeClasses.textMuted} text-xs mt-1`}>Update interval</div>
          </div>
        </div>
      </div>

      {/* Key Metrics Grid */}
      <div className={`${themeClasses.bgCard} border ${themeClasses.borderCard} rounded-lg p-6 transition-colors duration-200`}>
        <h3 className={`text-xl font-semibold mb-4 ${themeClasses.textPrimary}`}>Key Metrics</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <div className={`${themeClasses.bgInner} border ${themeClasses.borderCard} rounded-lg p-4 transition-colors duration-200`}>
            <div className={`${themeClasses.textSecondary} text-sm mb-2`}>Total Telemetry Events</div>
            <div className={`text-3xl font-bold ${themeClasses.textPrimary}`}>{analytics?.total_telemetry_events.toLocaleString() || 0}</div>
          </div>

          <div className={`${themeClasses.bgInner} border ${themeClasses.borderCard} rounded-lg p-4 transition-colors duration-200`}>
            <div className={`${themeClasses.textSecondary} text-sm mb-2`}>Routes Monitored</div>
            <div className={`text-3xl font-bold ${themeClasses.textPrimary}`}>{analytics?.routes_monitored || 0}</div>
          </div>

          <div className={`${themeClasses.bgInner} border ${themeClasses.borderCard} rounded-lg p-4 transition-colors duration-200`}>
            <div className={`${themeClasses.textSecondary} text-sm mb-2`}>Events Last Hour</div>
            <div className={`text-3xl font-bold ${themeClasses.textPrimary}`}>{analytics?.events_last_hour.toLocaleString() || 0}</div>
          </div>

          <div className={`${themeClasses.bgInner} border ${themeClasses.borderCard} rounded-lg p-4 transition-colors duration-200`}>
            <div className={`${themeClasses.textSecondary} text-sm mb-2`}>Data Points/Second</div>
            <div className={`text-3xl font-bold ${themeClasses.textPrimary}`}>{analytics?.events_per_second.toFixed(2) || '0.00'}</div>
          </div>
        </div>
      </div>

      {/* Recent Activity */}
      <div className={`${themeClasses.bgCard} border ${themeClasses.borderCard} rounded-lg p-6 transition-colors duration-200`}>
        <h3 className={`text-xl font-semibold mb-4 ${themeClasses.textPrimary}`}>Recent Activity</h3>
        <div className="space-y-2">
          {lastCollection && (
            <div className={`flex items-center justify-between p-3 ${themeClasses.bgInner} border ${themeClasses.borderCard} rounded transition-colors duration-200`}>
              <div className="flex items-center">
                <div className={`h-2 w-2 rounded-full mr-3 ${isLive ? 'bg-green-500 animate-pulse' : 'bg-gray-500'}`}></div>
                <span className={`text-sm ${themeClasses.textPrimary}`}>
                  Data collection successful
                  {isLive && <span className="ml-2 text-green-400 text-xs">(Live)</span>}
                </span>
              </div>
              <span className={`text-xs ${themeClasses.textMuted}`}>
                {formatDistanceToNow(lastCollection, { addSuffix: true })}
              </span>
            </div>
          )}
          {!isHealthy && (
            <div className={`flex items-center justify-between p-3 ${themeClasses.bgInner} border border-red-800 rounded transition-colors duration-200`}>
              <div className="flex items-center">
                <AlertCircle className="h-4 w-4 text-red-500 mr-3" />
                <span className="text-sm text-red-300">
                  System health check failed
                  {health?.message && <span className="ml-2 text-xs">({health.message})</span>}
                </span>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}