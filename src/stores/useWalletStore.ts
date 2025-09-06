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

        async connectInTelegram() {
            this.isLoading = true;
            try {
                console.log('📱 Connecting wallet in Telegram...');
            
                // ✅ Правильный способ: используем стандартные deep links
                const deepLink = isTelegramWebApp() 
                    ? 'tg://wallet?startattach=tonconnect'
                    : 'https://app.tonkeeper.com/ton-connect';
            
                console.log('🔗 Using deep link:', deepLink);
            
                // Открываем ссылку
                if (isTelegramWebApp()) {
                    openTelegramLink(deepLink);
                } else {
                    window.open(deepLink, '_blank');
                }
            
                // ✅ Просто инициируем подключение (без ожидания universalLink)
                connector.connect({
                    jsBridgeKey: 'tonkeeper'
                });
            
                return true;
            } catch (error) {
                console.error('❌ Telegram connection error:', error);
                throw error;
            } finally {
                this.isLoading = false;
            }
        },

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

        // В useWalletStore.ts добавьте:
        async sendTransactionInTelegram(toAddress: string, amount: number, payload?: string) {
            this.isLoading = true;
            try {
                if (!this.isConnected) {
                    throw new Error('Wallet not connected');
                }
                
                // Для Telegram используем deep link
                const nanoAmount = Math.floor(amount * 1e9).toString();
                const deepLink = `tg://wallet?startapp=transfer=${toAddress}_${nanoAmount}_${encodeURIComponent(payload || '')}`;
                
                openTelegramLink(deepLink);
                
                // Возвращаем mock результат для pending транзакции
                return {
                    boc: `pending_telegram_${Date.now()}`,
                    status: 'pending'
                };
                
            } catch (error) {
                console.error('Telegram transaction error:', error);
                throw error;
            } finally {
                this.isLoading = false;
            }
        },

        async sendTransaction(toAddress: string, amount: number, payload?: string) {
            this.isLoading = true;
            try {
                if (!this.isConnected || !connector.wallet) {
                    throw new Error('Wallet not connected');
                }
            
                const transaction = {
                    validUntil: Date.now() + 1000000, // 1000 секунд
                    messages: [
                        {
                            address: toAddress,
                            amount: Math.floor(amount * 1e9).toString(), // TON → нанотоны
                            payload: payload ? btoa(payload) : undefined
                        }
                    ]
                };
            
                console.log('Sending transaction:', transaction);
                
                const result = await connector.sendTransaction(transaction);
                console.log('Transaction result:', result);
                
                return result;
            } catch (error) {
                console.error('Transaction error:', error);
                throw error;
            } finally {
                this.isLoading = false;
            }
        },
        
        async waitForTransactionConfirmation(txHash: string, timeout: number = 60000) {
            const startTime = Date.now();
            
            return new Promise((resolve, reject) => {
                const checkInterval = setInterval(async () => {
                    try {
                        const response = await api.get(`/wallet/transaction/${txHash}`);
                        
                        if (response.data.status === 'completed') {
                            clearInterval(checkInterval);
                            resolve(true);
                        } else if (response.data.status === 'failed') {
                            clearInterval(checkInterval);
                            reject(new Error('Transaction failed'));
                        }
                        
                        if (Date.now() - startTime > timeout) {
                            clearInterval(checkInterval);
                            reject(new Error('Transaction timeout'));
                        }
                    } catch (error) {
                        // Продолжаем попытки при ошибках сети
                    }
                }, 3000);
            });
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