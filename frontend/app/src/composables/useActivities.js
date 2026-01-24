import { ref } from 'vue'
import { debounce } from 'lodash'
import { push } from 'notivue'
import { useI18n } from 'vue-i18n'
import { activities as activitiesService } from '@/services/activitiesService'
import { useAuthStore } from '@/stores/authStore'
import { useServerSettingsStore } from '@/stores/serverSettingsStore'

export const useActivities = () => {
  const { t } = useI18n()
  const serverSettingsStore = useServerSettingsStore()
  const authStore = useAuthStore()
  const activityTypes = ref([])
  const activities = ref([])
  const userNumberActivities = ref(0)
  const pageNumber = ref(1)
  const numRecords = serverSettingsStore.serverSettings.num_records_per_page || 25
  const totalPages = ref(1)
  const isLoading = ref(true)

  // Filter state
  const selectedType = ref('')
  const startDate = ref('')
  const endDate = ref('')
  const nameSearch = ref('')

  // Sorting state
  const sortBy = ref('start_time') // Default sort column
  const sortOrder = ref('desc') // Default sort order

  const performNameSearch = debounce(async () => {
    if (!nameSearch.value) {
      pageNumber.value = 1
      await applyFilters()
      return
    }
    try {
      await applyFilters()
    } catch (error) {
      push.error(`${t('activitiesView.errorUpdatingActivities')} - ${error}`)
    }
  }, 500)

  async function fetchActivityTypes() {
    try {
      activityTypes.value = await activitiesService.getActivityTypes()
    } catch (error) {
      push.error(`${t('activitiesView.errorFailedFetchActivityTypes')} - ${error}`)
    }
  }

  function setPageNumber(page) {
    pageNumber.value = page
  }

  async function updateActivities(activityType) {
    try {
      selectedType.value = activityType || selectedType.value
      isLoading.value = true
      await fetchActivities()
    } catch (error) {
      push.error(`${t('activitiesView.errorUpdatingActivities')} - ${error}`)
    } finally {
      isLoading.value = false
    }
  }

  async function fetchActivities() {
    activities.value = []
    const filters = {
      type: selectedType.value,
      start_date: startDate.value,
      end_date: endDate.value,
      name_search: nameSearch.value
    }
    try {
      activities.value = await activitiesService.getUserActivitiesWithPagination(
        authStore.user.id,
        pageNumber.value,
        numRecords,
        filters,
        sortBy.value,
        sortOrder.value
      )
      userNumberActivities.value = await activitiesService.getUserNumberOfActivities(filters)
      totalPages.value = Math.ceil(userNumberActivities.value / numRecords)
    } catch (error) {
      push.error(`${t('activitiesView.errorFetchingActivities')} - ${error}`)
    }
  }

  async function applyFilters() {
    pageNumber.value = 1
    await updateActivities()
  }

  async function clearFilters() {
    selectedType.value = ''
    startDate.value = ''
    endDate.value = ''
    nameSearch.value = ''
    sortBy.value = 'start_time'
    sortOrder.value = 'desc'
    await applyFilters()
  }

  async function handleSort(columnName) {
    if (sortBy.value === columnName) {
      sortOrder.value = sortOrder.value === 'asc' ? 'desc' : 'asc'
    } else {
      sortBy.value = columnName
      sortOrder.value = 'desc'
    }
    await updateActivities()
  }

  return {
    activities,
    activityTypes,
    selectedType,
    startDate,
    endDate,
    totalPages,
    isLoading,
    sortBy,
    sortOrder,
    nameSearch,
    performNameSearch,
    pageNumber,
    fetchActivityTypes,
    updateActivities,
    applyFilters,
    handleSort,
    clearFilters,
    setPageNumber
  }
}
