import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { useUserStore } from './useUserStore'
import { api } from '@/services/api'

export interface CrashGameState {
    gameId: number
    phase: 'waiting' | 'betting' | 'flying' | 'crashed' | 'finished'
    multiplier: number
    timeRemaining: number
    players: CrashPlayer[]
    history: CrashGameHistory[]
    bets: UserBet[]
}

export interface CrashPlayer {
    userId: number
    username: string
    avatar: string
    betAmount: number
    cashoutMultiplier?: number
    profit?: number
    status: 'waiting' | 'playing' | 'cashed_out' | 'crashed'
}

export interface UserBet {
    userId: number
    amount: number
    autoCashout?: number
    placedAt: Date
    cashedOut: boolean
    cashoutMultiplier?: number
    profit?: number
    betId?: number // ✅ Добавим опциональное поле
}

export interface CrashGameHistory {
    gameId: number
    multiplier: number
    crashedAt: number
    timestamp: Date
    playersCount: number
    totalBet: number
    totalPayout: number
}

export const useGameStore = defineStore('game', () => {
    const userStore = useUserStore()
    
    // Состояние краш-игры
    const crashGame = ref<CrashGameState>({
        gameId: 0,
        phase: 'waiting',
        multiplier: 1.0,
        timeRemaining: 0,
        players: [],
        history: [],
        bets: []
    })

    // Ставка пользователя
    const userBet = ref<UserBet | null>(null)
    const isBetting = ref(false)
    const error = ref<string | null>(null)

    // Компьютед свойства
    const isGameActive = computed(() => 
        crashGame.value.phase === 'betting' || crashGame.value.phase === 'flying'
    )

    const canPlaceBet = computed(() => 
        crashGame.value.phase === 'betting' && 
        !userBet.value && 
        userStore.balance.stars_balance > 0
    )

    const canCashOut = computed(() => 
        crashGame.value.phase === 'flying' && 
        userBet.value && 
        !userBet.value.cashedOut
    )

    const currentProfit = computed(() => {
        if (!userBet.value || userBet.value.cashedOut) return 0
        return userBet.value.amount * crashGame.value.multiplier
    })

    // Методы для краш-игры
    const setCrashGameState = (data: any) => {
        crashGame.value = {
            ...crashGame.value,
            ...data,
            players: data.players || [],
            bets: data.bets || []
        }
    }

    const processCrashResult = (data: any) => {
        // Обновляем историю
        if (data.history) {
            crashGame.value.history = data.history.slice(0, 50)
        }

        // Обрабатываем результат ставки пользователя
        if (userBet.value && data.finalMultiplier) {
            const finalMultiplier = data.finalMultiplier
            
            if (userBet.value.cashedOut) {
                // Пользователь успел вывести
                userBet.value.profit = userBet.value.amount * (userBet.value.cashoutMultiplier || 1)
            } else if (userBet.value.autoCashout && finalMultiplier >= userBet.value.autoCashout) {
                // Сработал авто-вывод
                userBet.value.cashedOut = true
                userBet.value.cashoutMultiplier = userBet.value.autoCashout
                userBet.value.profit = userBet.value.amount * userBet.value.autoCashout
            } else {
                // Проигрыш
                userBet.value.cashedOut = false
                userBet.value.profit = 0
            }

            // Обновляем баланс пользователя
            if (userBet.value.profit > 0) {
                userStore.updateBalance('stars', userBet.value.profit)
            }
        }

        // Переходим в фазу завершения
        crashGame.value.phase = 'finished'
    }

    const placeBet = async (amount: number, autoCashout?: number) => {
        if (!canPlaceBet.value) {
            throw new Error('Cannot place bet at this time')
        }

        if (amount > userStore.balance.stars_balance) {
            throw new Error('Insufficient balance')
        }

        isBetting.value = true
        error.value = null

        try {
            // Сначала списываем средства локально
            userStore.updateBalance('stars', -amount)

            // Создаем ставку
            userBet.value = {
                userId: userStore.user?.id || 0,
                amount: amount,
                autoCashout: autoCashout,
                placedAt: new Date(),
                cashedOut: false
            }

            // ✅ ОТПРАВЛЯЕМ НА СЕРВЕР ЧЕРЕЗ WebSocket (не API)
            // API вызов будет в компоненте через placeCrashBet

        } catch (err: any) {
            error.value = err.message
            // Возвращаем средства при ошибке
            userStore.updateBalance('stars', amount)
            throw err
        } finally {
            isBetting.value = false
        }
    }

    const cashOut = async () => {
        if (!canCashOut.value || !userBet.value) {
            throw new Error('Cannot cash out at this time')
        }

        try {
            // Помечаем ставку как выведенную
            userBet.value.cashedOut = true
            userBet.value.cashoutMultiplier = crashGame.value.multiplier
            userBet.value.profit = userBet.value.amount * crashGame.value.multiplier

            // Зачисляем выигрыш
            userStore.updateBalance('stars', userBet.value.profit)

        } catch (err: any) {
            error.value = err.message
            throw err
        }
    }

    const resetBet = () => {
        userBet.value = null
    }

    // ✅ ДОБАВИМ ЗАГЛУШКУ ДЛЯ ИСТОРИИ
    const generateFallbackHistory = () => {
        return [
            {
                gameId: 1,
                multiplier: 3.45,
                crashedAt: 3.45,
                timestamp: new Date(),
                playersCount: 12,
                totalBet: 1500,
                totalPayout: 1200
            },
            {
                gameId: 2,
                multiplier: 1.89,
                crashedAt: 1.89,
                timestamp: new Date(Date.now() - 100000),
                playersCount: 8,
                totalBet: 800,
                totalPayout: 0
            }
        ]
    }

    const loadGameHistory = async (limit: number = 50) => {
        try {
            // ✅ ЗАГЛУШКА - потом заменим на реальный API
            crashGame.value.history = generateFallbackHistory();
        } catch (err) {
            console.error('Failed to load game history:', err);
            crashGame.value.history = generateFallbackHistory();
        }
    }

    const getPlayerById = (userId: number) => {
        return crashGame.value.players.find(player => player.userId === userId)
    }

    const getTopPlayers = (limit: number = 10) => {
        return [...crashGame.value.players]
            .sort((a, b) => (b.profit || 0) - (a.profit || 0))
            .slice(0, limit)
    }

    // Автоматически загружаем историю при инициализации
    loadGameHistory()

    return {
        // State
        crashGame,
        userBet,
        isBetting,
        error,

        // Computed
        isGameActive,
        canPlaceBet,
        canCashOut,
        currentProfit,

        // Actions
        setCrashGameState,
        processCrashResult,
        placeBet,
        cashOut,
        resetBet,
        loadGameHistory,
        getPlayerById,
        getTopPlayers,
        generateFallbackHistory // ✅ Экспортируем если нужно
    }
})