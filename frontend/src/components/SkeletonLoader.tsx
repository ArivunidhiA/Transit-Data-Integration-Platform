export function MetricCardSkeleton() {
  return (
    <div className="bg-black border border-gray-800 rounded-lg p-4 animate-pulse">
      <div className="h-4 bg-gray-700 rounded w-1/3 mb-2"></div>
      <div className="h-8 bg-gray-700 rounded w-1/2 mb-1"></div>
      <div className="h-3 bg-gray-700 rounded w-2/3"></div>
    </div>
  );
}

export function ChartSkeleton() {
  return (
    <div className="bg-gray-900 border border-gray-800 rounded-lg p-6 animate-pulse">
      <div className="h-6 bg-gray-700 rounded w-1/4 mb-4"></div>
      <div className="h-64 bg-gray-800 rounded"></div>
    </div>
  );
}

export function TableSkeleton({ rows = 5 }: { rows?: number }) {
  return (
    <div className="bg-gray-900 border border-gray-800 rounded-lg p-6 animate-pulse">
      <div className="h-6 bg-gray-700 rounded w-1/4 mb-4"></div>
      <div className="space-y-2">
        {Array.from({ length: rows }).map((_, i) => (
          <div key={i} className="h-12 bg-gray-800 rounded"></div>
        ))}
      </div>
    </div>
  );
}

export function MapSkeleton() {
  return (
    <div className="bg-gray-900 border border-gray-800 rounded-lg overflow-hidden animate-pulse" style={{ height: '600px' }}>
      <div className="h-full bg-gray-800"></div>
    </div>
  );
}
