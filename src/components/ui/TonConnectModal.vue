<template>
  <TGModal v-model="isVisible" title="Connect TON Wallet" class="ton-connect-modal">
    <div class="modal-content">
      <div class="qr-section" v-if="showQR">
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
import { openTelegramLink, isTelegramWebApp } from '@/utils/telegram'; // ✅ Добавляем импорт

const isVisible = ref(false);
const showQR = ref(false);
const qrCodeUrl = ref('');
const connectionSource = ref<any>(null);

const open = async () => {
  isVisible.value = true;
  showQR.value = true;
  await generateQRCode();
};

const close = () => {
  isVisible.value = false;
  // Отменяем подключение если модалка закрыта
  if (connectionSource.value) {
    connectionSource.value.close?.();
  }
};

const generateQRCode = async () => {
  try {
    console.log('🔗 Creating TonConnect connection...');
    
    // ✅ Создаем подключение через TonConnect
    connectionSource.value = connector.connect({
      jsBridgeKey: 'tonkeeper' // Ключ для Telegram WebApp
    });
    
    // ✅ Получаем universal link для QR кода
    const connection = await connectionSource.value;
    if (connection?.universalLink) {
      console.log('📱 Universal link for QR:', connection.universalLink);
      // Генерируем QR код из universalLink
      qrCodeUrl.value = `https://api.qrserver.com/v1/create-qr-code/?size=200x200&data=${encodeURIComponent(connection.universalLink)}`;
    }
    
  } catch (error) {
    console.error('❌ Error generating QR code:', error);
  }
};

const connectTonKeeper = () => {
  // ✅ Используем правильный deeplink для Telegram
  if (isTelegramWebApp()) {
    openTelegramLink('tg://resolve?domain=tonkeeper&startattach=tonconnect');
  } else {
    // Для браузера
    window.open('https://app.tonkeeper.com/ton-connect', '_blank');
  }
  close();
};

const connectTelegramWallet = () => {
  // ✅ Используем правильный deeplink
  if (isTelegramWebApp()) {
    openTelegramLink('tg://wallet?startattach=tonconnect&ref=playonstars');
  } else {
    // Для браузера
    window.open('tg://wallet?startattach=tonconnect', '_blank');
  }
  close();
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