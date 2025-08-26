export const initTelegramWebApp = () => {
  if (typeof window.Telegram === 'undefined') {
    console.warn('Telegram WebApp not available');
    return false;
  }

  try {
    // Подавляем ошибки Telegram
    const originalConsoleError = console.error;
    console.error = (...args) => {
      // Игнорируем ошибки связанные с Telegram CSP
      if (typeof args[0] === 'string' && 
          (args[0].includes('Content Security Policy') || 
           args[0].includes('script-src') ||
           args[0].includes('gtmpx.com'))) {
        return; // Игнорируем эти ошибки
      }
      originalConsoleError.apply(console, args);
    };

    // Инициализируем Telegram WebApp
    window.Telegram.WebApp.ready();
    window.Telegram.WebApp.expand();
    
    console.log('Telegram WebApp initialized successfully');
    return true;
  } catch (error) {
    console.warn('Telegram init warning:', error);
    return true; // Все равно продолжаем работу
  }
};

export const getTelegramInitData = (): string | null => {
  try {
    if (typeof window.Telegram === 'undefined' || !window.Telegram.WebApp) {
      return null;
    }
    return window.Telegram.WebApp.initData || null;
  } catch (error) {
    console.error('Error getting Telegram initData:', error);
    return null;
  }
};