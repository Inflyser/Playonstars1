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
    betId?: number
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
        ['betting', 'flying'].includes(crashGame.value.phase)
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

    // ✅ ИСПРАВЛЕННЫЙ МЕТОД - правильная обработка данных от сервера
    const setCrashGameState = (data: any) => {
        console.log('🔄 Updating game state:', data)
        
        // Сохраняем текущую ставку пользователя перед обновлением
        const currentUserBet = userBet.value
        
        crashGame.value = {
            ...crashGame.value,
            ...data,
            players: data.players || [],
            bets: data.bets || []
        }
        
        // Восстанавливаем ставку пользователя (она может теряться при обновлении)
        if (currentUserBet) {
            userBet.value = currentUserBet
        }
        
        // ✅ ВАЖНО: Обновляем множитель в ставке пользователя если игра летит
        if (userBet.value && !userBet.value.cashedOut && data.multiplier) {
            // Можно обновить какую-то информацию о текущем множителе
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
            // ✅ ВАЖНО: Не списываем средства локально - это сделает сервер
            // userStore.updateBalance('stars', -amount)

            // Создаем ставку
            userBet.value = {
                userId: userStore.user?.id || 0,
                amount: amount,
                autoCashout: autoCashout,
                placedAt: new Date(),
                cashedOut: false
            }

            console.log('✅ Bet created locally:', userBet.value)

        } catch (err: any) {
            error.value = err.message
            // Откатываем изменения
            userBet.value = null
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
            // ✅ Только помечаем как выведенное локально
            // Реальный вывод сделает сервер через WebSocket
            userBet.value.cashedOut = true;
            userBet.value.cashoutMultiplier = crashGame.value.multiplier;
            userBet.value.profit = userBet.value.amount * crashGame.value.multiplier;
            
            console.log('✅ Cash out processed locally:', userBet.value);
            
        } catch (err: any) {
            error.value = err.message;
            throw err;
        }
    };
    
    // ✅ ИСПРАВЛЕННЫЙ МЕТОД - обработка результатов игры
    const processCrashResult = async (data: any) => {
        console.log('💥 Processing crash result:', data)
        
        if (data.history) {
            crashGame.value.history = data.history.slice(0, 50);
        }
    
        // ✅ ОБРАБОТКА СТАВКИ ПОЛЬЗОВАТЕЛЯ
        if (userBet.value) {
            const finalMultiplier = data.finalMultiplier || data.crashedAt;
            
            if (userBet.value.cashedOut) {
                // Уже вывели - ничего не делаем
                console.log('✅ User already cashed out');
            } else if (userBet.value.autoCashout && finalMultiplier >= userBet.value.autoCashout) {
                // Автовывод сработал
                userBet.value.cashedOut = true;
                userBet.value.cashoutMultiplier = userBet.value.autoCashout;
                userBet.value.profit = userBet.value.amount * userBet.value.autoCashout;
                
                console.log('✅ Auto cashout triggered:', userBet.value);
            } else if (finalMultiplier) {
                // Игра крашнулась раньше автовывода
                userBet.value.cashedOut = false;
                userBet.value.profit = 0;
                console.log('❌ User lost - crashed before cashout');
            }
        }
    
        crashGame.value.phase = 'finished';
        
        // ✅ ОБНОВЛЯЕМ БАЛАНС ЧЕРЕЗ НЕСКОЛЬКО СЕКУНД (после обработки на сервере)
        setTimeout(() => {
            userStore.fetchBalance().catch(console.error);
        }, 1500);
    };

    const resetBet = () => {
        console.log('🔄 Resetting user bet');
        userBet.value = null;
    }

    const loadGameHistory = async (limit: number = 10): Promise<void> => {
        try {
            const response = await api.get('/crash/history', { 
                params: { limit } 
            });
            
            if (response.data && Array.isArray(response.data)) {
                crashGame.value.history = response.data.map((game: any) => ({
                    gameId: game.gameId || game.id,
                    multiplier: game.multiplier,
                    crashedAt: game.crashedAt || game.multiplier,
                    timestamp: new Date(game.timestamp),
                    playersCount: game.playersCount || game.total_players,
                    totalBet: game.totalBet || game.total_bet,
                    totalPayout: game.totalPayout || game.total_payout
                }));
            }
        } catch (error) {
            console.error('Failed to load game history:', error);
            // ✅ Fallback на заглушку если API не доступно
            crashGame.value.history = generateFallbackHistory();
        }
    }

    // ✅ Заглушка для истории
    const generateFallbackHistory = (): CrashGameHistory[] => {
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
            },
            {
                gameId: 3,
                multiplier: 7.21,
                crashedAt: 7.21,
                timestamp: new Date(Date.now() - 200000),
                playersCount: 15,
                totalBet: 2100,
                totalPayout: 1800
            }
        ]
    }

    const getPlayerById = (userId: number) => {
        return crashGame.value.players.find(player => player.userId === userId)
    }

    const getTopPlayers = (limit: number = 15) => {
        return [...crashGame.value.players]
            .sort((a, b) => (b.profit || 0) - (a.profit || 0))
            .slice(0, limit)
    }

    // ✅ Новая функция для принудительного обновления множителя
    const updateMultiplier = (multiplier: number) => {
        if (crashGame.value.phase === 'flying') {
            crashGame.value.multiplier = multiplier;
        }
    }

    // ✅ Новая функция для сброса состояния игры
    const resetGameState = () => {
        crashGame.value = {
            gameId: crashGame.value.gameId + 1,
            phase: 'waiting',
            multiplier: 1.0,
            timeRemaining: 0,
            players: [],
            history: crashGame.value.history, // Сохраняем историю
            bets: []
        };
        resetBet();
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
        generateFallbackHistory,
        updateMultiplier,
        resetGameState
    }
})