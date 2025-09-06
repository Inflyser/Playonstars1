import { api } from './api';

class TransactionMonitorService {
  private intervalId: number | null = null;
  private callbacks: ((txs: any[]) => void)[] = [];

  async startMonitoring(intervalMs = 30000) {
    if (this.intervalId) return; // Уже запущен

    const check = async () => {
      try {
        const response = await api.get('/api/wallet/check-deposits');
        const pendingTxs = response.data.pending_transactions || [];
        
        if (pendingTxs.length > 0) {
          this.callbacks.forEach(callback => callback(pendingTxs));
        }
      } catch (error) {
        console.error('Transaction monitoring error:', error);
      }
    };

    // Проверяем сразу и затем периодически
    await check();
    this.intervalId = window.setInterval(check, intervalMs);
  }

  stopMonitoring() {
    if (this.intervalId) {
      clearInterval(this.intervalId);
      this.intervalId = null;
    }
  }

  onNewTransactions(callback: (txs: any[]) => void) {
    this.callbacks.push(callback);
    
    // Возвращаем функцию для удаления callback
    return () => {
      this.callbacks = this.callbacks.filter(cb => cb !== callback);
    };
  }
}

// Создаем singleton экземпляр
export const transactionMonitor = new TransactionMonitorService();