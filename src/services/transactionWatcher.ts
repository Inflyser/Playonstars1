import { api } from './api';
import { useUserStore } from '@/stores/useUserStore';
import { useWalletStore } from '@/stores/useWalletStore';

class TransactionWatcher {
    private intervalId: number | null = null;
    private watchedTransactions = new Set<string>();

    startWatching(intervalMs = 10000) {
        if (this.intervalId) return;

        this.intervalId = window.setInterval(() => {
            this.checkTransactions();
        }, intervalMs);
    }

    stopWatching() {
        if (this.intervalId) {
            clearInterval(this.intervalId);
            this.intervalId = null;
        }
    }

    async checkTransactions() {
        try {
            const response = await api.get('/api/wallet/check-deposits');
            const pendingTxs = response.data.pending_transactions || [];

            for (const tx of pendingTxs) {
                if (!this.watchedTransactions.has(tx.tx_hash)) {
                    this.watchedTransactions.add(tx.tx_hash);
                    this.watchTransaction(tx.tx_hash);
                }
            }
        } catch (error) {
            console.error('Transaction watch error:', error);
        }
    }

    async watchTransaction(txHash: string) {
        const maxAttempts = 30; // 5 минут при интервале 10 секунд
        let attempts = 0;

        const checkInterval = setInterval(async () => {
            try {
                attempts++;
                const response = await api.get(`/api/wallet/transaction/${txHash}`);
                const status = response.data.status;

                if (status === 'completed') {
                    clearInterval(checkInterval);
                    this.watchedTransactions.delete(txHash);
                    
                    // Обновляем балансы
                    const userStore = useUserStore();
                    const walletStore = useWalletStore();
                    
                    await userStore.fetchBalance();
                    await walletStore.updateBalance();
                    
                    console.log('✅ Transaction completed:', txHash);
                } else if (status === 'failed' || attempts >= maxAttempts) {
                    clearInterval(checkInterval);
                    this.watchedTransactions.delete(txHash);
                    console.log('❌ Transaction failed or timed out:', txHash);
                }
            } catch (error) {
                console.error('Transaction status check error:', error);
            }
        }, 10000);
    }
}

export const transactionWatcher = new TransactionWatcher();