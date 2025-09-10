import { ref, onUnmounted } from 'vue'
import { useUserStore } from '@/stores/useUserStore'
import { useWalletStore } from '@/stores/useWalletStore'
import { useGameStore } from '@/stores/useGameStore'

interface WebSocketCallbacks {
  onNewBet?: (betData: any) => void
  onBetHistory?: (historyData: any[]) => void
  onCrashUpdate?: (data: any) => void
  onCrashResult?: (data: any) => void
  onBalanceUpdate?: (balance: any) => void
}

export const useWebSocket = (callbacks: WebSocketCallbacks = {}) => {
    const socket = ref<WebSocket | null>(null)
    const crashSocket = ref<WebSocket | null>(null)
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

    const connect = (url?: string): Promise<boolean> => {
        const targetUrl = url || getWebSocketUrl()
        return connectToUrl(targetUrl, 'general')
    }

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
                    } else {
                        // Автопереподключение для crash игры
                        setTimeout(() => {
                            if (reconnectAttempts.value < maxReconnectAttempts) {
                                reconnectAttempts.value++
                                console.log(`🔄 Reconnecting to crash game (attempt ${reconnectAttempts.value})`)
                                connectToCrashGame().catch(console.error)
                            }
                        }, 2000)
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
        console.log(`📨 [WebSocket ${socketType}] Received:`, data)
        
        const userStore = useUserStore();
        const gameStore = useGameStore();

        switch (data.type) {
            case 'crash_update':
                console.log('🎮 Crash update:', data.data)
                if (callbacks.onCrashUpdate) {
                    callbacks.onCrashUpdate(data.data)
                } else {
                    // Fallback: обновляем хранилище напрямую
                    gameStore.setCrashGameState({
                        ...data.data,
                        players: data.data.players || [],
                        bets: data.data.bets || []
                    })
                }
                break;

            case 'crash_result':
                console.log('💥 Crash result:', data.data)
                if (callbacks.onCrashResult) {
                    callbacks.onCrashResult(data.data)
                } else {
                    gameStore.processCrashResult(data.data)
                    setTimeout(() => {
                        userStore.fetchBalance();
                    }, 2000)
                }
                break;

            case 'balance_update':
                console.log('💰 Balance update:', data.balance)
                if (callbacks.onBalanceUpdate) {
                    callbacks.onBalanceUpdate(data.balance)
                } else {
                    userStore.setBalance(data.balance)
                }
                break;

            case 'new_bet':
                console.log('🎯 New bet:', data.data)
                if (callbacks.onNewBet) {
                    callbacks.onNewBet(data.data)
                }
                break;

            case 'bet_history':
                console.log('📊 Bet history:', data.data)
                if (callbacks.onBetHistory) {
                    callbacks.onBetHistory(data.data)
                }
                break;

            case 'pong':
                console.log('🏓 Pong received')
                break;

            default:
                console.log('❓ Unknown message type:', data.type, data)
        }
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
        const targetSocket = socketType === 'general' ? socket.value : crashSocket.value
        const isTargetConnected = socketType === 'general' ? isConnected.value : isCrashConnected.value
        
        if (targetSocket && isTargetConnected && targetSocket.readyState === WebSocket.OPEN) {
            targetSocket.send(JSON.stringify(data))
            console.log('📤 Sent:', data)
            return true
        }
        
        console.warn('❌ Cannot send - WebSocket not connected')
        return false
    }
    
    const placeCrashBet = (amount: number, autoCashout?: number) => {
        try {
            const userStore = useUserStore()
            const userId = userStore.user?.id
            
            if (!userId) {
                console.error("❌ User ID not available")
                return false
            }
            
            const betData = {
                type: "place_bet",
                user_id: userId,
                amount: amount,
                auto_cashout: autoCashout,
                currency: "stars"
            }
            
            console.log("🎯 Sending crash bet:", betData)
            return send(betData, 'crash')
            
        } catch (error) {
            console.error("❌ Failed to send crash bet:", error)
            return false
        }
    }

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