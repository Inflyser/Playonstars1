import { defineStore } from 'pinia';
import { tonConnectUI, checkForTonConnectReturn } from '@/services/tonconnect'; // Импортируем новый сервис
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
            // 1. Проверяем, не вернулись ли мы только что из кошелька
            checkForTonConnectReturn();
            
            // 2. Восстанавливаем соединение с кошельком (если было)
            console.log('🔄 Восстанавливаем соединение с кошельком...');
            await tonConnectUI.restoreConnection();
            
            // 3. Настраиваем обработчик изменения статуса кошелька
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
            
            // 4. Сразу обновляем состояние на основе восстановленной сессии
            this.isConnected = tonConnectUI.connected;
            this.walletAddress = tonConnectUI.wallet?.account.address || null;
            console.log('🎯 Инициализация кошелька завершена. Подключен:', this.isConnected);
        },

        // ПРОСТО открываем модальное окно для подключения
        connect(): void {
            console.log('🎯 Открываем модалку подключения кошелька');
            tonConnectUI.openModal();
        },

        // Отключаем кошелек
        async disconnect(): Promise<void> {
            await tonConnectUI.disconnect();
            this.$reset(); // Чистим состояние хранилища
            console.log('✅ Кошелек отключен');
        },

        // Обновляем баланс
        async updateBalance(): Promise<void> {
            if (!this.walletAddress) return;
            try {
                const response = await api.get(`/api/wallet/balance/${this.walletAddress}`);
                this.tonBalance = response.data.balance;
            } catch (error) {
                console.error('Ошибка обновления баланса:', error);
            }
        },

        // Сохраняем кошелек в базу
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
        async sendTransaction(toAddress: string, amount: string): Promise<any> {
            const transaction = {
                validUntil: Math.floor(Date.now() / 1000) + 300, // 5 минут
                messages: [ { address: toAddress, amount: amount } ]
            };
            return await tonConnectUI.sendTransaction(transaction);
        }
    },

    getters: {
        shortAddress: (state) => state.walletAddress ? `${state.walletAddress.slice(0, 6)}...${state.walletAddress.slice(-4)}` : '',
        formattedBalance: (state) => state.tonBalance.toFixed(2)
    }
});