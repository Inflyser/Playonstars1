import { defineStore } from 'pinia';
import { connector, initTonConnect, generateConnectionLink, handleTonConnectReturn } from '@/services/tonconnect';
import { api } from '@/services/api';
import { openTelegramLink, isTelegramWebApp } from '@/utils/telegram';

interface WalletState {
    isConnected: boolean;
    walletAddress: string | null;
    tonBalance: number;
    isLoading: boolean;
    isInitialized: boolean;
    connectionError: string | null;
}

export const useWalletStore = defineStore('wallet', {
    state: (): WalletState => ({
        isConnected: false,
        walletAddress: null,
        tonBalance: 0,
        isLoading: false,
        isInitialized: false,
        connectionError: null
    }),

    actions: {
        async init() {
            if (this.isInitialized) {
                console.log('✅ Wallet store уже инициализирован');
                return;
            }

            try {
                console.log('🔄 Инициализация хранилища кошелька...');
                this.isLoading = true;
                this.connectionError = null;

                // Инициализируем TonConnect
                const connected = await initTonConnect();
                this.isConnected = connected;
                
                if (connected && connector.wallet) {
                    this.walletAddress = connector.wallet.account.address;
                    console.log('💰 Кошелек подключен:', this.walletAddress);
                    
                    await this.updateBalance();
                    await this.saveWalletToDB();
                }

                // Подписываемся на изменения статуса
                connector.onStatusChange(async (wallet) => {
                    console.log('🔄 Изменение статуса кошелька обнаружено');
                    this.isConnected = !!wallet;
                    this.walletAddress = wallet?.account.address || null;

                    if (wallet) {
                        console.log('✅ Кошелек подключен/изменен:', wallet.account.address);
                        await this.updateBalance();
                        await this.saveWalletToDB();
                    } else {
                        console.log('❌ Кошелек отключен');
                        this.walletAddress = null;
                        this.tonBalance = 0;
                    }
                });

                this.isInitialized = true;
                console.log('✅ Хранилище кошелька инициализировано');

            } catch (error) {
                console.error('❌ Ошибка инициализации хранилища кошелька:', error);
                this.connectionError = 'Ошибка инициализации';
                this.isInitialized = false;
            } finally {
                this.isLoading = false;
            }
        },

        async connect() {
            try {
                console.log('🎯 Начало подключения кошелька...');
                this.isLoading = true;
                this.connectionError = null;

                if (isTelegramWebApp()) {
                    console.log('📱 Telegram WebApp - открываем кошелек...');
                    
                    // Для Telegram используем deep link
                    const deepLink = 'tg://wallet?startattach=tonconnect';
                    openTelegramLink(deepLink);
                    
                    // Ждем возврата из кошелька
                    setTimeout(async () => {
                        await this.checkConnectionAfterTimeout();
                    }, 3000);
                    
                } else {
                    console.log('🌐 Браузер - стандартное подключение...');
                    // Для браузера используем стандартное подключение
                    await connector.connect({
                        universalLink: 'https://app.tonkeeper.com/ton-connect',
                        bridgeUrl: 'https://bridge.tonapi.io/bridge'
                    });
                }

            } catch (error) {
                console.error('❌ Ошибка подключения кошелька:', error);
                this.connectionError = 'Ошибка подключения';
                throw error;
            } finally {
                this.isLoading = false;
            }
        },

        async checkConnectionAfterTimeout() {
            // Проверяем соединение после таймаута (для Telegram)
            setTimeout(async () => {
                try {
                    await connector.restoreConnection();
                    this.isConnected = connector.connected;
                    
                    if (connector.connected && connector.wallet) {
                        this.walletAddress = connector.wallet.account.address;
                        await this.updateBalance();
                        await this.saveWalletToDB();
                        console.log('✅ Кошелек подключен после таймаута');
                    }
                } catch (error) {
                    console.error('Ошибка проверки соединения:', error);
                }
            }, 2000);
        },

        async saveWalletToDB() {
            if (!this.isConnected || !this.walletAddress) {
                console.log('❌ Не могу сохранить: кошелек не подключен');
                return false;
            }

            try {
                console.log('💾 Сохранение кошелька в БД:', this.walletAddress);
                
                const response = await api.post('/api/user/wallet', {
                    wallet_address: this.walletAddress,
                    wallet_provider: 'tonconnect'
                });
                
                console.log('✅ Кошелек сохранен в БД:', response.data);
                return true;
                
            } catch (error: any) {
                console.error('❌ Ошибка сохранения кошелька в БД:', error);
                
                if (error.response) {
                    console.error('Детали ошибки:', error.response.data);
                }
                
                return false;
            }
        },

        async updateBalance() {
            if (!this.walletAddress) {
                console.log('❌ Не могу обновить баланс: нет адреса кошелька');
                return;
            }

            try {
                console.log('🔄 Обновление баланса для:', this.walletAddress);
                
                const response = await api.get(`/wallet/balance/${this.walletAddress}`);
                this.tonBalance = response.data.balance;
                
                console.log('✅ Баланс обновлен:', this.tonBalance, 'TON');
                
            } catch (error) {
                console.error('❌ Ошибка обновления баланса:', error);
                this.tonBalance = 0;
            }
        },

        disconnect() {
            console.log('🚪 Отключение кошелька...');
            connector.disconnect();
            this.isConnected = false;
            this.walletAddress = null;
            this.tonBalance = 0;
            console.log('✅ Кошелек отключен');
        }
    },

    getters: {
        shortAddress: (state) => {
            if (!state.walletAddress) return '';
            return `${state.walletAddress.slice(0, 6)}...${state.walletAddress.slice(-4)}`;
        },
        formattedBalance: (state) => state.tonBalance.toFixed(2),
        hasError: (state) => state.connectionError !== null
    }
});