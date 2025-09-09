import { TonConnect } from '@tonconnect/sdk';

// URL манифеста ДОЛЖЕН быть абсолютным и доступным
const manifestUrl = `${window.location.origin}/tonconnect-manifest.json`;

// Создаем единственный экземпляр коннектора
export const connector = new TonConnect({
    manifestUrl,
    walletsListSource: 'https://raw.githubusercontent.com/ton-connect/wallets-list/main/wallets.json'
});

// Функция для проверки возврата из кошелька
export const isTonConnectReturn = (): boolean => {
    const urlParams = new URLSearchParams(window.location.search);
    const hash = window.location.hash;
    
    return urlParams.has('tonconnect') || 
           hash.includes('tonconnect') ||
           urlParams.has('startattach') || 
           hash.includes('startattach');
};

// Обработка возврата из кошелька - КРИТИЧЕСКИ ВАЖНАЯ ФУНКЦИЯ
export const handleTonConnectReturn = async (): Promise<boolean> => {
    try {
        if (!isTonConnectReturn()) {
            return false;
        }

        console.log('🔄 Обнаружен возврат из кошелька, обрабатываем...');
        
        // ВАЖНО: Даем время для обработки deep link
        await new Promise(resolve => setTimeout(resolve, 800));
        
        // Восстанавливаем соединение
        await connector.restoreConnection();
        
        // Очищаем URL от параметров TonConnect
        const cleanUrl = window.location.origin + window.location.pathname;
        window.history.replaceState({}, document.title, cleanUrl);
        
        console.log('✅ Обработка возврата завершена, подключен:', connector.connected);
        return connector.connected;
        
    } catch (error) {
        console.error('❌ Ошибка при обработке возврата из кошелька:', error);
        return false;
    }
};

// Инициализация TonConnect
export const initTonConnect = async (): Promise<boolean> => {
    try {
        console.log('🚀 Инициализация TonConnect...');
        
        // Сначала обрабатываем возврат (если есть)
        const wasReturn = await handleTonConnectReturn();
        
        // Если не было возврата, просто восстанавливаем соединение
        if (!wasReturn) {
            await connector.restoreConnection();
        }
        
        // Подписываемся на изменения статуса
        connector.onStatusChange((wallet) => {
            console.log('🔔 Статус кошелька изменился:', 
                       wallet ? `Подключен: ${wallet.account.address}` : 'Отключен');
        });
        
        console.log('✅ TonConnect инициализирован, статус:', connector.connected);
        return connector.connected;
        
    } catch (error) {
        console.error('❌ Ошибка инициализации TonConnect:', error);
        return false;
    }
};

// Генерация ссылки для подключения
export const generateConnectionLink = async (): Promise<string> => {
    try {
        const universalLink = await connector.connect({
            universalLink: 'https://app.tonkeeper.com/ton-connect',
            bridgeUrl: 'https://bridge.tonapi.io/bridge'
        });
        return universalLink;
    } catch (error) {
        console.error('Ошибка генерации ссылки:', error);
        return 'https://app.tonkeeper.com/ton-connect';
    }
};