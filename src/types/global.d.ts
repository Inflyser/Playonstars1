declare global {
  interface Window {
    tonProtocol: any;
    Telegram: {
      WebApp: {
        initData: string;
        initDataUnsafe: any;
        expand: () => void;
        ready: () => void;
        close: () => void;
        showPopup: (params: any) => void;
        showAlert: (message: string) => void;
        showConfirm: (message: string, callback: (confirmed: boolean) => void) => void;
        MainButton: any;
        BackButton: any;
        // Добавьте другие методы по необходимости
      }
    }
  }
}

export {};