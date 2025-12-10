/**
 * Helper utilities
 */

/**
 * Check if a timestamp is within the last N seconds (for "Live" indicators)
 */
export function isWithinSeconds(timestamp: string | Date, seconds: number): boolean {
  const date = typeof timestamp === 'string' ? new Date(timestamp) : timestamp;
  const now = new Date();
  const diff = (now.getTime() - date.getTime()) / 1000;
  return diff <= seconds;
}

/**
 * Format relative time (e.g., "2 seconds ago", "5 minutes ago")
 */
export function formatRelativeTime(timestamp: string | Date): string {
  const date = typeof timestamp === 'string' ? new Date(timestamp) : timestamp;
  const now = new Date();
  const diff = (now.getTime() - date.getTime()) / 1000;
  
  if (diff < 60) {
    return `${Math.floor(diff)} second${Math.floor(diff) !== 1 ? 's' : ''} ago`;
  } else if (diff < 3600) {
    const minutes = Math.floor(diff / 60);
    return `${minutes} minute${minutes !== 1 ? 's' : ''} ago`;
  } else if (diff < 86400) {
    const hours = Math.floor(diff / 3600);
    return `${hours} hour${hours !== 1 ? 's' : ''} ago`;
  } else {
    const days = Math.floor(diff / 86400);
    return `${days} day${days !== 1 ? 's' : ''} ago`;
  }
}

/**
 * Format file size for downloads
 */
export function formatFileSize(bytes: number): string {
  if (bytes === 0) return '0 Bytes';
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
}
