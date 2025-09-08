import { ref } from 'vue'

export const useBetHistory = () => {
    const betHistory = ref<any[]>([])
    const loading = ref(false)

    const addNewBet = (betData: any) => {
        if (betHistory.value.length >= 100) {
            betHistory.value.pop()
        }
        betHistory.value.unshift(betData)
    }

    const setBetHistory = (historyData: any[]) => {
        betHistory.value = historyData
    }

    return {
        betHistory,
        loading,
        addNewBet,
        setBetHistory
    }
}