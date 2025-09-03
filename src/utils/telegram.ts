// Типы для Telegram WebApp
declare global {
  interface Window {
    Telegram?: {
      WebApp?: {
        // Основные методы
        ready: () => void;
        expand: () => void;
        openLink: (url: string) => void;
        close: () => void;
        
        // Данные
        initData: string;
        initDataUnsafe: any;
        version: string;
        platform: string;
        
        // Другие методы
        showPopup?: (params: any, callback?: (buttonId: string) => void) => void;
        MainButton?: any;
        BackButton?: any;
      };
    };
  }
}

/**
 * Инициализирует Telegram WebApp
 */
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
    
    console.log('✅ Telegram WebApp initialized successfully');
    return true;
  } catch (error) {
    console.warn('⚠️ Telegram init warning:', error);
    return false;
  }
};

/**
 * Получает initData из Telegram WebApp
 */
export const getTelegramInitData = (): string | null => {
  try {
    if (typeof window === 'undefined' || !window.Telegram?.WebApp) {
      return null;
    }
    return window.Telegram.WebApp.initData || null;
  } catch (error) {
    console.error('❌ Error getting Telegram initData:', error);
    return null;
  }
};

/**
 * Безопасно открывает ссылку в Telegram WebApp
 */
export const openTelegramLink = (url: string): boolean => {
  try {
    if (typeof window !== 'undefined' && window.Telegram?.WebApp?.openLink) {
      window.Telegram.WebApp.openLink(url);
      console.log('✅ Opened link in Telegram WebApp:', url);
      return true;
    }
    
    // Fallback для браузера
    window.open(url, '_blank');
    return true;
    
  } catch (error) {
    console.error('❌ Error opening link:', error);
    window.open(url, '_blank');
    return false;
  }
};

/**
 * Проверяет доступность Telegram WebApp
 */
export const isTelegramWebApp = (): boolean => {
  return typeof window !== 'undefined' && !!(window.Telegram && window.Telegram.WebApp);
};

/**
 * Возвращает экземпляр Telegram WebApp
 */
export const getTelegramWebApp = () => {
  return typeof window !== 'undefined' ? window.Telegram?.WebApp : null;
};

/**
 * Создает deeplink для Telegram Wallet
 */
export const createTelegramDeepLink = (params?: Record<string, string>): string => {
  const baseUrl = 'tg://wallet';
  const defaultParams = {
    startattach: 'tonconnect',
    ref: 'playonstars',
    callback: typeof window !== 'undefined' ? window.location.origin : ''
  };
  
  const urlParams = new URLSearchParams({ ...defaultParams, ...params });
  return `${baseUrl}?${urlParams.toString()}`;
};

