import { api } from './api'

export const starsService = {
  // Создание инвойса
  async createInvoice(amount: number, description: string = ''): Promise<any> {
    const response = await api.post('/stars/create-invoice', {
      amount,
      description
    })
    return response.data
  },

  // Прямое пополнение (для тестирования)
  async purchaseStars(amount: number): Promise<any> {
    const response = await api.post('/stars/purchase', {
      amount
    })
    return response.data
  },

  // История транзакций
  async getTransactionHistory(limit: number = 50): Promise<any> {
    const response = await api.get('/stars/transactions', {
      params: { limit }
    })
    return response.data
  },

  // Проверка статуса платежа
  async checkPaymentStatus(paymentId: string): Promise<any> {
    const response = await api.get(`/stars/payment-status/${paymentId}`)
    return response.data
  }


  
}

