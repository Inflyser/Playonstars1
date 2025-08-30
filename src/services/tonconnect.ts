import TonConnect from '@tonconnect/sdk';

const manifestUrl = `${window.location.origin}/tonconnect-manifest.json`;

export const connector = new TonConnect({ manifestUrl });

// Инициализация connector
export const initTonConnect = async () => {
    try {
        await connector.restoreConnection();
        return connector;
    } catch (error) {
        console.error('Failed to initialize TonConnect:', error);
        return connector;
    }
};

// Подключение кошелька
export const connectWallet = async () => {
    try {
        const walletConnectionSource = {
            universalLink: 'https://app.tonkeeper.com/ton-connect',
            bridgeUrl: 'https://bridge.tonapi.io/bridge'
        };

        return connector.connect(walletConnectionSource);
    } catch (error) {
        console.error('Connection error:', error);
        throw error;
    }
};

// Отключение кошелька
export const disconnectWallet = () => {
    connector.disconnect();
};

// Отправка транзакции
export const sendTransaction = async (to: string, amount: string) => {
    try {
        const transaction = {
            validUntil: Math.floor(Date.now() / 1000) + 3600,
            messages: [
                {
                    address: to,
                    amount: amount
                }
            ]
        };

        return await connector.sendTransaction(transaction);
    } catch (error) {
        console.error('Transaction error:', error);
        throw error;
    }
};