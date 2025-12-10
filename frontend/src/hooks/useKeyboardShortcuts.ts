import { useEffect } from 'react';

export function useKeyboardShortcuts() {
  useEffect(() => {
    const handleKeyPress = (event: KeyboardEvent) => {
      // Don't trigger shortcuts if user is typing in an input
      if (
        event.target instanceof HTMLInputElement ||
        event.target instanceof HTMLTextAreaElement ||
        event.target instanceof HTMLSelectElement
      ) {
        return;
      }

      // Check for modifier keys
      const isModifier = event.ctrlKey || event.metaKey || event.altKey;

      // Navigation shortcuts (no modifier)
      // Use window.location for navigation (works without Router context)
      switch (event.key.toLowerCase()) {
        case '1':
          if (!isModifier) {
            if (window.location.pathname !== '/') {
              window.location.href = '/';
            }
            event.preventDefault();
          }
          break;
        case '2':
          if (!isModifier) {
            if (window.location.pathname !== '/map') {
              window.location.href = '/map';
            }
            event.preventDefault();
          }
          break;
        case '3':
          if (!isModifier) {
            if (window.location.pathname !== '/analytics') {
              window.location.href = '/analytics';
            }
            event.preventDefault();
          }
          break;
        case '4':
          if (!isModifier) {
            if (window.location.pathname !== '/timeseries') {
              window.location.href = '/timeseries';
            }
            event.preventDefault();
          }
          break;
        case '?':
          if (!isModifier) {
            // Show keyboard shortcuts help (could open a modal)
            alert('Keyboard Shortcuts:\n1 - Overview\n2 - Map\n3 - Analytics\n4 - Time Series');
          }
          break;
      }
    };

    window.addEventListener('keydown', handleKeyPress);
    return () => {
      window.removeEventListener('keydown', handleKeyPress);
    };
  }, []);
}
