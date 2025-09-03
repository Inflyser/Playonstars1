<template>
  <TGModal v-model="isVisible" title="Connect TON Wallet" class="ton-connect-modal">
    <div class="modal-content">
      <div class="qr-section" v-if="showQR">
        <h3>Scan QR Code</h3>
        <div class="qr-code">
          <!-- Здесь будет QR код -->
          <img :src="qrCodeUrl" alt="TON Connect QR Code" v-if="qrCodeUrl">
          <div class="qr-placeholder" v-else>
            <span>Loading QR code...</span>
          </div>
        </div>
        <p>Scan with your TON wallet app</p>
      </div>
      
      <div class="wallets-list">
        <h3>Connect with</h3>
        <div class="wallet-buttons">
          <button @click="connectTonKeeper" class="wallet-btn">
            <img src="@/assets/images/tonkeeper-icon.svg" alt="Tonkeeper">
            <span>Tonkeeper</span>
          </button>
          
          <button @click="connectTelegramWallet" class="wallet-btn">
            <img src="@/assets/images/telegram-icon.svg" alt="Telegram Wallet">
            <span>Telegram Wallet</span>
          </button>
        </div>
      </div>
    </div>
  </TGModal>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { connector } from '@/services/tonconnect';

const isVisible = ref(false);
const showQR = ref(false);
const qrCodeUrl = ref('');

const open = () => {
  isVisible.value = true;
  showQR.value = true;
  generateQRCode();
};

const close = () => {
  isVisible.value = false;
};

const generateQRCode = async () => {
  try {
    // TonConnect автоматически генерирует QR для десктоп версии
    console.log('Generating QR code for TonConnect');
  } catch (error) {
    console.error('Error generating QR code:', error);
  }
};

const connectTonKeeper = () => {
  // Открываем Tonkeeper прямо в Telegram
  if (window.Telegram?.WebApp) {
    window.Telegram.WebApp.openLink('https://app.tonkeeper.com/ton-connect');
  }
};

const connectTelegramWallet = () => {
  // Для Telegram Wallet
  if (window.Telegram?.WebApp) {
    window.Telegram.WebApp.openLink('tg://wallet?startattach=tonconnect');
  }
};

defineExpose({ open, close });
</script>

<style scoped>
.ton-connect-modal {
  max-width: 400px;
}

.modal-content {
  padding: 20px;
  text-align: center;
}

.qr-section {
  margin-bottom: 20px;
}

.qr-code {
  width: 200px;
  height: 200px;
  margin: 0 auto;
  border: 1px solid #ccc;
  display: flex;
  align-items: center;
  justify-content: center;
}

.wallet-buttons {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.wallet-btn {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  border: 1px solid #ddd;
  border-radius: 8px;
  background: white;
  cursor: pointer;
  transition: all 0.3s ease;
}

.wallet-btn:hover {
  background: #f5f5f5;
  border-color: #007bff;
}

.wallet-btn img {
  width: 24px;
  height: 24px;
}
</style>