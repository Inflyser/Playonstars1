interface ImportMetaEnv {
    readonly VITE_WS_URL: string
    readonly VITE_APP_WALLET_ADDRESS: string
    readonly VITE_TON_API_KEY: string
    // Добавьте другие переменные которые используете
}

interface ImportMeta {
    readonly env: ImportMetaEnv
}