import { fetchGetRequest } from '@/utils/serviceUtils'

export const activityAiInsights = {
  getActivityAiInsightsByActivityId(activity_id) {
    return fetchGetRequest(`activities_ai_insights/activity_id/${activity_id}`)
  }
}
