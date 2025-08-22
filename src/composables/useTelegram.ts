import { ref, onMounted } from 'vue';

export const useTelegram = () => {
  const webApp = ref<any>(null);
  const user = ref<any>(null);
  const isReady = ref(false);

  const init = () => {
    // ВАЖНО: Проверяем что Telegram существует
    if (typeof window !== 'undefined' && window.Telegram?.WebApp) {
      webApp.value = window.Telegram.WebApp;
      user.value = webApp.value.initDataUnsafe?.user;
      
      // Проверяем что методы существуют
      if (webApp.value.expand) webApp.value.expand();
      if (webApp.value.ready) webApp.value.ready();
      
      isReady.value = true;
    }
  };

  const sendData = (data: any) => {
    if (webApp.value?.sendData) {
      webApp.value.sendData(JSON.stringify(data));
    }
  };

  onMounted(() => {
    init();
  });

  return {
    webApp,
    user,
    isReady,
    sendData,
    init
  };
};