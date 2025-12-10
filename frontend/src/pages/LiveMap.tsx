import { useEffect, useState, useMemo } from 'react';
import { useQuery } from '@tanstack/react-query';
import { MapContainer, TileLayer, Marker, Popup, Polyline, useMap } from 'react-leaflet';
import L from 'leaflet';
import { apiClient, Vehicle, APIError } from '../lib/api';
import 'leaflet/dist/leaflet.css';
import { MapPin, AlertCircle } from 'lucide-react';
import { useDebounce } from '../utils/debounce';
import { MapSkeleton } from '../components/SkeletonLoader';
import { useTheme } from '../hooks/useTheme';
import { getThemeClasses } from '../utils/themeClasses';

// Fix for default marker icons in React Leaflet
delete (L.Icon.Default.prototype as any)._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
});

// Route colors mapping
const ROUTE_COLORS: Record<string, string> = {
  'Red': '#da291c',
  'Orange': '#ed8b00',
  'Green': '#00843d',
  'Blue': '#003da5',
};

// Store vehicle paths for trails (last 10 positions per vehicle)
const vehiclePaths = new Map<string, Array<[number, number]>>();
const MAX_PATH_LENGTH = 10;

function MapAutoFit({ vehicles }: { vehicles: Vehicle[] }) {
  const map = useMap();
  
  useEffect(() => {
    if (vehicles.length > 0) {
      const validVehicles = vehicles.filter(v => v.latitude && v.longitude);
      if (validVehicles.length > 0) {
        const bounds = L.latLngBounds(
          validVehicles.map(v => [v.latitude!, v.longitude!])
        );
        map.fitBounds(bounds, { padding: [50, 50] });
      }
    }
  }, [vehicles, map]);
  
  return null;
}

function createCustomIcon(routeId: string | null) {
  const color = routeId && ROUTE_COLORS[routeId] ? ROUTE_COLORS[routeId] : '#888';
  
  return L.divIcon({
    className: 'custom-marker',
    html: `<div style="background-color: ${color}; width: 20px; height: 20px; border-radius: 50%; border: 3px solid white; box-shadow: 0 2px 4px rgba(0,0,0,0.3);"></div>`,
    iconSize: [20, 20],
    iconAnchor: [10, 10],
  });
}

export default function LiveMap() {
  const [selectedRoute, setSelectedRoute] = useState<string>('all');
  const [selectedStatus, setSelectedStatus] = useState<string>('all');
  const [showTrails, setShowTrails] = useState<boolean>(false);
  const { theme } = useTheme();
  const themeClasses = getThemeClasses(theme);
  
  // Debounce route selection to reduce API calls
  const debouncedRoute = useDebounce(selectedRoute, 300);

  const { data: vehicles, isLoading, error } = useQuery({
    queryKey: ['vehicles', debouncedRoute === 'all' ? undefined : debouncedRoute],
    queryFn: () => apiClient.getVehicles(debouncedRoute === 'all' ? undefined : debouncedRoute),
    refetchInterval: 10000, // 10 seconds for near real-time updates
    staleTime: 5000, // Consider stale after 5 seconds
    retry: 2,
  });

  // Update vehicle paths for trails
  useEffect(() => {
    if (vehicles) {
      vehicles.forEach(vehicle => {
        if (vehicle.latitude && vehicle.longitude) {
          const path = vehiclePaths.get(vehicle.vehicle_id) || [];
          path.push([vehicle.latitude, vehicle.longitude]);
          if (path.length > MAX_PATH_LENGTH) {
            path.shift();
          }
          vehiclePaths.set(vehicle.vehicle_id, path);
        }
      });
    }
  }, [vehicles]);

  const filteredVehicles = useMemo(() => {
    return vehicles?.filter(v => {
      if (selectedStatus !== 'all' && v.current_status !== selectedStatus) {
        return false;
      }
      return v.latitude && v.longitude;
    }) || [];
  }, [vehicles, selectedStatus]);

  const uniqueRoutes = useMemo(() => {
    return Array.from(new Set(vehicles?.map(v => v.route_id).filter(Boolean) || []));
  }, [vehicles]);

  // Default to Boston area if no vehicles
  const defaultCenter: [number, number] = [42.3601, -71.0589];

  if (isLoading && !vehicles) {
    return (
      <div className="space-y-4">
        <div>
          <h2 className="text-3xl font-bold mb-2">Live Vehicle Map</h2>
          <p className="text-gray-400">Real-time GPS positions of MBTA vehicles</p>
        </div>
        <MapSkeleton />
      </div>
    );
  }

  if (error) {
    const errorMessage = error instanceof APIError ? error.message : 'Failed to load vehicle positions';
    return (
      <div className="space-y-4">
        <div>
          <h2 className="text-3xl font-bold mb-2">Live Vehicle Map</h2>
        </div>
        <div className="bg-red-900/20 border border-red-800 rounded-lg p-6">
          <div className="flex items-center">
            <AlertCircle className="h-5 w-5 text-red-500 mr-3" />
            <div>
              <h3 className="text-lg font-semibold text-red-300">Error Loading Map</h3>
              <p className="text-gray-400 text-sm mt-1">{errorMessage}</p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div>
        <h2 className={`text-3xl font-bold mb-2 ${themeClasses.textPrimary}`}>Live Vehicle Map</h2>
        <p className={themeClasses.textSecondary}>Real-time GPS positions of MBTA vehicles</p>
      </div>

      {/* Filters */}
      <div className={`${themeClasses.bgCard} border ${themeClasses.borderCard} rounded-lg p-4 flex flex-wrap gap-4 transition-colors duration-200`}>
        <div className="flex items-center space-x-2">
          <label className={`text-sm ${themeClasses.textSecondary}`}>Route:</label>
          <select
            value={selectedRoute}
            onChange={(e) => setSelectedRoute(e.target.value)}
            className={`${themeClasses.bgInner} border ${themeClasses.borderCard} rounded px-3 py-1 text-sm ${themeClasses.textPrimary} focus:outline-none focus:border-green-500 transition-colors duration-200`}
          >
            <option value="all">All Routes</option>
            {uniqueRoutes.map(route => (
              <option key={route} value={route}>{route}</option>
            ))}
          </select>
        </div>

        <div className="flex items-center space-x-2">
          <label className={`text-sm ${themeClasses.textSecondary}`}>Status:</label>
          <select
            value={selectedStatus}
            onChange={(e) => setSelectedStatus(e.target.value)}
            className={`${themeClasses.bgInner} border ${themeClasses.borderCard} rounded px-3 py-1 text-sm ${themeClasses.textPrimary} focus:outline-none focus:border-green-500 transition-colors duration-200`}
          >
            <option value="all">All Status</option>
            <option value="IN_TRANSIT_TO">In Transit</option>
            <option value="STOPPED_AT">Stopped</option>
            <option value="INCOMING_AT">Incoming</option>
          </select>
        </div>

        <div className="flex items-center space-x-2">
          <input
            type="checkbox"
            id="showTrails"
            checked={showTrails}
            onChange={(e) => setShowTrails(e.target.checked)}
            className="rounded"
          />
          <label htmlFor="showTrails" className={`text-sm ${themeClasses.textSecondary}`}>Show Trails</label>
        </div>

        <div className="flex items-center space-x-2 ml-auto">
          <MapPin className="h-4 w-4 text-green-500" />
          <span className={`text-sm ${themeClasses.textSecondary}`}>
            Tracking <span className={`${themeClasses.textPrimary} font-semibold`}>{filteredVehicles.length}</span> vehicles
          </span>
        </div>
      </div>

      {/* Map Container */}
      <div className={`${themeClasses.bgCard} border ${themeClasses.borderCard} rounded-lg overflow-hidden transition-colors duration-200`} style={{ height: '600px' }}>
        <MapContainer
          center={defaultCenter}
          zoom={11}
          style={{ height: '100%', width: '100%' }}
          zoomControl={true}
        >
          <TileLayer
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          />
          
          {/* Vehicle trails */}
          {showTrails && filteredVehicles.map((vehicle) => {
            const path = vehiclePaths.get(vehicle.vehicle_id);
            if (path && path.length > 1) {
              const routeColor = vehicle.route_id && ROUTE_COLORS[vehicle.route_id] 
                ? ROUTE_COLORS[vehicle.route_id] 
                : '#888';
              return (
                <Polyline
                  key={`trail-${vehicle.vehicle_id}`}
                  positions={path}
                  color={routeColor}
                  weight={2}
                  opacity={0.6}
                  dashArray="5, 5"
                />
              );
            }
            return null;
          })}
          
          {/* Vehicle markers */}
          {filteredVehicles.map((vehicle) => (
            <Marker
              key={vehicle.id}
              position={[vehicle.latitude!, vehicle.longitude!]}
              icon={createCustomIcon(vehicle.route_id || null)}
            >
              <Popup>
                <div className="text-black p-2">
                  <div className="font-semibold">Vehicle: {vehicle.vehicle_id}</div>
                  {vehicle.route_name && (
                    <div className="text-sm text-gray-600">Route: {vehicle.route_name}</div>
                  )}
                  {vehicle.current_status && (
                    <div className="text-sm text-gray-600">Status: {vehicle.current_status.replace(/_/g, ' ')}</div>
                  )}
                  {vehicle.speed !== null && (
                    <div className="text-sm text-gray-600">Speed: {vehicle.speed.toFixed(1)} mph</div>
                  )}
                  {vehicle.bearing !== null && (
                    <div className="text-sm text-gray-600">Bearing: {vehicle.bearing}°</div>
                  )}
                </div>
              </Popup>
            </Marker>
          ))}
          
          <MapAutoFit vehicles={filteredVehicles} />
        </MapContainer>
      </div>
    </div>
  );
}