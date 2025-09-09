import { TonConnect } from '@tonconnect/sdk';

class TonConnectService {
    private connector: TonConnect;
    private manifestUrl: string;

    constructor() {
        this.manifestUrl = `${window.location.origin}/tonconnect-manifest.json`;
        
        this.connector = new TonConnect({
            manifestUrl: this.manifestUrl,
            walletsListSource: 'https://raw.githubusercontent.com/ton-connect/wallets-list/main/wallets.json'
        });

        this.setupEventListeners();
    }

    private setupEventListeners(): void {
        this.connector.onStatusChange((wallet) => {
            console.log('🔄 Status changed:', wallet ? 'Connected' : 'Disconnected');
            
            if (wallet) {
                console.log('💰 Wallet address:', wallet.account.address);
                console.log('🔗 Chain:', wallet.account.chain);
                console.log('📱 Device:', wallet.device);
            }
        });
    }

    async init(): Promise<boolean> {
        try {
            console.log('🚀 Initializing TonConnect...');
            
            // Восстанавливаем соединение
            await this.connector.restoreConnection();
            
            // Обрабатываем возврат из кошелька
            await this.handleReturnFromWallet();
            
            console.log('✅ TonConnect initialized, connected:', this.connector.connected);
            return this.connector.connected;
            
        } catch (error) {
            console.error('❌ TonConnect init error:', error);
            return false;
        }
    }

    async connect(): Promise<string> {
        try {
            console.log('🔗 Starting connection process...');
            
            const universalLink = await this.connector.connect({
                jsBridgeKey: 'tonkeeper',
                universalLink: 'https://app.tonkeeper.com/ton-connect'
            });

            console.log('📱 Universal link generated:', universalLink);
            return universalLink;
            
        } catch (error) {
            console.error('❌ Connection error:', error);
            throw new Error('Failed to generate connection link');
        }
    }

    async handleReturnFromWallet(): Promise<boolean> {
        try {
            const urlParams = new URLSearchParams(window.location.search);
            const hash = window.location.hash;
            
            const isReturn = urlParams.has('tonconnect') || 
                           hash.includes('tonconnect') ||
                           urlParams.has('startattach') || 
                           hash.includes('startattach');

            if (!isReturn) {
                return false;
            }

            console.log('🔍 Detected return from wallet, processing...');
            
            // Даем время для обработки deep link
            await new Promise(resolve => setTimeout(resolve, 1000));
            
            // Восстанавливаем соединение
            await this.connector.restoreConnection();
            
            // Очищаем URL
            this.cleanUrl();
            
            console.log('✅ Return processing completed');
            return this.connector.connected;
            
        } catch (error) {
            console.error('❌ Error handling return:', error);
            return false;
        }
    }

    private cleanUrl(): void {
        const cleanUrl = window.location.origin + window.location.pathname;
        window.history.replaceState({}, document.title, cleanUrl);
        console.log('🧹 URL cleaned');
    }

    disconnect(): void {
        this.connector.disconnect();
        console.log('🔌 Disconnected');
    }

    getConnector(): TonConnect {
        return this.connector;
    }

    isConnected(): boolean {
        return this.connector.connected;
    }

    getWalletAddress(): string | null {
        return this.connector.wallet?.account.address || null;
    }
}

// Создаем singleton экземпляр
export const tonConnectService = new TonConnectService();