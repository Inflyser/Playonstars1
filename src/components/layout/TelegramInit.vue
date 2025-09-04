<script setup lang="ts">
import { onMounted, ref, onUnmounted, watch } from 'vue';
import { useTelegram } from '@/composables/useTelegram';
import { initTelegramWebApp, getTelegramInitData, isTelegramWebApp } from '@/utils/telegram';
import { useUserStore } from '@/stores/useUserStore';
import { initTonConnect, connector } from '@/services/tonconnect';
import { useWalletStore } from '@/stores/useWalletStore';
import { useWebSocket } from '@/composables/useWebSocket';
import TGLoader from '@/components/ui/TGLoader.vue';
import AppLayout from '@/components/layout/AppLayout.vue';

const { initTelegram, fetchUserData, fetchBalance, isLoading, error } = useTelegram();
const userStore = useUserStore();
const walletStore = useWalletStore();
const { connect: connectWebSocket } = useWebSocket();
const isInitialized = ref(false);
const initializationError = ref<string | null>(null);

// ✅ Правильная обработка глубоких ссылок TonConnect
const handleTonConnectReturn = () => {
  if (!isTelegramWebApp()) return;

  const urlParams = new URLSearchParams(window.location.search);
  console.log('🔍 URL params:', Object.fromEntries(urlParams.entries()));

  // TonConnect возвращает параметры в hash, а не в search
  const hashParams = new URLSearchParams(window.location.hash.slice(1));
  const hasTonConnectParams = hashParams.has('tonconnect') || hashParams.has('startattach');
  
  console.log('📱 TonConnect return detected:', hasTonConnectParams);

  if (hasTonConnectParams) {
    // Очищаем URL чтобы избежать повторной обработки
    const cleanUrl = window.location.origin + window.location.pathname;
    window.history.replaceState({}, document.title, cleanUrl);

    // Даем время TonConnect обработать возврат
    setTimeout(() => {
      walletStore.init().then(() => {
        console.log('✅ Wallet initialized after TonConnect return');
      }).catch((err) => {
        console.error('❌ Failed to init wallet after return:', err);
      });
    }, 1000);
  }
};

// ✅ Слушаем изменения статуса кошелька
const setupWalletListeners = () => {
  connector.onStatusChange(async (wallet) => {
    console.log('🔄 Wallet status changed:', wallet ? 'connected' : 'disconnected');
    
    if (wallet) {
      // Обновляем баланс при подключении кошелька
      try {
        await walletStore.updateBalance();
        console.log('✅ Balance updated after wallet connection');
      } catch (err) {
        console.error('❌ Failed to update balance:', err);
      }
    }
  });
};

const retryInit = async () => {
  console.log('🔄 Retrying initialization...');
  isInitialized.value = false;
  initializationError.value = null;
  error.value = null;
  await initializeApp();
};

const initializeApp = async () => {
  console.log('🔐 Starting application initialization...');
  
  try {
    // 1. ✅ Сначала проверяем возврат из кошелька (ВАЖНО: до всей инициализации)
    handleTonConnectReturn();

    const isTelegram = initTelegramWebApp();
    console.log('📱 Is Telegram environment:', isTelegram);

    // 2. ✅ Инициализируем TonConnect (должно быть ПЕРВЫМ)
    console.log('🔗 Initializing TonConnect...');
    await initTonConnect();
    setupWalletListeners();
    await walletStore.init();

    // 3. ✅ Инициализируем Telegram (если в Telegram)
    if (isTelegram) {
      const initData = getTelegramInitData();
      console.log('📋 InitData available:', !!initData);
      
      if (initData) {
        console.log('🔐 Authenticating with Telegram...');
        const authSuccess = await initTelegram(initData);
        
        if (!authSuccess) {
          throw new Error('Telegram authentication failed');
        }
      }
    }

    // 4. ✅ Параллельно загружаем пользовательские данные (если авторизованы)
    const loadPromises = [];
    
    if (userStore.user || isTelegram) {
      loadPromises.push(
        fetchUserData().catch(err => 
          console.error('Failed to load user data:', err)
        ),
        fetchBalance().catch(err => 
          console.error('Failed to load balance:', err)
        )
      );
    }

    // 5. ✅ Подключаем WebSocket для реальных обновлений
    if (isTelegram) {
      loadPromises.push(
        connectWebSocket().catch(err =>
          console.error('Failed to connect WebSocket:', err)
        )
      );
    }

    await Promise.all(loadPromises);

    isInitialized.value = true;
    console.log('🎉 Application fully initialized');

  } catch (err) {
    console.error('❌ Initialization failed:', err);
    initializationError.value = err instanceof Error ? err.message : 'Unknown error';
  }
};

// ✅ Следим за изменениями авторизации для обновления данных
watch(() => userStore.user, (newUser) => {
  if (newUser && !isInitialized.value) {
    console.log('🔄 User data changed, updating...');
    fetchBalance().catch(err => console.error('Failed to update balance:', err));
  }
});

let originalHashChangeHandler: ((event: HashChangeEvent) => void) | null = null;

onMounted(async () => {
    // ✅ Сохраняем оригинальный обработчик через присваивание функции
    originalHashChangeHandler = window.onhashchange ? 
        (event: HashChangeEvent) => {
            if (window.onhashchange) {
                window.onhashchange.call(window, event);
            }
        } : null;

    // ✅ Создаем собственный обработчик
    const handleHashChange = (event: HashChangeEvent) => {
        console.log('📍 Hash changed:', window.location.hash);
        handleTonConnectReturn();
        
        // ✅ Вызываем оригинальный обработчик
        if (originalHashChangeHandler) {
            originalHashChangeHandler(event);
        }
    };

    // ✅ Устанавливаем через addEventListener
    window.addEventListener('hashchange', handleHashChange);
    
    await initializeApp();
});

onUnmounted(() => {
    // ✅ Не нужно восстанавливать onhashchange, т.к. мы использовали addEventListener
    // Просто очищаем ссылку
    originalHashChangeHandler = null;
});
</script>

<template>
  <div class="telegram-init-container">
    <!-- Показываем загрузчик/ошибку пока не инициализировано -->
    <div v-if="!isInitialized" class="init-status">
      <TGLoader v-if="isLoading && !initializationError" />
      
      <div v-else-if="initializationError" class="error-state">
        <div class="error-icon">⚠️</div>
        <h3>Initialization Failed</h3>
        <p>{{ initializationError }}</p>
        <button @click="retryInit" class="retry-btn">Try Again</button>
      </div>
      
      <div v-else class="loading-state">
        <div class="loading-spinner"></div>
        <p>Initializing application...</p>
      </div>
    </div>
    
    <!-- После инициализации показываем основное приложение -->
    <AppLayout v-else>
      <RouterView />
    </AppLayout>
  </div>
</template>

<style scoped>
.telegram-init-container {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.init-status {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  padding: 20px;
}

.error-state {
  text-align: center;
  color: #ff6b6b;
}

.error-icon {
  font-size: 48px;
  margin-bottom: 16px;
}

.retry-btn {
  margin-top: 16px;
  padding: 10px 20px;
  background: #007bff;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
}

.loading-state {
  text-align: center;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 3px solid #f3f3f3;
  border-top: 3px solid #007bff;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 16px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}
</style>