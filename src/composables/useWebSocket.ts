import { ref, onUnmounted } from 'vue'
import { useUserStore } from '@/stores/useUserStore'
import { useWalletStore } from '@/stores/useWalletStore'

export const useWebSocket = () => {
    const socket = ref<WebSocket | null>(null)
    const isConnected = ref(false)
    const reconnectAttempts = ref(0)
    const maxReconnectAttempts = 5

    const connect = (url: string = import.meta.env.VITE_WS_URL || 'wss://your-websocket-url') => {
        return new Promise((resolve, reject) => {
            try {
                socket.value = new WebSocket(url)
                
                socket.value.onopen = () => {
                    console.log('✅ WebSocket connected')
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

            } catch (error) {
                console.error('Failed to create WebSocket:', error)
                reject(error)
            }
        })
    }

    const handleWebSocketMessage = (data: any) => {
        const userStore = useUserStore()
        const walletStore = useWalletStore()

        switch (data.type) {
            case 'balance_update':
                if (data.currency === 'ton') {
                    userStore.setBalance({ 
                        ton_balance: data.balance, 
                        stars_balance: userStore.balance.stars_balance 
                    })
                } else if (data.currency === 'stars') {
                    userStore.setBalance({ 
                        ton_balance: userStore.balance.ton_balance, 
                        stars_balance: data.balance 
                    })
                }
                break

            case 'transaction_update':
                if (data.status === 'completed') {
                    // Обновляем баланс при завершенной транзакции
                    walletStore.updateBalance()
                }
                break

            case 'game_result':
                // Обработка результатов игр
                console.log('Game result:', data)
                break

            default:
                console.log('Unknown WebSocket message:', data)
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

    onUnmounted(() => {
        disconnect()
    })

    return {
        socket,
        isConnected,
        connect,
        disconnect,
        send
    }
}