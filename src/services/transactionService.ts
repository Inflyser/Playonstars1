// src/services/transactionService.ts
import { api } from './api';

export class TransactionService {
  static async checkPendingDeposits(): Promise<any[]> {
    try {
      const response = await api.get('/wallet/check-deposits');
      return response.data.pending_transactions || [];
    } catch (error) {
      console.error('Error checking deposits:', error);
      return [];
    }
  }

  static async monitorDeposits(callback: (txs: any[]) => void, interval = 30000) {
    const check = async () => {
      const txs = await this.checkPendingDeposits();
      if (txs.length > 0) {
        callback(txs);
      }
    };

    // Проверяем сразу при старте
    await check();
    
    // И каждые 30 секунд
    return setInterval(check, interval);
  }
}