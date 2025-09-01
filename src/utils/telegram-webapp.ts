export const openTelegramLink = (url: string): boolean => {
  try {
    if (typeof window !== 'undefined' && window.Telegram?.WebApp?.openLink) {
      window.Telegram.WebApp.openLink(url);
      return true;
    }
    
    // Fallback для браузера
    window.open(url, '_blank');
    return true;
    
  } catch (error) {
    console.error('Error opening link:', error);
    window.open(url, '_blank');
    return false;
  }
};

export const isTelegramWebApp = (): boolean => {
  return typeof window !== 'undefined' && !!(window.Telegram && window.Telegram.WebApp);
};

export const getTelegramWebApp = () => {
  return typeof window !== 'undefined' ? window.Telegram?.WebApp : null;
};