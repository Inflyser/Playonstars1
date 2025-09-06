import { connector } from '@/services/tonconnect';

export const isTonConnectReturn = (): boolean => {
    const hash = window.location.hash;
    return hash.includes('tonconnect') || hash.includes('startattach');
};

export const handleTonConnectReturn = async (): Promise<boolean> => {
    if (!isTonConnectReturn()) return false;

    try {
        console.log('🔄 Processing TonConnect return...');
        
        // Даем время TonConnect обработать URL
        await new Promise(resolve => setTimeout(resolve, 500));
        
        // Восстанавливаем соединение
        await connector.restoreConnection();
        
        // Очищаем URL
        const cleanUrl = window.location.origin + window.location.pathname;
        window.history.replaceState({}, document.title, cleanUrl);
        
        console.log('✅ TonConnect return processed successfully');
        return true;
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