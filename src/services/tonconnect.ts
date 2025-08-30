import TonConnect from '@tonconnect/sdk';

const manifestUrl = `${window.location.origin}/tonconnect-manifest.json`;

export const connector = new TonConnect({ 
    manifestUrl
    // Убираем несуществующие опции
});

export const initTonConnect = async () => {
    try {
        await connector.restoreConnection();
        console.log('✅ TonConnect initialized');
        return connector;
    } catch (error) {
        console.error('Failed to initialize TonConnect:', error);
        return connector;
    }
};

export const connectWallet = async () => {
    try {
        console.log('🔄 Starting wallet connection...');
        
        const connection = connector.connect({
            universalLink: 'https://app.tonkeeper.com/ton-connect',
            bridgeUrl: 'https://bridge.tonapi.io/bridge'
        });

        console.log('✅ Connection process started');
        return connection;
    } catch (error) {
        console.error('Connection error:', error);
        throw error;
    }
};

export const disconnectWallet = () => {
    connector.disconnect();
};

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