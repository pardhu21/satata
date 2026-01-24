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
        </tr>
      </thead>

      <tbody class="table-group-divider">
        <tr
          v-for="(lap, index) in normalizedLaps"
          :key="lap.id ?? index"
          :style="
            activity.activity_type === 8
              ? {
                  'background-color': lap.baseLap?.swimIsRest
                    ? 'var(--bs-table-bg)'
                    : 'var(--bs-table-striped-bg)'
                }
              : null
          "
        >
          <td>{{ index + 1 }}</td>

          <td v-if="hasIntensity">
            <div>{{ lap.baseLap?.intensity ?? '—' }}</div>
            <small v-if="lap.comparedLap" class="text-muted">
              {{ lap.comparedLap.intensity ?? '—' }}
            </small>
          </td>

          <td>
            <div>{{ lap.formattedDistance }}</div>
            <small v-if="lap.comparedLap" class="text-muted">
              {{ lap.comparedFormattedDistance }}
            </small>
          </td>

          <td>
            <div>{{ lap.lapSecondsToMinutes }}</div>
            <small v-if="lap.comparedLap && lap.comparedLap.total_elapsed_time" class="text-muted">
              {{ formatSecondsToMinutes(lap.comparedLap.total_elapsed_time) }}
            </small>
          </td>

          <td v-if="activityTypeIsCycling(activity)">
            <div>{{ lap.formattedSpeedFull }}</div>
            <small v-if="lap.comparedLap" class="text-muted">
              {{ lap.comparedFormattedSpeedFull }}
            </small>
          </td>
          <td v-else>
            <div>{{ lap.formattedPaceFull }}</div>
            <small v-if="lap.comparedLap" class="text-muted">
              {{ lap.comparedFormattedPaceFull }}
            </small>
          </td>

          <td v-if="!activityTypeIsSwimming(activity)">
            <div>{{ lap.formattedElevationFull }}</div>
            <small v-if="lap.comparedLap" class="text-muted">
              {{ lap.comparedFormattedElevationFull }}
            </small>
          </td>

          <td v-if="activityTypeIsSwimming(activity)">
            <div>{{ lap.baseLap?.avg_cadence ?? '—' }}</div>
            <small v-if="lap.comparedLap" class="text-muted">
              {{ lap.comparedLap.avg_cadence ?? '—' }}
            </small>
          </td>

          <td>
            <div v-if="lap.baseLap?.avg_heart_rate">{{ lap.baseLap.avg_heart_rate }} bpm</div>
            <div v-else>—</div>
            <small v-if="lap.comparedLap && lap.comparedLap.avg_heart_rate" class="text-muted">
              {{ lap.comparedLap.avg_heart_rate }} bpm
            </small>
          </td>
        </tr>
      </tbody>
    </table>
  </div>

  <!-- MOBILE -->
  <div class="table-responsive d-lg-none d-block">
    <table class="table table-sm table-borderless" style="--bs-table-bg: var(--bs-gray-850)">
      <thead>
        <tr>
          <th scope="col" style="width: 5%">#</th>
          <th scope="col" style="width: 15%" v-if="activityTypeIsCycling(activity)">Speed</th>
          <th scope="col" style="width: 15%" v-else>Pace</th>
          <th scope="col" style="width: auto">&nbsp;</th>
          <th scope="col" style="width: 10%" v-if="!activityTypeIsSwimming(activity)">Elev</th>
          <th scope="col" style="width: 10%" v-if="activityTypeIsSwimming(activity)">SR</th>
          <th scope="col" style="width: 10%">HR</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="(lap, index) in normalizedLaps" :key="index">
          <td>{{ index + 1 }}</td>

          <td v-if="activityTypeIsCycling(activity)">
            <div>{{ lap.formattedSpeed }}</div>
            <small v-if="lap.comparedLap" class="text-muted">
              {{ lap.comparedFormattedSpeed }}
            </small>
          </td>
          <td v-else>
            <div>{{ lap.formattedPace }}</div>
            <small v-if="lap.comparedLap" class="text-muted">
              {{ lap.comparedFormattedPace }}
            </small>
          </td>

          <td>
            <div class="progress">
              <div class="progress-bar" :style="{ width: lap.normalizedScore + '%' }" />
            </div>

            <div v-if="lap.comparedNormalizedScore !== null" class="progress mt-1 opacity-50">
              <div class="progress-bar" :style="{ width: lap.comparedNormalizedScore + '%' }" />
            </div>
          </td>

          <td v-if="!activityTypeIsSwimming(activity)">
            <div>{{ lap.formattedElevation }}</div>
            <small v-if="lap.comparedLap" class="text-muted">
              {{ lap.comparedFormattedElevation }}
            </small>
          </td>

          <td v-if="activityTypeIsSwimming(activity)">
            <div>{{ lap.baseLap?.avg_cadence ?? '—' }}</div>
            <small v-if="lap.comparedLap" class="text-muted">
              {{ lap.comparedLap.avg_cadence ?? '—' }}
            </small>
          </td>

          <td>
            <div>{{ lap.baseLap?.avg_heart_rate ?? '—' }}</div>
            <small v-if="lap.comparedLap" class="text-muted">
              {{ lap.comparedLap.avg_heart_rate ?? '—' }}
            </small>
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

  if (!base.length && !compared.length) return []

  // Use the activity with more laps as the base for iteration
  const maxLaps = Math.max(base.length, compared.length)
  const allLaps = Array.from({ length: maxLaps }, (_, index) => ({
    baseLap: base[index] ?? null,
    comparedLap: compared[index] ?? null,
    index
  }))

  const fastest = Math.min(
    ...[...base, ...compared].map((l) => l?.enhanced_avg_pace).filter((p) => p > 0)
  )

  return allLaps.map(({ baseLap, comparedLap, index }) => {
    const lap = baseLap ?? comparedLap

    const normalizedScore =
      baseLap?.enhanced_avg_pace > 0
        ? Math.min((fastest / baseLap.enhanced_avg_pace) * 100, 100)
        : 0

    const comparedNormalizedScore =
      comparedLap?.enhanced_avg_pace > 0
        ? Math.min((fastest / comparedLap.enhanced_avg_pace) * 100, 100)
        : null

    return {
      ...lap,
      baseLap,
      comparedLap,
      normalizedScore,
      comparedNormalizedScore,
      formattedDistance: baseLap ? formatDistance(t, props.activity, props.units, baseLap) : '—',
      formattedElevation: baseLap
        ? formatElevation(t, baseLap.total_ascent, props.units, false)
        : '—',
      formattedElevationFull: baseLap ? formatElevation(t, baseLap.total_ascent, props.units) : '—',
      formattedPace: baseLap ? formatPace(t, props.activity, props.units, baseLap, false) : '—',
      formattedPaceFull: baseLap ? formatPace(t, props.activity, props.units, baseLap, true) : '—',
      formattedSpeed: baseLap
        ? formatAverageSpeed(t, props.activity, props.units, baseLap, false)
        : '—',
      formattedSpeedFull: baseLap
        ? formatAverageSpeed(t, props.activity, props.units, baseLap)
        : '—',
      comparedFormattedDistance: comparedLap
        ? formatDistance(t, props.comparedActivity ?? props.activity, props.units, comparedLap)
        : null,
      comparedFormattedElevation: comparedLap
        ? formatElevation(t, comparedLap.total_ascent, props.units, false)
        : null,
      comparedFormattedElevationFull: comparedLap
        ? formatElevation(t, comparedLap.total_ascent, props.units)
        : null,
      comparedFormattedPaceFull: comparedLap
        ? formatPace(t, props.comparedActivity ?? props.activity, props.units, comparedLap, true)
        : null,
      comparedFormattedPace: comparedLap
        ? formatPace(t, props.comparedActivity ?? props.activity, props.units, comparedLap, false)
        : null,
      comparedFormattedSpeedFull: comparedLap
        ? formatAverageSpeed(t, props.comparedActivity ?? props.activity, props.units, comparedLap)
        : null,
      comparedFormattedSpeed: comparedLap
        ? formatAverageSpeed(
            t,
            props.comparedActivity ?? props.activity,
            props.units,
            comparedLap,
            false
          )
        : null,
      lapSecondsToMinutes: baseLap
        ? formatSecondsToMinutes(baseLap.total_elapsed_time)
        : comparedLap
          ? formatSecondsToMinutes(comparedLap.total_elapsed_time)
          : '—'
    }
  })
})

const hasIntensity = computed(() =>
  normalizedLaps.value.some(
    (l) => l.baseLap?.intensity !== null || l.comparedLap?.intensity !== null
  )
)
</script>
