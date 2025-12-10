import { BrowserRouter, Routes, Route, NavLink } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ErrorBoundary } from './components/ErrorBoundary';
import { useKeyboardShortcuts } from './hooks/useKeyboardShortcuts';
import { useTheme } from './hooks/useTheme';
import Overview from './pages/Overview';
import LiveMap from './pages/LiveMap';
import RouteAnalytics from './pages/RouteAnalytics';
import TimeSeriesExplorer from './pages/TimeSeriesExplorer';
import { Map as MapIcon, BarChart3, LineChart, Activity, Sun, Moon } from 'lucide-react';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchInterval: 10000, // Refetch every 10 seconds for near real-time updates
      staleTime: 5000, // Data considered stale after 5 seconds
      retry: 2,
      retryDelay: (attemptIndex) => Math.min(500 * 2 ** attemptIndex, 10000), // Faster retries
    },
  },
});

function AppContent() {
  const { theme, toggleTheme } = useTheme();
  useKeyboardShortcuts(); // Can be called outside Router - uses window.location

  return (
    <BrowserRouter>
      <div className={`min-h-screen transition-colors duration-200 ${
        theme === 'dark' 
          ? 'bg-black text-white' 
          : 'bg-white text-gray-900'
      }`}>
        {/* Navigation */}
        <nav className={`border-b transition-colors duration-200 ${
          theme === 'dark' 
            ? 'border-gray-800 bg-gray-900' 
            : 'border-gray-200 bg-gray-100'
        }`}>
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex items-center justify-between h-16">
              <div className="flex items-center">
                <Activity className="h-8 w-8 text-green-500 mr-3" />
                <h1 className="text-xl font-bold">MBTA Telemetry Platform</h1>
              </div>
              <div className="flex items-center space-x-4">
                <div className="flex space-x-1">
                  <NavLink
                    to="/"
                    className={({ isActive }) =>
                      `px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                        isActive
                          ? 'bg-green-600 text-white'
                          : theme === 'dark'
                            ? 'text-gray-300 hover:bg-gray-800 hover:text-white'
                            : 'text-gray-600 hover:bg-gray-200 hover:text-gray-900'
                      }`
                    }
                    title="Overview (1)"
                  >
                    <div className="flex items-center">
                      <Activity className="h-4 w-4 mr-2" />
                      <span className="hidden sm:inline">Overview</span>
                    </div>
                  </NavLink>
                  <NavLink
                    to="/map"
                    className={({ isActive }) =>
                      `px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                        isActive
                          ? 'bg-green-600 text-white'
                          : theme === 'dark'
                            ? 'text-gray-300 hover:bg-gray-800 hover:text-white'
                            : 'text-gray-600 hover:bg-gray-200 hover:text-gray-900'
                      }`
                    }
                    title="Map (2)"
                  >
                    <div className="flex items-center">
                      <MapIcon className="h-4 w-4 mr-2" />
                      <span className="hidden sm:inline">Map</span>
                    </div>
                  </NavLink>
                  <NavLink
                    to="/analytics"
                    className={({ isActive }) =>
                      `px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                        isActive
                          ? 'bg-green-600 text-white'
                          : theme === 'dark'
                            ? 'text-gray-300 hover:bg-gray-800 hover:text-white'
                            : 'text-gray-600 hover:bg-gray-200 hover:text-gray-900'
                      }`
                    }
                    title="Analytics (3)"
                  >
                    <div className="flex items-center">
                      <BarChart3 className="h-4 w-4 mr-2" />
                      <span className="hidden sm:inline">Analytics</span>
                    </div>
                  </NavLink>
                  <NavLink
                    to="/timeseries"
                    className={({ isActive }) =>
                      `px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                        isActive
                          ? 'bg-green-600 text-white'
                          : theme === 'dark'
                            ? 'text-gray-300 hover:bg-gray-800 hover:text-white'
                            : 'text-gray-600 hover:bg-gray-200 hover:text-gray-900'
                      }`
                    }
                    title="Time Series (4)"
                  >
                    <div className="flex items-center">
                      <LineChart className="h-4 w-4 mr-2" />
                      <span className="hidden sm:inline">Time Series</span>
                    </div>
                  </NavLink>
                </div>
                <button
                  onClick={toggleTheme}
                  className={`p-2 rounded-md transition-colors ${
                    theme === 'dark'
                      ? 'text-gray-300 hover:bg-gray-800 hover:text-white'
                      : 'text-gray-600 hover:bg-gray-200 hover:text-gray-900'
                  }`}
                  title="Toggle theme"
                >
                  {theme === 'dark' ? <Sun className="h-5 w-5" /> : <Moon className="h-5 w-5" />}
                </button>
              </div>
            </div>
          </div>
        </nav>

        {/* Main Content */}
        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <Routes>
            <Route path="/" element={<Overview />} />
            <Route path="/map" element={<LiveMap />} />
            <Route path="/analytics" element={<RouteAnalytics />} />
            <Route path="/timeseries" element={<TimeSeriesExplorer />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  );
}

function App() {
  return (
    <ErrorBoundary>
      <QueryClientProvider client={queryClient}>
        <AppContent />
      </QueryClientProvider>
    </ErrorBoundary>
  );
}

export default App;