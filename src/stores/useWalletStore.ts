import { defineStore } from 'pinia';
import { connector } from '@/services/tonconnect';
import { api } from '@/services/api';
import { openTelegramLink, isTelegramWebApp } from '@/utils/telegram-webapp';

interface WalletState {
    isConnected: boolean;
    walletAddress: string | null;
    tonBalance: number;
    isLoading: boolean;
    isInitialized: boolean;
}

export const useWalletStore = defineStore('wallet', {
    state: (): WalletState => ({
        isConnected: false,
        walletAddress: null,
        tonBalance: 0,
        isLoading: false,
        isInitialized: false
    }),

    actions: {
        // ✅ ДОБАВЛЯЕМ метод init()
        async init() {
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
                
                if (this.isTelegramWebApp()) {
                    // ✅ СПЕЦИАЛЬНЫЙ URL для Telegram WebApp
                    const telegramDeepLink = `tg://wallet?startattach=tonconnect&ref=playonstars`;
                    
                    // ✅ Используем специальный метод для Telegram
                    if (window.Telegram?.WebApp?.openLink) {
                        window.Telegram.WebApp.openLink(telegramDeepLink);
                    } else {
                        window.open(telegramDeepLink, '_blank');
                    }
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
            } finally {
                this.isLoading = false;
            }
        },

        // Показываем модалку с QR кодом (если нужно)
        showTonConnectModal() {
            // Здесь можно показать кастомную модалку
            console.log('Showing TonConnect modal in Telegram');
        },

        // ✅ ДОБАВЛЯЕМ метод disconnect
        disconnect() {
            connector.disconnect();
            this.isConnected = false;
            this.walletAddress = null;
            this.tonBalance = 0;
            console.log('✅ Wallet disconnected');
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

        // ✅ ДОБАВЛЯЕМ метод isTelegramWebApp
        isTelegramWebApp(): boolean {
            return isTelegramWebApp();
        }
    },

    // ✅ ДОБАВЛЯЕМ геттеры
    getters: {
        shortAddress: (state) => {
            if (!state.walletAddress) return '';
            return `${state.walletAddress.slice(0, 6)}...${state.walletAddress.slice(-4)}`;
        },
        formattedBalance: (state) => state.tonBalance.toFixed(2)
    }
});