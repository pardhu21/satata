<template>
  <div class="table-responsive d-none d-lg-block">
    <table
      class="table table-borderless table-hover table-sm rounded text-center"
      :class="{ 'table-striped': activity.activity_type !== 8 }"
      style="--bs-table-bg: var(--bs-gray-850)"
    >
      <thead>
        <tr>
          <th>#</th>
          <th v-if="hasIntensity">Intensity</th>
          <th>Distance</th>
          <th>Time</th>
          <th v-if="activityTypeIsCycling(activity)">Speed</th>
          <th v-else>Pace</th>
          <th v-if="!activityTypeIsSwimming(activity)">Elevation</th>
          <th v-if="activityTypeIsSwimming(activity)">SR</th>
          <th>HR</th>
          <th>Δ</th>
        </tr>
      </thead>

      <tbody class="table-group-divider">
        <tr v-for="(lap, index) in normalizedLaps" :key="lap.id ?? index">
          <td>{{ index + 1 }}</td>

          <td v-if="hasIntensity">{{ lap.intensity ?? '—' }}</td>

          <td>{{ lap.formattedDistance }}</td>
          <td>{{ lap.lapSecondsToMinutes }}</td>

          <td v-if="activityTypeIsCycling(activity)">
            {{ lap.formattedSpeedFull }}
          </td>
          <td v-else>
            {{ lap.formattedPaceFull }}
          </td>

          <td v-if="!activityTypeIsSwimming(activity)">
            {{ lap.formattedElevationFull }}
          </td>

          <td v-if="activityTypeIsSwimming(activity)">
            {{ lap.avg_cadence ?? '—' }}
          </td>

          <td>
            <span v-if="lap.avg_heart_rate"> {{ lap.avg_heart_rate }} bpm </span>
            <span v-else>—</span>
          </td>

          <td>
            <span v-if="lap.comparedLap">
              {{ lap.diffLabel }}
            </span>
            <span v-else>—</span>
          </td>
        </tr>
      </tbody>
    </table>
  </div>

  <!-- MOBILE -->
  <div class="table-responsive d-lg-none d-block">
    <table class="table table-sm table-borderless" style="--bs-table-bg: var(--bs-gray-850)">
      <tbody>
        <tr v-for="(lap, index) in normalizedLaps" :key="index">
          <td style="width: 5%">{{ index + 1 }}</td>

          <td style="width: 25%">
            <div class="progress">
              <div class="progress-bar" :style="{ width: lap.normalizedScore + '%' }" />
            </div>

            <div v-if="lap.comparedNormalizedScore !== null" class="progress mt-1 opacity-50">
              <div class="progress-bar" :style="{ width: lap.comparedNormalizedScore + '%' }" />
            </div>
          </td>

          <td style="width: 30%">
            <div>
              {{ activityTypeIsCycling(activity) ? lap.formattedSpeed : lap.formattedPace }}
            </div>
            <small class="text-muted">
              {{ lap.diffLabel }}
            </small>
          </td>

          <td style="width: 20%">
            {{ lap.avg_heart_rate ?? '—' }}
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { formatSecondsToMinutes } from '@/utils/dateTimeUtils'
import {
  formatDistance,
  formatElevation,
  formatPace,
  formatAverageSpeed,
  activityTypeIsCycling,
  activityTypeIsSwimming
} from '@/utils/activityUtils'

const props = defineProps({
  activity: Object,
  comparedActivity: Object,
  activityActivityLaps: Object,
  comparedActivityActivityLaps: Object,
  units: String
})

const { t } = useI18n()

const normalizedLaps = computed(() => {
  const base = props.activityActivityLaps ?? []
  const compared = props.comparedActivityActivityLaps ?? []

  if (!base.length) return []

  const fastest = Math.min(...base.map((l) => l.enhanced_avg_pace).filter((p) => p > 0))

  return base.map((lap, index) => {
    const comparedLap = compared[index] ?? null

    const normalizedScore =
      lap.enhanced_avg_pace > 0 ? Math.min((fastest / lap.enhanced_avg_pace) * 100, 100) : 0

    const comparedNormalizedScore =
      comparedLap?.enhanced_avg_pace > 0
        ? Math.min((fastest / comparedLap.enhanced_avg_pace) * 100, 100)
        : null

    const diffPace =
      lap.enhanced_avg_pace && comparedLap?.enhanced_avg_pace
        ? lap.enhanced_avg_pace - comparedLap.enhanced_avg_pace
        : null

    const diffLabel = diffPace !== null ? `${diffPace > 0 ? '+' : ''}${Math.round(diffPace)}s` : '—'

    return {
      ...lap,
      comparedLap,
      normalizedScore,
      comparedNormalizedScore,
      diffLabel,
      formattedDistance: formatDistance(t, props.activity, props.units, lap),
      formattedElevation: formatElevation(t, lap.total_ascent, props.units, false),
      formattedElevationFull: formatElevation(t, lap.total_ascent, props.units),
      formattedPace: formatPace(t, props.activity, props.units, lap, false),
      formattedPaceFull: formatPace(t, props.activity, props.units, lap, true),
      formattedSpeed: formatAverageSpeed(t, props.activity, props.units, lap, false),
      formattedSpeedFull: formatAverageSpeed(t, props.activity, props.units, lap),
      lapSecondsToMinutes: formatSecondsToMinutes(lap.total_elapsed_time)
    }
  })
})

const hasIntensity = computed(() => normalizedLaps.value.some((l) => l.intensity !== null))
</script>
