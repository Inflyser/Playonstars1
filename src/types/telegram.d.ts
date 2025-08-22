declare global {
  interface Window {
    Telegram: {
      WebApp: {
        initData: string
        initDataUnsafe: {
          user?: {
            id: number
            first_name: string
            username?: string
            language_code?: string
          }
        }
        ready: () => void
        expand: () => void
        showAlert: (message: string) => void
        sendData: (data: string) => void
        close: () => void
      }
    }
  }
}

export {}