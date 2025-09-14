import { defineStore } from 'pinia'
import { ref } from 'vue'
import { api } from '@/services/api'

interface Referral {
  id: number
  telegram_id: number
  username: string | null
  first_name: string | null
  last_name: string | null
  photo_url: string | null
  stars_balance: number
  created_at: string | null
}

export const useReferralStore = defineStore('referral', () => {
  const userReferrals = ref<Referral[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)

  const fetchUserReferrals = async (userId: number) => {
    try {
      loading.value = true
      error.value = null
      const response = await api.get('/api/user/my-referrals')
      userReferrals.value = response.data.referrals || []
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Ошибка загрузки рефералов'
      console.error('Error fetching referrals:', err)
    } finally {
      loading.value = false
    }
  }

  return {
    userReferrals,
    loading,
    error,
    fetchUserReferrals
  }
})