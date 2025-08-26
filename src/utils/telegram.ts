export const initTelegramWebApp = () => {
  if (typeof window.Telegram === 'undefined') {
    console.warn('Telegram WebApp not available');
    return false;
  }

  try {
    // Инициализируем Telegram WebApp
    window.Telegram.WebApp.ready();
    window.Telegram.WebApp.expand();
    
    console.log('Telegram WebApp initialized');
    return true;
  } catch (error) {
    console.error('Telegram init error:', error);
    return false;
  }
};

export const getTelegramInitData = (): string | null => {
  try {
    return window.Telegram?.WebApp?.initData || null;
  } catch (error) {
    console.error('Error getting initData:', error);
    return null;
  }
};