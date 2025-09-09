<template>
  <button 
    @click="walletStore.connect()" 
    :disabled="walletStore.isLoading"
    class="connect-btn"
  >
    {{ walletStore.isConnected ? shortAddress : 'Connect Wallet' }}
  </button>
</template>

<script setup lang="ts">
import { useWalletStore } from '@/stores/useWalletStore';
import { storeToRefs } from 'pinia';

const walletStore = useWalletStore();
const { isConnected, shortAddress } = storeToRefs(walletStore);
</script>