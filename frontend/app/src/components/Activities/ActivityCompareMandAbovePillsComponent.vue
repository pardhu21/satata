<template>
  <ul class="nav nav-pills mb-3 mt-3 justify-content-center" id="pills-tab" role="tablist">
    <li class="nav-item" role="presentation" v-if="graphItems && graphItems.length > 0">
      <button
        class="nav-link link-body-emphasis"
        :class="{ active: graphItems || graphItems.length > 0 }"
        id="pills-graphs-tab"
        data-bs-toggle="pill"
        data-bs-target="#pills-graphs"
        type="button"
        role="tab"
        aria-controls="pills-graphs"
        :aria-selected="graphItems && graphItems.length > 0 ? true : false"
      >
        {{ $t('activityMandAbovePillsComponent.labelPillGraphs') }}
      </button>
    </li>
    <li
      class="nav-item"
      role="presentation"
      v-if="activityActivityLaps && activityActivityLaps.length > 0"
    >
      <button
        class="nav-link link-body-emphasis"
        :class="{ active: !graphItems || graphItems.length === 0 }"
        id="pills-laps-tab"
        data-bs-toggle="pill"
        data-bs-target="#pills-laps"
        type="button"
        role="tab"
        aria-controls="pills-laps"
        :aria-selected="!graphItems || graphItems.length === 0 ? 'true' : 'false'"
      >
        {{ $t('activityMandAbovePillsComponent.labelPillLaps') }}
      </button>
    </li>
    <li
      class="nav-item"
      role="presentation"
      v-if="activityActivityWorkoutSteps && activityActivityWorkoutSteps.length > 0"
    >
      <button
        class="nav-link link-body-emphasis"
        id="pills-workout-steps-tab"
        data-bs-toggle="pill"
        data-bs-target="#pills-workout-steps"
        type="button"
        role="tab"
        aria-controls="pills-workout-steps"
        aria-selected="false"
      >
        {{ $t('activityMandAbovePillsComponent.labelPillWorkoutSets') }}
      </button>
    </li>
  </ul>

  <div class="tab-content" id="pills-tabContent">
    <div
      class="tab-pane fade show"
      :class="{ active: graphItems || graphItems.length > 0 }"
      id="pills-graphs"
      role="tabpanel"
      aria-labelledby="pills-graphs-tab"
      tabindex="0"
      v-if="graphItems && graphItems.length > 0"
    >
      <div class="row">
        <div class="col-md-2">
          <p>{{ $t('activityMandAbovePillsComponent.labelGraph') }}</p>
          <ul class="nav nav-pills flex-column mb-auto" id="sidebarLineGraph">
            <li class="nav-item" v-for="item in graphItems" :key="item.type">
              <a
                href="javascript:void(0);"
                class="nav-link text-secondary"
                :class="{ 'active text-white': graphSelection === item.type }"
                @click="selectGraph(item.type)"
              >
                {{ item.label }}
              </a>
            </li>
          </ul>
        </div>
        <div class="col">
          <div if="activity" style="height: 400px; margin: 20px 0">
            <ActivityCompareStreamsLineChartComponent
              :activity="activity"
              :comparedActivity="comparedActivity"
              :graphSelection="graphSelection"
              :activityStreams="activityActivityStreams"
              :comparedActivityStreams="comparedActivityActivityStreams"
              v-if="graphSelection === 'hr' && hrPresent"
            />
            <ActivityCompareStreamsLineChartComponent
              :activity="activity"
              :comparedActivity="comparedActivity"
              :graphSelection="graphSelection"
              :activityStreams="activityActivityStreams"
              :comparedActivityStreams="comparedActivityActivityStreams"
              v-if="graphSelection === 'power' && powerPresent"
            />
            <ActivityCompareStreamsLineChartComponent
              :activity="activity"
              :comparedActivity="comparedActivity"
              :graphSelection="graphSelection"
              :activityStreams="activityActivityStreams"
              :comparedActivityStreams="comparedActivityActivityStreams"
              v-if="graphSelection === 'cad' && cadPresent"
            />
            <ActivityCompareStreamsLineChartComponent
              :activity="activity"
              :comparedActivity="comparedActivity"
              :graphSelection="graphSelection"
              :activityStreams="activityActivityStreams"
              :comparedActivityStreams="comparedActivityActivityStreams"
              v-if="graphSelection === 'ele' && elePresent"
            />
            <ActivityCompareStreamsLineChartComponent
              :activity="activity"
              :comparedActivity="comparedActivity"
              :graphSelection="graphSelection"
              :activityStreams="activityActivityStreams"
              :comparedActivityStreams="comparedActivityActivityStreams"
              v-if="graphSelection === 'vel' && velPresent"
            />
            <ActivityCompareStreamsLineChartComponent
              :activity="activity"
              :comparedActivity="comparedActivity"
              :graphSelection="graphSelection"
              :activityStreams="activityActivityStreams"
              :comparedActivityStreams="comparedActivityActivityStreams"
              v-if="graphSelection === 'pace' && pacePresent"
            />
            <BarChartComponent
              v-if="Object.values(hrZones).length > 0 && graphSelection === 'hrZones' && hrPresent"
              :labels="getHrBarChartData(hrZones, t).labels"
              :values="getHrBarChartData(hrZones, t).values"
              :barColors="getHrBarChartData(hrZones, t).barColors"
              :datalabelsFormatter="(value) => `${Math.round(value)}%`"
              :title="$t('activityMandAbovePillsComponent.labelHRZones')"
            />
          </div>
        </div>
      </div>
    </div>

    <div
      class="tab-pane fade"
      :class="{ 'show active': !graphItems || graphItems.length === 0 }"
      id="pills-laps"
      role="tabpanel"
      aria-labelledby="pills-laps-tab"
      tabindex="1"
      v-if="activityActivityLaps && activityActivityLaps.length > 0"
    >
      <ActivityCompareLapsComponent
        :activity="activity"
        :comparedActivity="comparedActivity"
        :activityActivityLaps="activityActivityLaps"
        :comparedActivityActivityLaps="comparedActivityActivityLaps"
        :units="units"
      />
    </div>

    <div
      class="tab-pane fade"
      id="pills-workout-steps"
      role="tabpanel"
      aria-labelledby="pills-workout-steps-tab"
      tabindex="2"
      v-if="activityActivityWorkoutSteps && activityActivityWorkoutSteps.length > 0"
    >
      <ActivityWorkoutStepsComponent
        :activity="activity"
        :activityActivityWorkoutSteps="activityActivityWorkoutSteps"
        :units="units"
        :activityActivityExerciseTitles="activityActivityExerciseTitles"
        :activityActivitySets="activityActivitySets"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'

// Importing the components
import ActivityCompareLapsComponent from '@/components/Activities/ActivityCompareLapsComponent.vue'
import ActivityCompareStreamsLineChartComponent from '@/components/Activities/ActivityCompareStreamsLineChartComponent.vue'
import ActivityWorkoutStepsComponent from '@/components/Activities/ActivityWorkoutStepsComponent.vue'
import BarChartComponent from '@/components/GeneralComponents/BarChartComponent.vue'

import {
  activityTypeIsCycling,
  activityTypeNotCycling,
  activityTypeIsSwimming,
  activityTypeIsSailing,
  activityTypeNotSailing,
  activityTypeIsWindsurf,
  activityTypeNotWindsurf
} from '@/utils/activityUtils'

// Import Notivue push
import { push } from 'notivue'

// Props
const props = defineProps({
  activity: { type: Object, required: true },
  comparedActivity: { type: Object, required: true },

  activityActivityLaps: { type: [Object, null], required: true },
  comparedActivityActivityLaps: { type: [Object, null], required: true },

  activityActivityWorkoutSteps: { type: [Object, null], required: true },
  comparedActivityActivityWorkoutSteps: { type: [Object, null], required: true },

  activityActivityStreams: { type: [Object, null], required: true },
  comparedActivityActivityStreams: { type: [Object, null], required: true },

  units: { type: Number, default: 1 },

  activityActivityExerciseTitles: { type: [Object, null], required: true },
  comparedActivityActivityExerciseTitles: { type: [Object, null], required: true },

  activityActivitySets: { type: [Object, null], required: true },
  comparedActivityActivitySets: { type: [Object, null], required: true }
})

// Composables
const { t } = useI18n()

// Reactive state
const graphSelection = ref('hr')
const graphItems = ref([])

// Activity flags
const hrPresent = ref(false)
const powerPresent = ref(false)
const elePresent = ref(false)
const cadPresent = ref(false)
const velPresent = ref(false)
const pacePresent = ref(false)
const hrZones = ref({})

// Compared activity flags
const comparedHrPresent = ref(false)
const comparedPowerPresent = ref(false)
const comparedElePresent = ref(false)
const comparedCadPresent = ref(false)
const comparedVelPresent = ref(false)
const comparedPacePresent = ref(false)
const comparedHrZones = ref({})

// Methods
function selectGraph(type) {
  graphSelection.value = type
}

// Lifecycle
onMounted(async () => {
  try {
    /* ===========================
       ACTIVITY STREAMS
    ============================ */
    if (props.activityActivityStreams && props.activityActivityStreams.length > 0) {
      for (const element of props.activityActivityStreams) {
        if (element.stream_type === 1) {
          hrPresent.value = true
          const hrStream = props.activityActivityStreams.find(
            (stream) => stream.hr_zone_percentages
          )
          hrZones.value =
            hrStream && hrStream.hr_zone_percentages ? hrStream.hr_zone_percentages : {}
        }

        if (element.stream_type === 2) powerPresent.value = true
        if (element.stream_type === 3) cadPresent.value = true

        if (element.stream_type === 4 && !activityTypeIsSwimming(props.activity)) {
          elePresent.value = true
        }

        if (
          element.stream_type === 5 &&
          (activityTypeIsCycling(props.activity) ||
            activityTypeIsSailing(props.activity) ||
            activityTypeIsWindsurf(props.activity))
        ) {
          velPresent.value = true
        }

        if (
          element.stream_type === 6 &&
          activityTypeNotCycling(props.activity) &&
          activityTypeNotSailing(props.activity) &&
          activityTypeNotWindsurf(props.activity)
        ) {
          pacePresent.value = true
        }
      }
    }

    /* ===========================
       COMPARED ACTIVITY STREAMS
    ============================ */
    if (props.comparedActivityActivityStreams && props.comparedActivityActivityStreams.length > 0) {
      for (const element of props.comparedActivityActivityStreams) {
        if (element.stream_type === 1) {
          comparedHrPresent.value = true
          const hrStream = props.comparedActivityActivityStreams.find(
            (stream) => stream.hr_zone_percentages
          )
          comparedHrZones.value =
            hrStream && hrStream.hr_zone_percentages ? hrStream.hr_zone_percentages : {}
        }

        if (element.stream_type === 2) comparedPowerPresent.value = true
        if (element.stream_type === 3) comparedCadPresent.value = true

        if (element.stream_type === 4 && !activityTypeIsSwimming(props.comparedActivity)) {
          comparedElePresent.value = true
        }

        if (
          element.stream_type === 5 &&
          (activityTypeIsCycling(props.comparedActivity) ||
            activityTypeIsSailing(props.comparedActivity) ||
            activityTypeIsWindsurf(props.comparedActivity))
        ) {
          comparedVelPresent.value = true
        }

        if (
          element.stream_type === 6 &&
          activityTypeNotCycling(props.comparedActivity) &&
          activityTypeNotSailing(props.comparedActivity) &&
          activityTypeNotWindsurf(props.comparedActivity)
        ) {
          comparedPacePresent.value = true
        }
      }
    }

    /* ===========================
       GRAPH TABS (intersection)
    ============================ */
    if (hrPresent.value && comparedHrPresent.value) {
      graphItems.value.push({
        type: 'hr',
        label: t('activityMandAbovePillsComponent.labelGraphHR')
      })
    }

    if (Object.keys(hrZones.value).length > 0 && Object.keys(comparedHrZones.value).length > 0) {
      graphItems.value.push({
        type: 'hrZones',
        label: t('activityMandAbovePillsComponent.labelHRZones')
      })
    }

    if (powerPresent.value && comparedPowerPresent.value) {
      graphItems.value.push({
        type: 'power',
        label: t('activityMandAbovePillsComponent.labelGraphPower')
      })
    }

    if (cadPresent.value && comparedCadPresent.value) {
      graphItems.value.push({
        type: 'cad',
        label: activityTypeIsSwimming(props.activity)
          ? t('activityMandAbovePillsComponent.labelGraphStrokeRate')
          : t('activityMandAbovePillsComponent.labelGraphCadence')
      })
    }

    if (elePresent.value && comparedElePresent.value) {
      graphItems.value.push({
        type: 'ele',
        label: t('activityMandAbovePillsComponent.labelGraphElevation')
      })
    }

    if (velPresent.value && comparedVelPresent.value) {
      graphItems.value.push({
        type: 'vel',
        label: t('activityMandAbovePillsComponent.labelGraphVelocity')
      })
    }

    if (pacePresent.value && comparedPacePresent.value) {
      graphItems.value.push({
        type: 'pace',
        label: t('activityMandAbovePillsComponent.labelGraphPace')
      })
    }

    if (graphItems.value.length > 0) {
      graphSelection.value = graphItems.value[0].type
    }
  } catch (error) {
    push.error(
      `${t('activityMandAbovePillsComponent.errorMessageProcessingActivityStreams')} - ${error}`
    )
  }
})
</script>
