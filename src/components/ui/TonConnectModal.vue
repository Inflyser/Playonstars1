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
import { ref, onMounted } from 'vue';
import { openTelegramLink, isTelegramWebApp } from '@/utils/telegram';
import { connector } from '@/services/tonconnect'; // ✅ Импортируйте ваш connector

const isVisible = ref(false);
const qrCodeUrl = ref('');

const generateQRCode = (link: string): string => {
  return `https://api.qrserver.com/v1/create-qr-code/?size=200x200&data=${encodeURIComponent(link)}`;
};


const open = () => {
    console.log('🚀 [TonConnectModal] Modal open() method called');
    isVisible.value = true;
    console.log('✅ [TonConnectModal] Modal visibility set to true');
};

const close = () => {
    console.log('🚪 [TonConnectModal] Modal close() method called');
    isVisible.value = false;
};

const connectWith = (walletType: 'tonkeeper' | 'telegram') => {
    console.log(`🎯 [TonConnectModal] Connecting with: ${walletType}`);
    
    const links = {
        tonkeeper: 'tg://resolve?domain=tonkeeper&startattach=tonconnect',
        telegram: 'tg://wallet?startattach=tonconnect'
    };
    
    console.log('🔗 [TonConnectModal] Opening link:', links[walletType]);
    openTelegramLink(links[walletType]);
    console.log('✅ [TonConnectModal] Telegram link opened');
    
    close();
};



defineExpose({ open, close });
</script>