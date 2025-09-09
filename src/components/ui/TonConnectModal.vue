<template>
  <TGModal v-model="isVisible" title="Connect TON Wallet" class="ton-connect-modal">
    <div class="modal-content">
      <div class="qr-section">
        <h3>Scan QR Code</h3>
        <div class="qr-code">
          <img :src="qrCodeUrl" alt="TON Connect QR Code" v-if="qrCodeUrl">
          <div class="qr-placeholder" v-else>
            <div class="spinner"></div>
            <span>Generating QR code...</span>
          </div>
        </div>
        <div v-if="!qrCodeUrl" class="injected-wallet-message">
          <p>🎉 Using injected wallet - no QR code needed</p>
          <p>Check your wallet app for connection request</p>
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
import { ref } from 'vue';
import { useWalletStore } from '@/stores/useWalletStore';
import { tonConnectService } from '@/services/tonconnect'; // ✅ Импортируем сервис

const isVisible = ref(false);
const qrCodeUrl = ref('');
const isConnecting = ref<string | null>(null);
const walletStore = useWalletStore();

const open = async () => {
  console.log('🚀 Opening TonConnect modal');
  isVisible.value = true;
  
  try {
    // ✅ Используем сервис вместо функции
    const universalLink = await tonConnectService.connect();
    
    if (universalLink) {
      // Создаем QR-код только если есть universal link
      qrCodeUrl.value = await generateQRCode(universalLink);
      console.log('✅ QR code generated successfully');
    } else {
      console.log('ℹ️ No QR code needed (injected wallet)');
      qrCodeUrl.value = ''; // Очищаем QR код
    }
  } catch (error) {
    console.error('❌ Error generating connection:', error);
    qrCodeUrl.value = '';
  }
};

const generateQRCode = async (url: string): Promise<string> => {
  try {
    // Используем API для генерации QR-кода на бэкенде
    const response = await fetch('/api/generate-qr', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ url })
    });
    
    if (response.ok) {
      const blob = await response.blob();
      return URL.createObjectURL(blob);
    }
    
    // Fallback: используем внешний сервис если бэкенд недоступен
    return `https://api.qrserver.com/v1/create-qr-code/?size=200x200&data=${encodeURIComponent(url)}`;
  } catch (error) {
    console.error('QR code generation failed, using fallback:', error);
    return `https://api.qrserver.com/v1/create-qr-code/?size=200x200&data=${encodeURIComponent(url)}`;
  }
};

const connectWith = async (walletType: 'tonkeeper' | 'telegram') => {
  console.log(`🔗 Connecting with: ${walletType}`);
  isConnecting.value = walletType;
  
  try {
    await walletStore.connectInTelegram(walletType);
    console.log('✅ Connection initiated successfully');
    
    // Закрываем модалку через 2 секунды
    setTimeout(() => {
      close();
    }, 2000);
    
  } catch (error) {
    console.error('❌ Connection failed:', error);
    isConnecting.value = null;
  }
};

const close = () => {
  isVisible.value = false;
  isConnecting.value = null;
  qrCodeUrl.value = '';
};

defineExpose({ open, close });
</script>

<style scoped>
.qr-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
  padding: 20px;
}

.spinner {
  width: 24px;
  height: 24px;
  border: 3px solid #f3f3f3;
  border-top: 3px solid #007bff;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}
</style>