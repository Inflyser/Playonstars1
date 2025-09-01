import { defineStore } from 'pinia';
import { connector } from '@/services/tonconnect';
import { api } from '@/services/api';

interface WalletState {
    isConnected: boolean;
    walletAddress: string | null;
    tonBalance: number;
    isLoading: boolean;
    isInitialized: boolean; // Добавляем флаг инициализации
}

export const useWalletStore = defineStore('wallet', {
    state: (): WalletState => ({
        isConnected: false,
        walletAddress: null,
        tonBalance: 0,
        isLoading: false,
        isInitialized: false // Инициализировано ли хранилище
    }),

    actions: {
        async init() {
            // Защита от повторной инициализации
            if (this.isInitialized) {
                console.log('✅ Wallet store already initialized');
                return;
            }

            this.isConnected = connector.connected;
            
            if (connector.connected && connector.wallet) {
                this.walletAddress = connector.wallet.account.address;
                await this.updateBalance();
            }

            connector.onStatusChange((wallet) => {
                this.isConnected = !!wallet;
                this.walletAddress = wallet?.account.address || null;
                if (wallet) {
                    this.updateBalance();
                }
            });

            this.isInitialized = true;
            console.log('✅ Wallet store initialized');
        },

        async connect() {
            this.isLoading = true;
            try {
                console.log('🔗 Opening TonConnect...');
                
                // Для Telegram WebApp используем openLink
                if (window.Telegram && window.Telegram.WebApp) {
                    window.Telegram.WebApp.openLink('https://app.tonkeeper.com/ton-connect');
                } else {
                    // Для браузера стандартное подключение
                    await connector.connect({
                        universalLink: 'https://app.tonkeeper.com/ton-connect',
                        bridgeUrl: 'https://bridge.tonapi.io/bridge'
                    });
                }
            } catch (error) {
                console.error('Connection error:', error);
                throw error;
            } finally {
                this.isLoading = false;
            }
        },

        disconnect() {
            connector.disconnect();
            this.isConnected = false;
            this.walletAddress = null;
            this.tonBalance = 0;
        },

        async updateBalance() {
            if (!this.walletAddress) return;
            
            try {
                const response = await api.get(`/wallet/balance/${this.walletAddress}`);
                this.tonBalance = response.data.balance;
            } catch (error) {
                console.error('Failed to update balance:', error);
            }
        },

        // Добавляем метод deposit если его нет
        async deposit(amount: number) {
            try {
                const response = await api.post('/wallet/deposit/verify', {
                    amount,
                    address: this.walletAddress
                });
                return response.data;
            } catch (error) {
                console.error('Failed to deposit:', error);
                throw error;
            }
        }
    },

    getters: {
        shortAddress: (state) => {
            if (!state.walletAddress) return '';
            return `${state.walletAddress.slice(0, 6)}...${state.walletAddress.slice(-4)}`;
        },
        formattedBalance: (state) => state.tonBalance.toFixed(2)
    }
});