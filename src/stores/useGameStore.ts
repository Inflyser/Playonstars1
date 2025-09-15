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
            throw new Error('Cannot cash out at this time');
        }
    
        try {
            userBet.value.cashedOut = true;
            userBet.value.cashoutMultiplier = crashGame.value.multiplier;
            const profit = userBet.value.amount * crashGame.value.multiplier;
            userBet.value.profit = profit;
        
            // ✅ ОБНОВЛЯЕМ БАЛАНС ЧЕРЕЗ USER STORE С СИНХРОНИЗАЦИЕЙ
            await userStore.updateBalance('stars', profit, 'add');
            
            console.log('Balance updated successfully:', userStore.balance.stars_balance);
        
        } catch (err: any) {
            error.value = err.message;
            throw err;
        }
    };
    
    const processCrashResult = async (data: any) => {
        if (data.history) {
            crashGame.value.history = data.history.slice(0, 50);
        }
    
        if (userBet.value && data.finalMultiplier) {
            const finalMultiplier = data.finalMultiplier;
            
            if (userBet.value.cashedOut) {
                userBet.value.profit = userBet.value.amount * (userBet.value.cashoutMultiplier || 1);
            } else if (userBet.value.autoCashout && finalMultiplier >= userBet.value.autoCashout) {
                userBet.value.cashedOut = true;
                userBet.value.cashoutMultiplier = userBet.value.autoCashout;
                const profit = userBet.value.amount * userBet.value.autoCashout;
                userBet.value.profit = profit;
                
                // ✅ ОБНОВЛЯЕМ БАЛАНС
                await userStore.updateBalance('stars', profit, 'add');
            } else {
                userBet.value.cashedOut = false;
                userBet.value.profit = 0;
            }
        }
    
        crashGame.value.phase = 'finished';
    };
    


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
    

    const loadGameHistory = async (limit: number = 49): Promise<void> => {
      try {
        const response = await api.get('/crash/history', { 
          params: { limit } 
        })
        crashGame.value.history = response.data
      } catch (error) {
        console.error('Failed to load game history:', error)
        crashGame.value.history = []
      }
    }

    const getPlayerById = (userId: number) => {
        return crashGame.value.players.find(player => player.userId === userId)
    }

    const getTopPlayers = (limit: number = 15) => {
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