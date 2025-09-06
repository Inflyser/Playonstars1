<template>
  <TGModal v-model="isVisible" title="Connect TON Wallet" class="ton-connect-modal">
    <div class="modal-content">
      <!-- Упрощенная строка -->
      <div class="qr-section" v-if="universalLink">
        <h3>Scan QR Code</h3>
        <div class="qr-code">
          <img :src="generateQRCode(universalLink)" alt="TON Connect QR Code">
        </div>
        <p>Scan with your TON wallet app</p>
      </div>
      
      <div class="wallets-list">
        <h3>Connect with</h3>
        <div class="wallet-buttons">
          <button @click="connectWith('tonkeeper')" class="wallet-btn">
            <img src="@/assets/images/tonkeeper-icon.svg" alt="Tonkeeper">
            <span>Tonkeeper</span>
          </button>
          
          <button @click="connectWith('telegram')" class="wallet-btn">
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
import { openTelegramLink, isTelegramWebApp } from '@/utils/telegram';

const isVisible = ref(false);
const universalLink = ref('https://app.tonkeeper.com/ton-connect');

const generateQRCode = (link: string): string => {
  return `https://api.qrserver.com/v1/create-qr-code/?size=200x200&data=${encodeURIComponent(link)}`;
};

const open = () => {
  isVisible.value = true;
};

const connectWith = (walletType: 'tonkeeper' | 'telegram') => {
    const links = {
        tonkeeper: 'tg://resolve?domain=tonkeeper&startattach=tonconnect',
        telegram: 'tg://wallet?startattach=tonconnect'
    };
    
    openTelegramLink(links[walletType]);
    close();
};

const close = () => {
  isVisible.value = false;
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

.qr-code img {
  width: 100%;
  height: 100%;
  object-fit: contain;
}

.qr-placeholder {
  color: #666;
  font-size: 14px;
}

.wallet-buttons {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-top: 15px;
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

.wallet-btn span {
  font-weight: 500;
}
</style>