import { ref, onUnmounted } from 'vue'
import { useUserStore } from '@/stores/useUserStore'
import { useWalletStore } from '@/stores/useWalletStore'
import { useGameStore } from '@/stores/useGameStore'

export const useWebSocket = () => {
    const socket = ref<WebSocket | null>(null)
    const isConnected = ref(false)
    const reconnectAttempts = ref(0)
    const maxReconnectAttempts = 5

    // ✅ Функция для получения WebSocket URL с fallback
    const getWebSocketUrl = (): string => {
        const envUrl = import.meta.env.VITE_WS_URL
        if (envUrl && envUrl !== 'wss://your-websocket-url') {
            return envUrl
        }

        // Fallback: автоматически определяем URL на основе текущего хоста
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
        const host = window.location.host
        return `${protocol}//${host}/ws`
    }

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

    // ✅ Методы для краш-игры
    const placeCrashBet = (amount: number, autoCashout?: number) => {
        send({
            type: 'place_bet',
            amount: amount,
            auto_cashout: autoCashout,
            currency: 'stars'
        })
    }

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

    const handleWebSocketMessage = (data: any) => {
        const userStore = useUserStore();
        const walletStore = useWalletStore();
        const gameStore = useGameStore();

        switch (data.type) {
            case 'crash_update':
                // Обновляем состояние краш-игры с реальными данными
                gameStore.setCrashGameState({
                    ...data.data,
                    // Добавляем недостающие поля
                    players: data.data.players || [],
                    bets: data.data.bets || []
                });
                break;

            case 'crash_result':
                // Обрабатываем результат игры
                gameStore.processCrashResult(data.data);

                // Автоматически обновляем баланс после игры
                setTimeout(() => {
                    userStore.fetchBalance();
                }, 2000);
                break;

            case 'balance_update':
                // Синхронизируем баланс с сервером
                userStore.setBalance(data.balance);
                break;

            // ... остальные cases
        }
    };

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
        
        // Методы для краш-игры
        connectToCrashGame,
        connectToGeneral,
        connectToUserChannel,
        placeCrashBet,
        cashOut,
        getCrashHistory
    }
}