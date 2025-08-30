import { defineStore } from 'pinia';
import { connector, connectWallet, disconnectWallet } from '@/services/tonconnect';
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
        async init() {
            this.isConnected = connector.connected;
            if (connector.connected && connector.wallet) {
                this.walletAddress = connector.wallet.account.address;
                await this.updateBalance();
            }

            connector.onStatusChange((wallet) => {
                this.isConnected = !!wallet;
                this.walletAddress = wallet?.account.address || null;
                
                if (wallet) {
                    this.linkWalletToBackend(wallet.account.address);
                    this.updateBalance();
                }
            });
        },

        async connect() {
            this.isLoading = true;
            try {
                await connectWallet();
            } catch (error) {
                console.error('Failed to connect wallet:', error);
                throw error;
            } finally {
                this.isLoading = false;
            }
        },

        async disconnect() {
            disconnectWallet();
            this.isConnected = false;
            this.walletAddress = null;
            this.tonBalance = 0;
        },

        async linkWalletToBackend(address: string) {
            try {
                await api.post('/wallet/connect', { address });
            } catch (error) {
                console.error('Failed to link wallet to backend:', error);
            }
        },

        async updateBalance() {
            if (!this.walletAddress) return;
            
            try {
                const response = await api.get(`/wallet/balance/${this.walletAddress}`);
                this.tonBalance = response.data.balance;
            } catch (error) {
                console.error('Failed to update balance:', error);
            }
        },

        async deposit(amount: number) {
            try {
                const response = await api.post('/wallet/deposit/verify', {
                    amount,
                    address: this.walletAddress
                });
                return response.data;
            } catch (error) {
                console.error('Failed to deposit:', error);
                throw error;
            }
        },

        async withdraw(amount: number, address: string) {
            try {
                const response = await api.post('/wallet/withdraw', {
                    amount,
                    address
                });
                return response.data;
            } catch (error) {
                console.error('Failed to withdraw:', error);
                throw error;
            }
        }
    },

    getters: {
        shortAddress: (state) => {
            if (!state.walletAddress) return '';
            return `${state.walletAddress.slice(0, 6)}...${state.walletAddress.slice(-4)}`;
        },
        formattedBalance: (state) => state.tonBalance.toFixed(2)
    }
});