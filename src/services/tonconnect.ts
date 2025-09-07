import { TonConnect } from '@tonconnect/sdk';

const manifestUrl = `${window.location.origin}/tonconnect-manifest.json`;

export const connector = new TonConnect({
    manifestUrl,
    walletsListSource: 'https://raw.githubusercontent.com/ton-connect/wallets-list/main/wallets.json'
});

export const initTonConnect = async () => {
    try {
        // Восстанавливаем существующее соединение
        const connected = await connector.restoreConnection();
        
        // Подписываемся на изменения статуса
        connector.onStatusChange((wallet) => {
            console.log('Wallet status changed:', wallet);
        });
        
        console.log('✅ TonConnect initialized, connected:', connected);
        return connected;
    } catch (error) {
        console.error('❌ TonConnect init error:', error);
        return false;
    }
};