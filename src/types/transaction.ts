export interface Transaction {
  id: number;
  tx_hash: string;
  amount: number;
  status: 'pending' | 'completed' | 'failed';
  transaction_type: 'deposit' | 'withdrawal';
  created_at: string;
  completed_at?: string;
}

export interface PendingTransaction {
  tx_hash: string;
  amount: number;
  created_at: string;
}

export interface TransactionResponse {
  pending_transactions: PendingTransaction[];
}