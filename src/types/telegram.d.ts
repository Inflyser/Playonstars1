// telegram.d.ts - исправленная версия
declare namespace Telegram {
  // Добавляем тип для статуса инвойса
  type InvoiceStatus = 'paid' | 'cancelled' | 'failed' | 'pending';
  
  interface WebApp {
    // Основные свойства
    initData: string;
    initDataUnsafe: any;
    version: string;
    platform: string;
    colorScheme: string;
    themeParams: ThemeParams;
    isExpanded: boolean;
    viewportHeight: number;
    viewportStableHeight: number;
    headerColor: string;
    backgroundColor: string;
    
    // ✅ ДОБАВЛЯЕМ МЕТОД openInvoice
    openInvoice(url: string, callback?: (status: InvoiceStatus) => void): void;
    
    // Кнопки
    BackButton: BackButton;
    MainButton: MainButton;
    
    // Сервисы
    HapticFeedback: HapticFeedback;
    CloudStorage: CloudStorage;
    
    // Основные методы
    close(): void;
    expand(): void;
    ready(): void;
    openLink(url: string): void;
    showPopup(params: any): void;
    showAlert(message: string): void;
    showConfirm(message: string, callback: (confirmed: boolean) => void): void;
    
    // Дополнительные методы
    enableClosingConfirmation?(): void;
    disableClosingConfirmation?(): void;
    setHeaderColor?(color: string): void;
    setBackgroundColor?(color: string): void;
  }

  interface ThemeParams {
    bg_color: string;
    text_color: string;
    hint_color: string;
    link_color: string;
    button_color: string;
    button_text_color: string;
    secondary_bg_color: string;
  }

  interface BackButton {
    isVisible: boolean;
    onClick(callback: () => void): void;
    offClick(callback: () => void): void;
    show(): void;
    hide(): void;
  }

  interface MainButton {
    text: string;
    color: string;
    textColor: string;
    isVisible: boolean;
    isActive: boolean;
    isProgressVisible: boolean;
    onClick(callback: () => void): void;
    offClick(callback: () => void): void;
    show(): void;
    hide(): void;
    enable(): void;
    disable(): void;
    showProgress(leaveActive?: boolean): void;
    hideProgress(): void;
    setText(text: string): void;
  }

  interface HapticFeedback {
    impactOccurred(style: 'light' | 'medium' | 'heavy' | 'rigid' | 'soft'): void;
    notificationOccurred(type: 'error' | 'success' | 'warning'): void;
    selectionChanged(): void;
  }

  interface CloudStorage {
    setItem(key: string, value: string, callback?: (error: string | null) => void): void;
    getItem(key: string, callback: (error: string | null, value?: string) => void): void;
    getItems(keys: string[], callback: (error: string | null, values?: string[]) => void): void;
    removeItem(key: string, callback?: (error: string | null) => void): void;
    removeItems(keys: string[], callback?: (error: string | null) => void): void;
    getKeys(callback: (error: string | null, keys?: string[]) => void): void;
  }
}

declare global {
  interface Window {
    Telegram: {
      WebApp: Telegram.WebApp;
    };
    tonProtocol: any;
  }
}