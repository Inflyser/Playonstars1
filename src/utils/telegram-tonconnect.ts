export const openTonConnectInTelegram = () => {
    if (window.Telegram && window.Telegram.WebApp) {
        // Используем Telegram WebApp метод для открытия ссылок
        window.Telegram.WebApp.openLink('https://app.tonkeeper.com/ton-connect');
        return true;
    }
    return false;
};

export const isTelegramWebApp = () => {
    return !!(window.Telegram && window.Telegram.WebApp);
};