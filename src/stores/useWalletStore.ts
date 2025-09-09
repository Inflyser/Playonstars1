import { defineStore } from 'pinia';
import { tonConnectService } from '@/services/tonconnect'; // Импортируем сервис
import { api } from '@/services/api';
import { openTelegramLink, isTelegramWebApp } from '@/utils/telegram';

interface WalletState {
    isConnected: boolean;
    walletAddress: string | null;
    tonBalance: number;
    isLoading: boolean;
    isInitialized: boolean;
    connectionError: string | null;
    connectionStatus: 'disconnected' | 'connecting' | 'connected' | 'error';
}

export const useWalletStore = defineStore('wallet', {
    state: (): WalletState => ({
        isConnected: false,
        walletAddress: null,
        tonBalance: 0,
        isLoading: false,
        isInitialized: false,
        connectionError: null,
        connectionStatus: 'disconnected'
    }),

    actions: {
        async init(): Promise<void> {
            if (this.isInitialized) {
                console.log('✅ Wallet store already initialized');
                return;
            }

            try {
                console.log('🔄 Initializing wallet store...');
                this.connectionStatus = 'connecting';
                this.connectionError = null;

                // Инициализируем TonConnect через сервис
                const connected = await tonConnectService.init();
                this.isConnected = connected;
                
                if (connected) {
                    this.walletAddress = tonConnectService.getWalletAddress();
                    console.log('✅ Wallet connected during init:', this.walletAddress);
                    
                    await this.updateBalance();
                    await this.saveWalletToDB();
                }

                this.isInitialized = true;
                this.connectionStatus = this.isConnected ? 'connected' : 'disconnected';
                console.log('✅ Wallet store initialized successfully');
                
            } catch (error) {
                console.error('❌ Wallet store init error:', error);
                this.connectionError = 'Initialization failed';
                this.connectionStatus = 'error';
                this.isInitialized = false;
            }
        },

        async connect(): Promise<void> {
            try {
                console.log('🎯 Starting wallet connection...');
                this.isLoading = true;
                this.connectionStatus = 'connecting';
                this.connectionError = null;

                if (isTelegramWebApp()) {
                    console.log('📱 Telegram environment detected');
                    await this.connectInTelegram();
                } else {
                    console.log('🌐 Browser environment detected');
                    await this.connectInBrowser();
                }

            } catch (error: any) {
                console.error('❌ Connection error:', error);
                this.connectionError = error.message || 'Connection failed';
                this.connectionStatus = 'error';
                throw error;
            } finally {
                this.isLoading = false;
            }
        },

        async connectInTelegram(walletType: 'tonkeeper' | 'telegram' = 'telegram'): Promise<void> {
            try {
                console.log(`📱 Connecting via ${walletType} in Telegram...`);

                const links = {
                    tonkeeper: 'tg://resolve?domain=tonkeeper&startattach=tonconnect',
                    telegram: 'tg://wallet?startattach=tonconnect'
                };
            
                // Генерируем ссылку для подключения через сервис
                const universalLink = await tonConnectService.connect();

                if (universalLink) {
                    console.log('🔗 Generated universal link:', universalLink);
                    // Открываем deep link в Telegram
                    openTelegramLink(links[walletType]);
                } else {
                    console.log('ℹ️ Using injected wallet connection');
                    // Для injected wallet не нужен universal link
                }

                // Запускаем мониторинг статуса подключения
                this.startConnectionMonitoring();

            } catch (error) {
                console.error('❌ Telegram connection error:', error);
                throw new Error('Failed to connect via Telegram');
            }
        },

        async connectInBrowser(): Promise<void> {
            try {
                console.log('🌐 Connecting in browser...');
                
                const universalLink = await tonConnectService.connect();
                
                if (universalLink) {
                    console.log('🔗 Universal link for browser:', universalLink);
                    // Открываем в новом окне для браузера
                    window.open(universalLink, '_blank', 'noopener,noreferrer');
                } else {
                    console.log('ℹ️ Using injected wallet connection in browser');
                    // Для injected wallet ничего дополнительно делать не нужно
                }
                
                this.startConnectionMonitoring();
                
            } catch (error) {
                console.error('❌ Browser connection error:', error);
                throw new Error('Failed to connect in browser');
            }
        },

        startConnectionMonitoring(): void {
            // Сохраняем ссылку на интервал для очистки
            let checkInterval: number;
            let timeoutId: number;

            const cleanup = () => {
                if (checkInterval) clearInterval(checkInterval);
                if (timeoutId) clearTimeout(timeoutId);
            };

            // Мониторим изменение статуса
            checkInterval = window.setInterval(async () => {
                try {
                    const isConnected = await this.checkConnection();
                    
                    if (isConnected) {
                        cleanup();
                        console.log('✅ Wallet connected successfully');
                    }
                    
                } catch (error) {
                    console.error('❌ Connection check error:', error);
                }
            }, 3000); // Проверяем каждые 3 секунды

            // Таймаут через 2 минуты
            timeoutId = window.setTimeout(() => {
                cleanup();
                if (!this.isConnected) {
                    this.connectionStatus = 'error';
                    this.connectionError = 'Connection timeout';
                    console.log('⏰ Connection monitoring timeout');
                }
            }, 120000);
        },

        async saveWalletToDB(): Promise<boolean> {
            if (!this.walletAddress) {
                console.log('❌ No wallet address to save');
                return false;
            }

            try {
                console.log('💾 Saving wallet to DB:', this.walletAddress);
                
                const response = await api.post('/api/user/wallet', {
                    wallet_address: this.walletAddress,
                    wallet_provider: 'tonconnect',
                    network: 'mainnet'
                });
                
                console.log('✅ Wallet saved to DB:', response.data);
                return true;
                
            } catch (error: any) {
                console.error('❌ Error saving wallet to DB:', error);
                return false;
            }
        },

        async updateBalance(): Promise<void> {
            if (!this.walletAddress) {
                console.log('❌ No wallet address for balance check');
                return;
            }

            try {
                console.log('🔄 Updating balance for:', this.walletAddress);
                
                const response = await api.get(`/api/wallet/balance/${this.walletAddress}`);
                this.tonBalance = response.data.balance;
                
                console.log('✅ Balance updated:', this.tonBalance, 'TON');
                
            } catch (error) {
                console.error('❌ Balance update error:', error);
            }
        },

        disconnect(): void {
            console.log('🚪 Disconnecting wallet...');
            tonConnectService.disconnect();
            
            this.isConnected = false;
            this.walletAddress = null;
            this.tonBalance = 0;
            this.connectionStatus = 'disconnected';
            
            console.log('✅ Wallet disconnected');
        },

        async checkConnection(): Promise<boolean> {
            try {
                // Используем сервис для проверки соединения
                await tonConnectService.init();
                this.isConnected = tonConnectService.isConnected();
                
                if (this.isConnected) {
                    this.walletAddress = tonConnectService.getWalletAddress();
                    await this.updateBalance();
                }
                
                return this.isConnected;
                
            } catch (error) {
                console.error('❌ Connection check error:', error);
                return false;
            }
        }
    },

    getters: {
        shortAddress: (state) => {
            if (!state.walletAddress) return '';
            return `${state.walletAddress.slice(0, 6)}...${state.walletAddress.slice(-4)}`;
        },
        formattedBalance: (state) => state.tonBalance.toFixed(2),
        connectionState: (state) => state.connectionStatus,
        hasError: (state) => state.connectionError !== null
    }
});