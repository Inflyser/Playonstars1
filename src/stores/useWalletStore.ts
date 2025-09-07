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
                
                // Генерируем ссылку для подключения
                const universalLink = connector.connect({
                    universalLink: 'https://t.me/wallet',
                    bridgeUrl: 'https://bridge.tonapi.io/bridge'
                });
                
                // Открываем в Telegram
                if (isTelegramWebApp()) {
                    openTelegramLink(`https://t.me/wallet?startattach=tonconnect`);
                } else {
                    window.open(universalLink, '_blank');
                }
                
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
            console.log('🔄 [WalletStore] Connect method called');
            this.isLoading = true;
            console.log('⏳ [WalletStore] Loading state set to true');
            
            try {
                console.log('📱 [WalletStore] Is Telegram environment:', isTelegramWebApp());
                
                if (isTelegramWebApp()) {
                    console.log('📲 [WalletStore] Telegram env - should open modal');
                    // Для Telegram модалка открывается из компонента
                } else {
                    console.log('🌐 [WalletStore] Browser env - connecting via TonConnect...');
                    await connector.connect({
                        universalLink: 'https://app.tonkeeper.com/ton-connect',
                        bridgeUrl: 'https://bridge.tonapi.io/bridge'
                    });
                    console.log('✅ [WalletStore] TonConnect connection successful');
                }
            } catch (error) {
                console.error('❌ [WalletStore] Connection error:', error);
                throw error;
            } finally {
                this.isLoading = false;
                console.log('⏳ [WalletStore] Loading state set to false');
            }
        },

        async sendTransaction(toAddress: string, amount: number, payload?: string) {
            this.isLoading = true;
            try {
                if (!this.isConnected || !connector.wallet) {
                    throw new Error('Wallet not connected');
                }

                const transaction = {
                    validUntil: Date.now() + 1000000,
                    messages: [
                        {
                            address: toAddress,
                            amount: Math.floor(amount * 1e9).toString(),
                            payload: payload ? btoa(payload) : undefined
                        }
                    ]
                };

                const result = await connector.sendTransaction(transaction);
                return result;
            } catch (error) {
                console.error('Transaction error:', error);
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