// ✅ Импортируем из нашего файла, а не из @tonconnect/sdk
import { connector } from '@/services/tonconnect';

export class TonConnectHelper {
  static async generateConnectionLink(): Promise<string> {
    try {
      // Создаем подключение
      await connector.connect({
        jsBridgeKey: 'tonkeeper'
      });
      
      // Для QR кода используем стандартную ссылку
      return 'https://app.tonkeeper.com/ton-connect';
      
    } catch (error) {
      console.error('❌ Error generating connection link:', error);
      return 'https://app.tonkeeper.com/ton-connect';
    }
  }
  
  static getDefaultLinks() {
    return {
      tonkeeper: 'https://app.tonkeeper.com/ton-connect',
      telegram: 'tg://wallet?startattach=tonconnect',
      tonhub: 'https://tonhub.com/ton-connect'
    };
  }
  
  static getWalletDeepLink(walletType: 'tonkeeper' | 'telegram' | 'tonhub' = 'tonkeeper'): string {
    const links = {
      tonkeeper: 'tg://resolve?domain=tonkeeper&startattach=tonconnect',
      telegram: 'tg://wallet?startattach=tonconnect',
      tonhub: 'https://tonhub.com/ton-connect'
    };
    
    return links[walletType];
  }
}