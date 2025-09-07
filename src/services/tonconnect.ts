import { TonConnect } from '@tonconnect/sdk';

const manifestUrl = `${window.location.origin}/tonconnect-manifest.json`;

export const connector = new TonConnect({
    manifestUrl,
    walletsListSource: 'https://raw.githubusercontent.com/ton-connect/wallets-list/main/wallets.json'
});

export const isTonConnectReturn = (): boolean => {
    const hash = window.location.hash;
    const search = window.location.search;
    return hash.includes('tonconnect') || 
           hash.includes('startattach') ||
           search.includes('tonconnect') ||
           search.includes('startattach');
};

export const handleTonConnectReturn = async (): Promise<boolean> => {
    if (!isTonConnectReturn()) return false;

    try {
        console.log('🔄 Processing TonConnect return...');
        
        // Даем время TonConnect обработать URL
        await new Promise(resolve => setTimeout(resolve, 500));
        
        // Восстанавливаем соединение - этот метод не возвращает boolean!
        await connector.restoreConnection();
        
        // Очищаем URL
        const cleanUrl = window.location.origin + window.location.pathname;
        window.history.replaceState({}, document.title, cleanUrl);
        
        // Проверяем статус подключения через свойство connector.connected
        console.log('✅ TonConnect return processed, connected:', connector.connected);
        return connector.connected;
    } catch (error) {
        console.error('❌ Failed to process TonConnect return:', error);
        return false;
    }
};

export const getUniversalLink = (): string => {
    return 'https://app.tonkeeper.com/ton-connect';
};

export const createTelegramWalletLink = (): string => {
    return 'tg://wallet?startattach=tonconnect';
};

export const initTonConnect = async (): Promise<boolean> => {
    try {
        // Сначала обрабатываем возврат из кошелька (если есть)
        const wasReturn = await handleTonConnectReturn();
        
        // Если не было возврата, восстанавливаем обычное соединение
        if (!wasReturn) {
            await connector.restoreConnection();
        }
        
        // Подписываемся на изменения статуса
        connector.onStatusChange((wallet) => {
            console.log('Wallet status changed:', wallet ? 'connected' : 'disconnected');
        });
        
        console.log('✅ TonConnect initialized');
        return connector.connected; // ✅ Явно возвращаем boolean
    } catch (error) {
        console.error('❌ TonConnect init error:', error);
        return false; // ✅ Возвращаем false в случае ошибки
    }
};