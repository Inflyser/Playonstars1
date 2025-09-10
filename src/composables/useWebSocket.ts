import { ref, onUnmounted } from 'vue'
import { useUserStore } from '@/stores/useUserStore'
import { useWalletStore } from '@/stores/useWalletStore'
import { useGameStore } from '@/stores/useGameStore'

interface WebSocketCallbacks {
  onNewBet?: (betData: any) => void
  onBetHistory?: (historyData: any[]) => void
}

export const useWebSocket = (callbacks: WebSocketCallbacks = {}) => {
    const socket = ref<WebSocket | null>(null)
    const crashSocket = ref<WebSocket | null>(null) // ✅ Отдельный сокет для краш-игры
    const isConnected = ref(false)
    const isCrashConnected = ref(false)
    const reconnectAttempts = ref(0)
    const maxReconnectAttempts = 5
    let pingInterval: number | null = null

    const getWebSocketUrl = (): string => {
        const envUrl = import.meta.env.VITE_WS_URL;
        
        if (envUrl && envUrl.startsWith('wss://')) {
            return envUrl;
        }
        
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const host = window.location.host;
        
        return `${protocol}//${host}/ws`;
    };

    // ✅ ОБЩЕЕ ПОДКЛЮЧЕНИЕ
    const connect = (url?: string): Promise<boolean> => {
        const targetUrl = url || getWebSocketUrl()
        return connectToUrl(targetUrl, 'general')
    }

    // ✅ ПОДКЛЮЧЕНИЕ К КРАШ-ИГРЕ
    const connectToCrashGame = async (): Promise<boolean> => {
        const baseUrl = getWebSocketUrl()
        const url = baseUrl.endsWith('/') ? `${baseUrl}crash` : `${baseUrl}/crash`
        return connectToUrl(url, 'crash')
    }

    const connectToUrl = async (url: string, socketType: 'general' | 'crash' = 'general'): Promise<boolean> => {
        try {
            const ws = new WebSocket(url)
            
            return new Promise((resolve, reject) => {
                ws.onopen = () => {
                    console.log(`✅ WebSocket connected to ${socketType}:`, url)
                    
                    if (socketType === 'general') {
                        socket.value = ws
                        isConnected.value = true
                    } else {
                        crashSocket.value = ws
                        isCrashConnected.value = true
                    }
                    
                    reconnectAttempts.value = 0
                    
                    // Запускаем ping только для общего соединения
                    if (socketType === 'general' && !pingInterval) {
                        pingInterval = window.setInterval(() => {
                            if (ws.readyState === WebSocket.OPEN) {
                                ws.send(JSON.stringify({
                                    type: 'ping',
                                    timestamp: Date.now()
                                }))
                            }
                        }, 30000)
                    }
                    
                    resolve(true)
                }

                ws.onmessage = (event) => {
                    try {
                        const data = JSON.parse(event.data)
                        handleWebSocketMessage(data, socketType)
                    } catch (error) {
                        console.error('Error parsing WebSocket message:', error)
                    }
                }

                ws.onclose = (event) => {
                    console.log(`WebSocket ${socketType} disconnected:`, event.code, event.reason)
                    
                    if (socketType === 'general') {
                        isConnected.value = false
                        socket.value = null
                    } else {
                        isCrashConnected.value = false
                        crashSocket.value = null
                    }
                    
                    if (socketType === 'general') {
                        attemptReconnect()
                    }
                }

                ws.onerror = (error) => {
                    console.error(`WebSocket ${socketType} error:`, error)
                    reject(error)
                }
            })
        } catch (error) {
            console.error('Failed to create WebSocket:', error)
            return false
        }
    }

    const handleWebSocketMessage = (data: any, socketType: string) => {
        const userStore = useUserStore();
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
                // Обновляем баланс после завершения игры
                setTimeout(() => {
                    userStore.fetchBalance();
                }, 2000);
                break;

            case 'balance_update':
                userStore.setBalance(data.balance);
                break;

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

            case 'pong':
                // Обработка pong ответа
                break;

            default:
                console.log('Unknown WebSocket message type:', data.type);
        }
    };

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

    const disconnect = (socketType: 'general' | 'crash' = 'general') => {
        if (socketType === 'general' && socket.value) {
            socket.value.close()
            socket.value = null
            isConnected.value = false
            
            if (pingInterval) {
                clearInterval(pingInterval)
                pingInterval = null
            }
        } else if (socketType === 'crash' && crashSocket.value) {
            crashSocket.value.close()
            crashSocket.value = null
            isCrashConnected.value = false
        }
    }

    const send = (data: any, socketType: 'general' | 'crash' = 'general') => {
        const targetSocket = socketType === 'general' ? socket.value : crashSocket.value;
        const isTargetConnected = socketType === 'general' ? isConnected.value : isCrashConnected.value;
        
        if (targetSocket && isTargetConnected && targetSocket.readyState === WebSocket.OPEN) {
            targetSocket.send(JSON.stringify(data))
            return true
        }
        return false
    }
    
    const placeCrashBet = (amount: number, autoCashout?: number) => {
        try {
            const userStore = useUserStore();
            const userId = userStore.user?.id;
            
            if (!userId) {
                console.error("❌ User ID not available");
                return false;
            }
            
            const betData = {
                type: "place_bet",
                user_id: userId,
                amount: amount,
                auto_cashout: autoCashout,
                currency: "stars"
            };
            
            console.log("🎯 Sending crash bet:", betData);
            return send(betData, 'crash');
            
        } catch (error) {
            console.error("❌ Failed to send crash bet:", error);
            return false;
        }
    };

    const cashOut = () => {
        return send({
            type: 'cash_out'
        }, 'crash')
    }

    const getCrashHistory = () => {
        return send({
            type: 'get_history',
            game: 'crash',
            limit: 50
        }, 'crash')
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
        return window.setInterval(poll, interval)
    }

    onUnmounted(() => {
        disconnect('general')
        disconnect('crash')
        if (pingInterval) {
            clearInterval(pingInterval)
        }
    })

    return {
        socket,
        crashSocket,
        isConnected,
        isCrashConnected,
        connect,
        connectToCrashGame,
        disconnect,
        send,
        startPolling,
        placeCrashBet,
        cashOut,
        getCrashHistory
    }
}