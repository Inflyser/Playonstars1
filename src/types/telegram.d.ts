declare namespace Telegram {
  interface WebApp {
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
    BackButton: BackButton;
    MainButton: MainButton;
    HapticFeedback: HapticFeedback;
    CloudStorage: CloudStorage;
    close(): void;
    expand(): void;
    ready(): void;
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
  }
}