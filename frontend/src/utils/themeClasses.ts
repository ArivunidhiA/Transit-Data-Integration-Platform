/**
 * Utility function to get theme-aware CSS classes
 */
export function getThemeClasses(theme: 'dark' | 'light') {
  return {
    bgMain: theme === 'dark' ? 'bg-black' : 'bg-white',
    bgCard: theme === 'dark' ? 'bg-gray-900' : 'bg-gray-50',
    bgInner: theme === 'dark' ? 'bg-black' : 'bg-white',
    borderCard: theme === 'dark' ? 'border-gray-800' : 'border-gray-200',
    textPrimary: theme === 'dark' ? 'text-white' : 'text-gray-900',
    textSecondary: theme === 'dark' ? 'text-gray-400' : 'text-gray-600',
    textMuted: theme === 'dark' ? 'text-gray-500' : 'text-gray-500',
    navBg: theme === 'dark' ? 'bg-gray-900' : 'bg-gray-100',
    navBorder: theme === 'dark' ? 'border-gray-800' : 'border-gray-200',
    linkInactive: theme === 'dark' ? 'text-gray-300 hover:bg-gray-800 hover:text-white' : 'text-gray-600 hover:bg-gray-200 hover:text-gray-900',
  };
}
