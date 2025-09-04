export interface GameState {
    id: number
    status: 'waiting' | 'active' | 'finished'
    players: GamePlayer[]
    timestamp: Date
}

export interface GamePlayer {
    id: number
    username: string
    avatar: string
    bet: number
    multiplier?: number
    profit?: number
    status: 'playing' | 'cashed_out' | 'crashed'
}

export interface BetData {
    amount: number
    currency: 'stars' | 'ton'
    autoCashout?: number
}

export interface CashoutResult {
    success: boolean
    multiplier: number
    profit: number
    newBalance: number
}