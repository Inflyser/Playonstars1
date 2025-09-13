// src/vue-shim.d.ts
import { type LanguageStore } from '@/stores/useLanguageStore'; // Предполагаемый путь

declare module 'vue' {
  interface ComponentCustomProperties {
    $t: (key: string) => string;
    $language: string; // Если вы также используете $language
  }
}