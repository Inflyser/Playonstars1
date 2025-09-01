import { defineStore } from 'pinia';
import { connector } from '@/services/tonconnect';
import { api } from '@/services/api';

interface WalletState {
    isConnected: boolean;
    walletAddress: string | null;
    tonBalance: number;
}

export const useWalletStore = defineStore('wallet', {
    state: (): WalletState => ({
        isConnected: false,
        walletAddress: null,
        tonBalance: 0
    }),

    actions: {
        async init() {
            // Простая инициализация
            this.isConnected = connector.connected;
            
            if (connector.connected && connector.wallet) {
                this.walletAddress = connector.wallet.account.address;
                await this.updateBalance();
            }

            // Слушаем изменения статуса
            connector.onStatusChange((wallet) => {
                this.isConnected = !!wallet;
                this.walletAddress = wallet?.account.address || null;
                if (wallet) {
                    this.updateBalance();
                }
            });
        },

        async connect() {
            try {
                console.log('🔗 Opening TonConnect...');
                
                // Для Telegram WebApp используем openLink
                if (window.Telegram && window.Telegram.WebApp) {
                    window.Telegram.WebApp.openLink('https://app.tonkeeper.com/ton-connect');
                    return;
                }
                
                // Для браузера стандартное подключение
                await connector.connect({
                    universalLink: 'https://app.tonkeeper.com/ton-connect',
                    bridgeUrl: 'https://bridge.tonapi.io/bridge'
                });
                
            } catch (error) {
                console.error('Connection error:', error);
                throw error;
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