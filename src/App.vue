<template>
  <TelegramInit />
</template>

<script setup lang="ts">
import { onMounted } from 'vue';
import { useWalletStore } from '@/stores/useWalletStore';
import { initTonConnect } from '@/services/tonconnect'; // Правильный импорт

const walletStore = useWalletStore();

onMounted(async () => {
    // Инициализируем TonConnect
    await initTonConnect();
    // Инициализируем хранилище кошелька
    await walletStore.init();
});
</script>

<script lang="ts">
import TelegramInit from '@/components/layout/TelegramInit.vue';

export default {
    components: {
        TelegramInit
    }
}
</script>