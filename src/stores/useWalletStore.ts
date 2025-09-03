import { defineStore } from 'pinia';
import { connector } from '@/services/tonconnect';
import { api } from '@/services/api';
import { 
  openTelegramLink, 
  isTelegramWebApp,
  createTelegramDeepLink 
} from '@/utils/telegram';

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
                console.log('🔗 Starting wallet connection...');

                // ✅ Используем импортированную функцию isTelegramWebApp
                if (isTelegramWebApp()) {
                    console.log('📱 Using Telegram WebApp deep link...');

                    // ✅ Используем импортированную функцию createTelegramDeepLink
                    const deepLink = createTelegramDeepLink({
                        startattach: 'tonconnect',
                        ref: 'playonstars'
                    });

                    // ✅ Используем импортированную функцию openTelegramLink
                    openTelegramLink(deepLink);
                    console.log('✅ Deep link opened in Telegram');

                    return;
                }

                // ✅ Для браузера используем стандартный TonConnect
                console.log('🌐 Using standard TonConnect for browser...');
                await connector.connect({
                    universalLink: 'https://app.tonkeeper.com/ton-connect',
                    bridgeUrl: 'https://bridge.tonapi.io/bridge'
                });

            } catch (error) {
                console.error('❌ Connection error:', error);
                throw error;
            } finally {
                this.isLoading = false;
            }
        },

        // ✅ УДАЛЯЕМ дублирующиеся методы - используем импортированные
        // createTelegramDeepLink() - УДАЛЯЕМ, используем импортированную
        // isTelegramWebApp() - УДАЛЯЕМ, используем импортированную

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
        }

    }, // ← ЗАКРЫВАЕМ actions

    getters: {
        shortAddress: (state) => {
            if (!state.walletAddress) return '';
            return `${state.walletAddress.slice(0, 6)}...${state.walletAddress.slice(-4)}`;
        },
        formattedBalance: (state) => state.tonBalance.toFixed(2)
    }
}); // ← ЗАКРЫВАЕМ defineStore