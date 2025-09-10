<template>
  <TelegramInit />
</template>

<script lang="ts">
import TelegramInit from '@/components/layout/TelegramInit.vue';
import { transactionMonitor } from '@/services/transactionMonitor';


transactionMonitor.startMonitoring();
transactionMonitor.onNewTransactions((txs) => {
  console.log('New transactions:', txs);
});

export default {
  components: {
    TelegramInit
  }
}
</script>