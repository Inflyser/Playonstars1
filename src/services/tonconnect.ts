// ЗАМЕНИТЕ весь файл на этот код:
import { TonConnect } from '@tonconnect/sdk';

const manifestUrl = `${window.location.origin}/tonconnect-manifest.json`;

export const connector = new TonConnect({
    manifestUrl,
    walletsListSource: 'https://raw.githubusercontent.com/ton-connect/wallets-list/main/wallets.json'
});

// Правильная обработка возврата из кошелька
export const handleTonConnectReturn = async (): Promise<boolean> => {
    try {
        // Проверяем наличие параметров TonConnect в URL
        const urlParams = new URLSearchParams(window.location.search);
        const hasTonConnect = urlParams.has('tonconnect') || 
                            window.location.hash.includes('tonconnect');
        
        if (!hasTonConnect) return false;

        console.log('🔄 Processing TonConnect return...');
        
        // Даем время для обработки
        await new Promise(resolve => setTimeout(resolve, 1000));
        
        // Восстанавливаем соединение
        await connector.restoreConnection();
        
        // Очищаем URL
        const cleanUrl = window.location.origin + window.location.pathname;
        window.history.replaceState({}, document.title, cleanUrl);
        
        return connector.connected;
    } catch (error) {
        console.error('❌ Failed to process TonConnect return:', error);
        return false;
    }
};

export const initTonConnect = async (): Promise<boolean> => {
    try {
        // Сначала обрабатываем возврат
        await handleTonConnectReturn();
        
        // Затем восстанавливаем обычное соединение
        await connector.restoreConnection();
        
        connector.onStatusChange((wallet) => {
            console.log('Wallet status changed:', wallet ? 'connected' : 'disconnected');
        });
        
        return connector.connected;
    } catch (error) {
        console.error('❌ TonConnect init error:', error);
        return false;
    }
};