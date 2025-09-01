import TonConnect from '@tonconnect/sdk';

const manifestUrl = `${window.location.origin}/tonconnect-manifest.json`;

export const connector = new TonConnect({ manifestUrl });

export const initTonConnect = async () => {
    try {
        // Восстанавливаем соединение если было
        await connector.restoreConnection();
        console.log('✅ TonConnect initialized');
        return true;
    } catch (error) {
        console.error('❌ TonConnect init error:', error);
        return false;
    }
};