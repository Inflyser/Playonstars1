import { defineStore } from 'pinia';
import { tonConnectUI } from '@/services/tonconnect'; // Импортируем UI-сервис
import { api } from '@/services/api';

interface WalletState {
    isConnected: boolean;
    walletAddress: string | null;
    tonBalance: number;
    isLoading: boolean;
}

export const useWalletStore = defineStore('wallet', {
    state: (): WalletState => ({
        isConnected: false,
        walletAddress: null,
        tonBalance: 0,
        isLoading: false
    }),

    actions: {
        // ГЛАВНЫЙ метод инициализации. Вызывается при загрузке приложения.
        async init(): Promise<void> {
            // Убираем вызов restoreConnection(), т.к. его нет в UI-библиотеке.
            // Вместо этого просто настраиваем обработчики событий.
            
            console.log('🔄 Инициализируем слушатели кошелька...');
            
            // 1. Подписываемся на изменения статуса кошелька
            tonConnectUI.onStatusChange((wallet) => {
                console.log('♻️ Статус кошелька изменился:', wallet ? 'Подключен' : 'Отключен');
                this.isConnected = !!wallet;
                this.walletAddress = wallet?.account.address || null;
                
                if (this.isConnected) {
                    console.log('✅ Кошелек подключен:', this.walletAddress);
                    this.updateBalance(); // Обновляем баланс
                    this.saveWalletToDB(); // Сохраняем в базу
                } else {
                    console.log('❌ Кошелек отключен');
                }
            });
            
            // 2. Сразу обновляем состояние на основе текущей сессии TonConnectUI
            // У tonConnectUI есть свойство `connected` и `wallet`
            this.isConnected = tonConnectUI.connected;
            this.walletAddress = tonConnectUI.wallet?.account.address || null;
            
            if (this.isConnected) {
                console.log('✅ Активная сессия кошелька восстановлена:', this.walletAddress);
                await this.updateBalance();
            }
            
            console.log('🎯 Инициализация кошелька завершена. Подключен:', this.isConnected);
        },

        // ПРОСТО открываем модальное окно для подключения
        connect(): void {
            console.log('🎯 Открываем модалку подключения кошелька');
            tonConnectUI.openModal(); // Используем встроенный метод открытия модалки:cite[3]
        },

        // Отключаем кошелек
        async disconnect(): Promise<void> {
            await tonConnectUI.disconnect(); // Этот метод есть в UI:cite[3]
            this.$reset(); // Чистим состояние хранилища
            console.log('✅ Кошелек отключен');
        },

        // Обновляем баланс (без изменений)
        async updateBalance(): Promise<void> {
            if (!this.walletAddress) return;
            try {
                const response = await api.get(`/api/wallet/balance/${this.walletAddress}`);
                this.tonBalance = response.data.balance;
            } catch (error) {
                console.error('Ошибка обновления баланса:', error);
            }
        },

        // Сохраняем кошелек в базу (без изменений)
        async saveWalletToDB(): Promise<boolean> {
            if (!this.walletAddress) return false;
            try {
                await api.post('/api/user/wallet', { wallet_address: this.walletAddress });
                return true;
            } catch (error) {
                console.error('Ошибка сохранения кошелька:', error);
                return false;
            }
        },

        // Отправляем транзакцию (для пополнения и вывода)
        async sendTransaction(toAddress: string, amountInNanotons: string): Promise<any> {
            const transaction = {
                validUntil: Math.floor(Date.now() / 1000) + 300, // 5 минут в Unix-времени:cite[4]
                messages: [
                    {
                        address: toAddress,
                        amount: amountInNanotons // Сумма уже в нанотонах!
                    }
                ]
            };
            // Используем метод sendTransaction из TonConnectUI:cite[4]
            return await tonConnectUI.sendTransaction(transaction);
        }
    },

    getters: {
        shortAddress: (state) => state.walletAddress ? `${state.walletAddress.slice(0, 6)}...${state.walletAddress.slice(-4)}` : '',
        formattedBalance: (state) => state.tonBalance.toFixed(2)
    }
});