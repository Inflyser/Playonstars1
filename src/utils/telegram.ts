export const initTelegramWebApp = (): boolean => {
  if (typeof window === 'undefined' || typeof window.Telegram === 'undefined') {
    console.warn('Telegram WebApp not available');
    return false;
  }

  try {
    // Безопасно вызываем методы Telegram
    if (window.Telegram.WebApp?.ready) {
      window.Telegram.WebApp.ready();
    }
    
    if (window.Telegram.WebApp?.expand) {
      window.Telegram.WebApp.expand();
    }
    
    console.log('Telegram WebApp initialized successfully');
    return true;
  } catch (error) {
    console.warn('Telegram init warning:', error);
    return true; // Все равно продолжаем работу
  }
};

export const getTelegramInitData = (): string | null => {
  try {
    if (typeof window === 'undefined' || !window.Telegram?.WebApp) {
      return null;
    }
    return window.Telegram.WebApp.initData || null;
  } catch (error) {
    console.error('Error getting Telegram initData:', error);
    return null;
  }
};