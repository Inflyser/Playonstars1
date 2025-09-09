import { TonConnectUI } from '@tonconnect/ui';

// ВСЯ логика подключения здесь! Больше никаких сложных классов.
export const tonConnectUI = new TonConnectUI({
    manifestUrl: import.meta.env.VITE_APP_URL + '/tonconnect-manifest.json' // https://playonstars.netlify.app/tonconnect-manifest.json
});

// Вспомогательная функция для проверки возврата из кошелька
export const checkForTonConnectReturn = (): boolean => {
    const urlParams = new URLSearchParams(window.location.search);
    const hasReturn = urlParams.has('tonconnect') || urlParams.has('startattach');
    
    if (hasReturn) {
        console.log('🔍 Обнаружен возврат из кошелька. Очищаем URL.');
        // Очищаем URL от параметров TonConnect
        const cleanUrl = window.location.origin + window.location.pathname;
        window.history.replaceState({}, document.title, cleanUrl);
        return true;
    }
    return false;
};