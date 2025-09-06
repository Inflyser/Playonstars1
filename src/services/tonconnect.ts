import TonConnect from '@tonconnect/sdk';

const manifestUrl = `${window.location.origin}/tonconnect-manifest.json`;

// ✅ Создаем экземпляр connector, а не импортируем
export const connector = new TonConnect({ manifestUrl });

export const initTonConnect = async () => {
    try {
        await connector.restoreConnection();
        console.log('✅ TonConnect initialized');
        return true;
    } catch (error) {
        console.error('❌ TonConnect init error:', error);
        return false;
    }
};