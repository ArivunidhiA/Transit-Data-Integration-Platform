/**
 * Data export utilities
 */

export interface ExportOptions {
  format: 'csv' | 'json';
  filename?: string;
  dateRange?: {
    start: Date;
    end: Date;
  };
}

/**
 * Convert data to CSV format
 */
export function toCSV(data: any[], headers?: string[]): string {
  if (!data || data.length === 0) return '';
  
  // Get headers from first object if not provided
  const csvHeaders = headers || Object.keys(data[0]);
  
  // Create CSV rows
  const rows = [
    csvHeaders.join(','),
    ...data.map(row => 
      csvHeaders.map(header => {
        const value = row[header];
        // Escape commas and quotes in CSV
        if (value === null || value === undefined) return '';
        const stringValue = String(value);
        if (stringValue.includes(',') || stringValue.includes('"') || stringValue.includes('\n')) {
          return `"${stringValue.replace(/"/g, '""')}"`;
        }
        return stringValue;
      }).join(',')
    )
  ];
  
  return rows.join('\n');
}

/**
 * Export data to file
 */
export function exportToFile(content: string, filename: string, mimeType: string = 'text/plain') {
  const blob = new Blob([content], { type: mimeType });
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  window.URL.revokeObjectURL(url);
}

/**
 * Export vehicles data
 */
export function exportVehicles(vehicles: any[], options: ExportOptions) {
  const timestamp = new Date().toISOString().split('T')[0];
  const filename = options.filename || `vehicles_${timestamp}.${options.format}`;
  
  if (options.format === 'csv') {
    const csv = toCSV(vehicles);
    exportToFile(csv, filename, 'text/csv');
  } else {
    const json = JSON.stringify(vehicles, null, 2);
    exportToFile(json, filename, 'application/json');
  }
}

/**
 * Export time-series data
 */
export function exportTimeSeries(data: any[], options: ExportOptions) {
  const timestamp = new Date().toISOString().split('T')[0];
  const filename = options.filename || `timeseries_${timestamp}.${options.format}`;
  
  // Filter by date range if provided
  let filteredData = data;
  if (options.dateRange) {
    filteredData = data.filter(item => {
      const itemDate = new Date(item.timestamp || item.time);
      return itemDate >= options.dateRange!.start && itemDate <= options.dateRange!.end;
    });
  }
  
  if (options.format === 'csv') {
    const csv = toCSV(filteredData);
    exportToFile(csv, filename, 'text/csv');
  } else {
    const json = JSON.stringify(filteredData, null, 2);
    exportToFile(json, filename, 'application/json');
  }
}
