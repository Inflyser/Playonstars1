import { ref, onUnmounted } from 'vue'
import { useUserStore } from '@/stores/useUserStore'
import { useWalletStore } from '@/stores/useWalletStore'
import { useGameStore } from '@/stores/useGameStore'
import { api } from '@/services/api'

interface WebSocketCallbacks {
  onNewBet?: (betData: any) => void
  onBetHistory?: (historyData: any[]) => void
}

export const useWebSocket = (callbacks: WebSocketCallbacks = {}) => {
    const socket = ref<WebSocket | null>(null)
    const isConnected = ref(false)
    const reconnectAttempts = ref(0)
    const maxReconnectAttempts = 5

    const getWebSocketUrl = (): string => {
        const envUrl = import.meta.env.VITE_WS_URL;
        
        // Если в .env есть правильный URL - используем его
        if (envUrl && envUrl.startsWith('wss://')) {
            return envUrl;
        }
        
        // Fallback: автоматически определяем URL на основе текущего хоста
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const host = window.location.host;
        
        // ✅ Подключаемся к БАЗОВОМУ URL /ws (а не /ws/general или /ws/crash)
        return `${protocol}//${host}/ws`;
    };

    const connect = (url?: string): Promise<boolean> => {
        const targetUrl = url || getWebSocketUrl()
        return connectToUrl(targetUrl)
    }

    const connectToUrl = async (url: string): Promise<boolean> => {
        try {
            socket.value = new WebSocket(url)
            
            return new Promise((resolve, reject) => {
                if (!socket.value) {
                    reject(new Error('Failed to create WebSocket'))
                    return
                }

                socket.value.onopen = () => {
                    console.log('✅ WebSocket connected to:', url)
                    isConnected.value = true
                    reconnectAttempts.value = 0
                    resolve(true)
                }

                socket.value.onmessage = (event) => {
                    try {
                        const data = JSON.parse(event.data)
                        handleWebSocketMessage(data)
                    } catch (error) {
                        console.error('Error parsing WebSocket message:', error)
                    }
                }

                socket.value.onclose = (event) => {
                    console.log('WebSocket disconnected:', event.code, event.reason)
                    isConnected.value = false
                    attemptReconnect()
                }

                socket.value.onerror = (error) => {
                    console.error('WebSocket error:', error)
                    reject(error)
                }
            })
        } catch (error) {
            console.error('Failed to create WebSocket:', error)
            return false
        }
    }

    const handleWebSocketMessage = (data: any) => {
        const userStore = useUserStore();
        const walletStore = useWalletStore();
        const gameStore = useGameStore();

        switch (data.type) {
            case 'crash_update':
                gameStore.setCrashGameState({
                    ...data.data,
                    players: data.data.players || [],
                    bets: data.data.bets || []
                });
                break;

            case 'crash_result':
                gameStore.processCrashResult(data.data);
                setTimeout(() => {
                    userStore.fetchBalance();
                }, 2000);
                break;

            case 'balance_update':
                userStore.setBalance(data.balance);
                break;

            // ✅ ОБРАБОТКА СТАВОК ЧЕРЕЗ CALLBACK
            case 'new_bet':
                if (callbacks.onNewBet) {
                    callbacks.onNewBet(data.data);
                }
                break;

            case 'bet_history':
                if (callbacks.onBetHistory) {
                    callbacks.onBetHistory(data.data);
                }
                break;

            case 'ping':
                send({ type: 'pong', timestamp: data.timestamp });
                break;

            default:
                console.log('Unknown WebSocket message type:', data.type);
        }
    };

    // ✅ Добавляем методы для краш-игры
    const connectToCrashGame = async (): Promise<boolean> => {
        const baseUrl = getWebSocketUrl()
        const url = baseUrl.endsWith('/') ? `${baseUrl}crash` : `${baseUrl}/crash`
        return connectToUrl(url)
    }

    const connectToGeneral = async (): Promise<boolean> => {
        const baseUrl = getWebSocketUrl()
        const url = baseUrl.endsWith('/') ? `${baseUrl}general` : `${baseUrl}/general`
        return connectToUrl(url)
    }

    const connectToUserChannel = async (userId: number): Promise<boolean> => {
        const baseUrl = getWebSocketUrl()
        const url = baseUrl.endsWith('/') ? `${baseUrl}user/${userId}` : `${baseUrl}/user/${userId}`
        return connectToUrl(url)
    }



    const attemptReconnect = () => {
        if (reconnectAttempts.value < maxReconnectAttempts) {
            reconnectAttempts.value++
            const delay = Math.min(1000 * reconnectAttempts.value, 10000)
            
            console.log(`Reconnecting in ${delay}ms (attempt ${reconnectAttempts.value})`)
            
            setTimeout(() => {
                connect().catch(console.error)
            }, delay)
        }
    }

    const disconnect = () => {
        if (socket.value) {
            socket.value.close()
            socket.value = null
            isConnected.value = false
        }
    }

    const send = (data: any) => {
        if (socket.value && isConnected.value) {
            socket.value.send(JSON.stringify(data))
        }
    }
    
    const placeCrashBet = (amount: number, autoCashout?: number) => {
        try {
            const userStore = useUserStore();
            
            // ✅ ВАЖНО: Проверяем, что отправляем ID из БД, а не telegram_id
            const userId = userStore.user?.id; // Это ID из БД
            const telegramId = userStore.user?.telegram_id; // Это telegram_id
            
            console.log("🎯 [Frontend] User data:", {
                db_id: userId, 
                telegram_id: telegramId,
                amount: amount
            });
            
            if (!userId) {
                console.error("❌ [Frontend] User ID not available");
                return;
            }
            
            const betData = {
                type: "place_bet",
                user_id: userId, // ✅ Отправляем ID из БД
                amount: amount,
                auto_cashout: autoCashout,
                currency: "stars"
            };
            
            console.log("🎯 [Frontend] Sending bet:", betData);
            send(betData);
            
        } catch (error) {
            console.error("❌ [Frontend] Failed to send bet:", error);
        }
    };

    const cashOut = () => {
        send({
            type: 'cash_out'
        })
    }

    const getCrashHistory = () => {
        send({
            type: 'get_history',
            game: 'crash',
            limit: 50
        })
    }

    // ✅ Функция для периодического опроса (fallback)
    const startPolling = (interval: number = 5000) => {
        console.log('🔄 Starting polling as WebSocket fallback')
        
        const poll = async () => {
            try {
                await Promise.all([
                    useUserStore().fetchBalance(),
                    useWalletStore().updateBalance()
                ])
            } catch (error) {
                console.error('Polling error:', error)
            }
        }

        poll()
        return setInterval(poll, interval)
    }

    

    onUnmounted(() => {
        disconnect()
    })

    return {
        socket,
        isConnected,
        connect,
        disconnect,
        send,
        startPolling,
        connectToCrashGame,
        connectToGeneral,
        connectToUserChannel,
        placeCrashBet,
        cashOut,
        getCrashHistory
    }
}