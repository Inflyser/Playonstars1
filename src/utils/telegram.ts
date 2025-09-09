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

export const isNativeTelegramApp = (): boolean => {
  if (typeof window === 'undefined') return false;
  
  const webApp = window.Telegram?.WebApp;
  if (!webApp) return false;
  
  // В нативных приложениях platform !== 'web'
  return webApp.platform !== 'web';
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


export const openTelegramLink = (url: string): boolean => {
  try {
    console.log('🔗 Opening link:', url);
    
    if (url.startsWith('tg://')) {
      // Deep link - используем location.href
      window.location.href = url;
      return true;
    } else {
      // Обычная ссылка
      if (window.Telegram?.WebApp?.openLink) {
        window.Telegram.WebApp.openLink(url);
      } else {
        window.open(url, '_blank', 'noopener,noreferrer');
      }
      return true;
    }
  } catch (err) {
    console.error('❌ Error opening link:', err);
    return false;
  }
};

export const isNativeTelegram = (): boolean => {
  const webApp = window.Telegram?.WebApp;
  return webApp?.platform !== 'web' && webApp?.platform !== undefined;
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

