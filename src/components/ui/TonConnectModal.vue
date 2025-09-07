<template>
  <TGModal v-model="isVisible" title="Connect TON Wallet" class="ton-connect-modal">
    <div class="modal-content">
      <div class="qr-section">
        <h3>Scan QR Code</h3>
        <div class="qr-code">
          <img :src="qrCodeUrl" alt="TON Connect QR Code" v-if="qrCodeUrl">
          <div class="qr-placeholder" v-else>
            <span>Loading QR code...</span>
          </div>
        </div>
        <p>Scan with your TON wallet app</p>
      </div>
      
      <div class="wallets-list">
        <h3>Or connect with</h3>
        <div class="wallet-buttons">
          <button 
            @click="connectWith('tonkeeper')" 
            class="wallet-btn" 
            :disabled="!!isConnecting">
          >
            <img src="@/assets/images/tonkeeper-icon.svg" alt="Tonkeeper">
            <span>Tonkeeper</span>
            <span v-if="isConnecting === 'tonkeeper'" class="connecting-spinner"></span>
          </button>
          
          <button 
            @click="connectWith('telegram')" 
            class="wallet-btn" 
            :disabled="!!isConnecting">
          >
            <img src="@/assets/images/telegram-icon.svg" alt="Telegram Wallet">
            <span>Telegram Wallet</span>
            <span v-if="isConnecting === 'telegram'" class="connecting-spinner"></span>
          </button>
        </div>
      </div>
    </div>
  </TGModal>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { useWalletStore } from '@/stores/useWalletStore';

const isVisible = ref(false);
const qrCodeUrl = ref('');
const isConnecting = ref<string | null>(null); // Может быть string или null
const walletStore = useWalletStore();

const open = async () => {
  console.log('🚀 [TonConnectModal] Modal opening...');
  isVisible.value = true;
  
  // Генерируем QR код при открытии
  try {
    const universalLink = await walletStore.generateConnectionLink();
    qrCodeUrl.value = `https://api.qrserver.com/v1/create-qr-code/?size=200x200&data=${encodeURIComponent(universalLink)}`;
  } catch (error) {
    console.error('Error generating QR code:', error);
    qrCodeUrl.value = '';
  }
};

const close = () => {
  console.log('🚪 [TonConnectModal] Modal closing');
  isVisible.value = false;
  isConnecting.value = null;
};

const connectWith = async (walletType: 'tonkeeper' | 'telegram') => {
  console.log(`🎯 [TonConnectModal] Connecting with: ${walletType}`);
  isConnecting.value = walletType;
  
  try {
    await walletStore.connectInTelegram(walletType);
    console.log('✅ [TonConnectModal] Connection initiated');
    
    // Закрываем модалку через секунду
    setTimeout(() => {
      close();
    }, 1000);
    
  } catch (error) {
    console.error('❌ [TonConnectModal] Connection failed:', error);
    isConnecting.value = null;
  }
};

defineExpose({ open, close });
</script>

<style scoped>
.connecting-spinner {
  width: 16px;
  height: 16px;
  border: 2px solid #f3f3f3;
  border-top: 2px solid #007bff;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-left: 8px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.wallet-btn:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}
</style>