<template>
  <div class="ai-insights-card">
    <h2 class="ai-title">AI Insights</h2>

    <div v-if="aiInsight">
      <p class="ai-text">{{ aiInsight }}</p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { activityAiInsights } from '@/services/activityAiInsightsService.js'

const props = defineProps({
  activity: {
    type: Object,
    required: true
  }
})

const aiInsight = ref(null)

onMounted(async () => {
  const response = await activityAiInsights.getActivityAiInsightsByActivityId(props.activity.id)

  aiInsight.value = response.insight_text
})
</script>

<style scoped>
.ai-insights-card {
  border-radius: 12px;
  padding: 20px 22px;
  border: 1px solid #e5e7eb;
  margin-top: 16px;
}

.ai-title {
  font-size: 1.1rem;
  font-weight: 600;
  margin-bottom: 12px;
}

.ai-text {
  white-space: pre-line;
  line-height: 1.7;
  font-size: 0.95rem;
}
</style>
