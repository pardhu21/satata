<template>
  <div if="activity" class="fw-lighter">
    <!-- laps -->
    <ActivityLapsComponent
      :activity="activity"
      :activityActivityLaps="activityActivityLaps"
      :units="units"
      v-if="activityActivityLaps && activityActivityLaps.length > 0"
    />

    <!-- Pace values -->
    <div v-if="pacePresent || comparePacePresent">
      <span class="fw-normal">
        {{ $t('activityBellowMPillsComponent.subTitlePace') }}
      </span>
      <div style="height: 400px; margin: 20px 0">
        <ActivityCompareStreamsLineChartComponent
          :activity="activity"
          :comparedActivity="compareActivity"
          :graphSelection="'pace'"
          :activityStreams="activityActivityStreams"
          :comparedActivityStreams="compareActivityActivityStreams"
        />
      </div>

      <!-- Primary Activity Stats -->
      <div v-if="pacePresent" class="mb-3">
        <div class="text-muted small mb-2">{{ activity.name || 'Activity 1' }}</div>
        <div class="d-flex justify-content-between mt-2" v-if="formattedPace">
          <span>{{ $t('activityBellowMPillsComponent.labelAvgPace') }}</span>
          <span
            ><b>{{ formattedPace }}</b></span
          >
        </div>
        <div class="d-flex justify-content-between mt-2" v-if="activity.total_elapsed_time">
          <span>{{ $t('activityBellowMPillsComponent.labelElapsedTime') }}</span>
          <span
            ><b>{{ formatSecondsToMinutes(activity.total_elapsed_time) }}</b></span
          >
        </div>
        <div class="d-flex justify-content-between mt-2" v-if="activity.total_timer_time">
          <span>{{ $t('activityBellowMPillsComponent.labelMovingTime') }}</span>
          <span
            ><b>{{ formatSecondsToMinutes(activity.total_timer_time) }}</b></span
          >
        </div>
      </div>

      <!-- Compared Activity Stats -->
      <div v-if="comparePacePresent && compareActivity" class="mb-3">
        <div class="text-muted small mb-2">{{ compareActivity.name || 'Activity 2' }}</div>
        <div class="d-flex justify-content-between mt-2" v-if="compareFormattedPace">
          <span>{{ $t('activityBellowMPillsComponent.labelAvgPace') }}</span>
          <span
            ><b>{{ compareFormattedPace }}</b></span
          >
        </div>
        <div class="d-flex justify-content-between mt-2" v-if="compareActivity.total_elapsed_time">
          <span>{{ $t('activityBellowMPillsComponent.labelElapsedTime') }}</span>
          <span
            ><b>{{ formatSecondsToMinutes(compareActivity.total_elapsed_time) }}</b></span
          >
        </div>
        <div class="d-flex justify-content-between mt-2" v-if="compareActivity.total_timer_time">
          <span>{{ $t('activityBellowMPillsComponent.labelMovingTime') }}</span>
          <span
            ><b>{{ formatSecondsToMinutes(compareActivity.total_timer_time) }}</b></span
          >
        </div>
      </div>
      <hr />
    </div>

    <!-- Velocity values -->
    <div v-if="velPresent || compareVelPresent">
      <span class="fw-normal">
        {{ $t('activityBellowMPillsComponent.subTitleSpeed') }}
      </span>
      <div style="height: 400px; margin: 20px 0">
        <ActivityCompareStreamsLineChartComponent
          :activity="activity"
          :comparedActivity="compareActivity"
          :graphSelection="'vel'"
          :activityStreams="activityActivityStreams"
          :comparedActivityStreams="compareActivityActivityStreams"
        />
      </div>

      <!-- Primary Activity Stats -->
      <div v-if="velPresent" class="mb-3">
        <div class="text-muted small mb-2">{{ activity.name || 'Activity 1' }}</div>
        <div class="d-flex justify-content-between mt-2" v-if="activity.average_speed">
          <span>{{ $t('activityBellowMPillsComponent.labelAvgSpeed') }}</span>
          <span>
            <span v-if="Number(units) === 1">
              <b
                >{{ formatAverageSpeedMetric(activity.average_speed) }}
                {{ $t('generalItems.unitsKmH') }}</b
              >
            </span>
            <span v-else>
              <b
                >{{ formatAverageSpeedImperial(activity.average_speed) }}
                {{ $t('generalItems.unitsMph') }}</b
              >
            </span>
          </span>
        </div>
        <div class="d-flex justify-content-between mt-2" v-if="activity.max_speed">
          <span>{{ $t('activityBellowMPillsComponent.labelMaxSpeed') }}</span>
          <span>
            <span v-if="Number(units) === 1">
              <b
                >{{ formatAverageSpeedMetric(activity.max_speed) }}
                {{ $t('generalItems.unitsKmH') }}</b
              >
            </span>
            <span v-else>
              <b
                >{{ formatAverageSpeedImperial(activity.max_speed) }}
                {{ $t('generalItems.unitsMph') }}</b
              >
            </span>
          </span>
        </div>
      </div>

      <!-- Compared Activity Stats -->
      <div v-if="compareVelPresent && compareActivity" class="mb-3">
        <div class="text-muted small mb-2">{{ compareActivity.name || 'Activity 2' }}</div>
        <div class="d-flex justify-content-between mt-2" v-if="compareActivity.average_speed">
          <span>{{ $t('activityBellowMPillsComponent.labelAvgSpeed') }}</span>
          <span>
            <span v-if="Number(units) === 1">
              <b
                >{{ formatAverageSpeedMetric(compareActivity.average_speed) }}
                {{ $t('generalItems.unitsKmH') }}</b
              >
            </span>
            <span v-else>
              <b
                >{{ formatAverageSpeedImperial(compareActivity.average_speed) }}
                {{ $t('generalItems.unitsMph') }}</b
              >
            </span>
          </span>
        </div>
        <div class="d-flex justify-content-between mt-2" v-if="compareActivity.max_speed">
          <span>{{ $t('activityBellowMPillsComponent.labelMaxSpeed') }}</span>
          <span>
            <span v-if="Number(units) === 1">
              <b
                >{{ formatAverageSpeedMetric(compareActivity.max_speed) }}
                {{ $t('generalItems.unitsKmH') }}</b
              >
            </span>
            <span v-else>
              <b
                >{{ formatAverageSpeedImperial(compareActivity.max_speed) }}
                {{ $t('generalItems.unitsMph') }}</b
              >
            </span>
          </span>
        </div>
      </div>
      <hr />
    </div>

    <!-- Heart rate values -->
    <div v-if="hrPresent || compareHrPresent">
      <span class="fw-normal">
        {{ $t('activityBellowMPillsComponent.subTitleHeartRate') }}
      </span>
      <div style="height: 400px; margin: 20px 0">
        <ActivityCompareStreamsLineChartComponent
          :activity="activity"
          :comparedActivity="compareActivity"
          :graphSelection="'hr'"
          :activityStreams="activityActivityStreams"
          :comparedActivityStreams="compareActivityActivityStreams"
        />
      </div>

      <!-- Primary Activity Stats -->
      <div v-if="hrPresent" class="mb-3">
        <div class="text-muted small mb-2">{{ activity.name || 'Activity 1' }}</div>
        <div class="d-flex justify-content-between mt-2" v-if="activity.average_hr">
          <span>{{ $t('activityBellowMPillsComponent.labelAvgHeartRate') }}</span>
          <span
            ><b>{{ activity.average_hr }} {{ $t('generalItems.unitsBpm') }}</b></span
          >
        </div>
        <div class="d-flex justify-content-between mt-2" v-if="activity.max_hr">
          <span>{{ $t('activityBellowMPillsComponent.labelMaxHeartRate') }}</span>
          <span
            ><b>{{ activity.max_hr }} {{ $t('generalItems.unitsBpm') }}</b></span
          >
        </div>
        <BarChartComponent
          v-if="Object.values(hrZones).length > 0"
          :labels="getHrBarChartData(hrZones, t).labels"
          :values="getHrBarChartData(hrZones, t).values"
          :barColors="getHrBarChartData(hrZones, t).barColors"
          :datalabelsFormatter="(value) => `${Math.round(value)}%`"
          :title="$t('activityMandAbovePillsComponent.labelHRZones')"
        />
      </div>

      <!-- Compared Activity Stats -->
      <div v-if="compareHrPresent && compareActivity" class="mb-3">
        <div class="text-muted small mb-2">{{ compareActivity.name || 'Activity 2' }}</div>
        <div class="d-flex justify-content-between mt-2" v-if="compareActivity.average_hr">
          <span>{{ $t('activityBellowMPillsComponent.labelAvgHeartRate') }}</span>
          <span
            ><b>{{ compareActivity.average_hr }} {{ $t('generalItems.unitsBpm') }}</b></span
          >
        </div>
        <div class="d-flex justify-content-between mt-2" v-if="compareActivity.max_hr">
          <span>{{ $t('activityBellowMPillsComponent.labelMaxHeartRate') }}</span>
          <span
            ><b>{{ compareActivity.max_hr }} {{ $t('generalItems.unitsBpm') }}</b></span
          >
        </div>
        <BarChartComponent
          v-if="Object.values(compareHrZones).length > 0"
          :labels="getHrBarChartData(compareHrZones, t).labels"
          :values="getHrBarChartData(compareHrZones, t).values"
          :barColors="getHrBarChartData(compareHrZones, t).barColors"
          :datalabelsFormatter="(value) => `${Math.round(value)}%`"
          :title="$t('activityMandAbovePillsComponent.labelHRZones')"
        />
      </div>
      <hr />
    </div>

    <!-- Power values -->
    <div v-if="powerPresent || comparePowerPresent">
      <span class="fw-normal">
        {{ $t('activityBellowMPillsComponent.subTitlePower') }}
      </span>
      <div style="height: 400px; margin: 20px 0">
        <ActivityCompareStreamsLineChartComponent
          :activity="activity"
          :comparedActivity="compareActivity"
          :graphSelection="'power'"
          :activityStreams="activityActivityStreams"
          :comparedActivityStreams="compareActivityActivityStreams"
        />
      </div>

      <!-- Primary Activity Stats -->
      <div v-if="powerPresent" class="mb-3">
        <div class="text-muted small mb-2">{{ activity.name || 'Activity 1' }}</div>
        <div class="d-flex justify-content-between mt-2" v-if="activity.average_power">
          <span>{{ $t('activityBellowMPillsComponent.labelAvgPower') }}</span>
          <span
            ><b>{{ activity.average_power }} {{ $t('generalItems.unitsWattsShort') }}</b></span
          >
        </div>
        <div class="d-flex justify-content-between mt-2" v-if="activity.max_power">
          <span>{{ $t('activityBellowMPillsComponent.labelMaxPower') }}</span>
          <span
            ><b>{{ activity.max_power }} {{ $t('generalItems.unitsWattsShort') }}</b></span
          >
        </div>
        <div class="d-flex justify-content-between mt-2" v-if="activity.normalized_power">
          <span>{{ $t('activityBellowMPillsComponent.labelNormalizedPower') }}</span>
          <span
            ><b>{{ activity.normalized_power }} {{ $t('generalItems.unitsWattsShort') }}</b></span
          >
        </div>
      </div>

      <!-- Compared Activity Stats -->
      <div v-if="comparePowerPresent && compareActivity" class="mb-3">
        <div class="text-muted small mb-2">{{ compareActivity.name || 'Activity 2' }}</div>
        <div class="d-flex justify-content-between mt-2" v-if="compareActivity.average_power">
          <span>{{ $t('activityBellowMPillsComponent.labelAvgPower') }}</span>
          <span
            ><b
              >{{ compareActivity.average_power }} {{ $t('generalItems.unitsWattsShort') }}</b
            ></span
          >
        </div>
        <div class="d-flex justify-content-between mt-2" v-if="compareActivity.max_power">
          <span>{{ $t('activityBellowMPillsComponent.labelMaxPower') }}</span>
          <span
            ><b>{{ compareActivity.max_power }} {{ $t('generalItems.unitsWattsShort') }}</b></span
          >
        </div>
        <div class="d-flex justify-content-between mt-2" v-if="compareActivity.normalized_power">
          <span>{{ $t('activityBellowMPillsComponent.labelNormalizedPower') }}</span>
          <span
            ><b
              >{{ compareActivity.normalized_power }} {{ $t('generalItems.unitsWattsShort') }}</b
            ></span
          >
        </div>
      </div>
      <hr />
    </div>

    <!-- Cadence values -->
    <div v-if="cadPresent || compareCadPresent">
      <span class="fw-normal" v-if="!activityTypeIsSwimming(activity)">
        {{ $t('activityBellowMPillsComponent.subTitleCadence') }}
      </span>
      <span class="fw-normal" v-else>
        {{ $t('activityBellowMPillsComponent.subTitleStrokeRate') }}
      </span>
      <div style="height: 400px; margin: 20px 0">
        <ActivityCompareStreamsLineChartComponent
          :activity="activity"
          :comparedActivity="compareActivity"
          :graphSelection="'cad'"
          :activityStreams="activityActivityStreams"
          :comparedActivityStreams="compareActivityActivityStreams"
        />
      </div>

      <!-- Primary Activity Stats -->
      <div v-if="cadPresent" class="mb-3">
        <div class="text-muted small mb-2">{{ activity.name || 'Activity 1' }}</div>
        <div class="d-flex justify-content-between mt-2" v-if="activity.average_cad">
          <span v-if="!activityTypeIsSwimming(activity)">
            {{ $t('activityBellowMPillsComponent.labelAvgCadence') }}
          </span>
          <span v-else>
            {{ $t('activityBellowMPillsComponent.labelAvgStrokeRate') }}
          </span>
          <span
            ><b>{{ activity.average_cad }} {{ $t('generalItems.unitsSpm') }}</b></span
          >
        </div>
        <div class="d-flex justify-content-between mt-2" v-if="activity.max_cad">
          <span v-if="!activityTypeIsSwimming(activity)">
            {{ $t('activityBellowMPillsComponent.labelMaxCadence') }}
          </span>
          <span v-else>
            {{ $t('activityBellowMPillsComponent.labelMaxStrokeRate') }}
          </span>
          <span
            ><b>{{ activity.max_cad }} {{ $t('generalItems.unitsSpm') }}</b></span
          >
        </div>
      </div>

      <!-- Compared Activity Stats -->
      <div v-if="compareCadPresent && compareActivity" class="mb-3">
        <div class="text-muted small mb-2">{{ compareActivity.name || 'Activity 2' }}</div>
        <div class="d-flex justify-content-between mt-2" v-if="compareActivity.average_cad">
          <span v-if="!activityTypeIsSwimming(compareActivity)">
            {{ $t('activityBellowMPillsComponent.labelAvgCadence') }}
          </span>
          <span v-else>
            {{ $t('activityBellowMPillsComponent.labelAvgStrokeRate') }}
          </span>
          <span
            ><b>{{ compareActivity.average_cad }} {{ $t('generalItems.unitsSpm') }}</b></span
          >
        </div>
        <div class="d-flex justify-content-between mt-2" v-if="compareActivity.max_cad">
          <span v-if="!activityTypeIsSwimming(compareActivity)">
            {{ $t('activityBellowMPillsComponent.labelMaxCadence') }}
          </span>
          <span v-else>
            {{ $t('activityBellowMPillsComponent.labelMaxStrokeRate') }}
          </span>
          <span
            ><b>{{ compareActivity.max_cad }} {{ $t('generalItems.unitsSpm') }}</b></span
          >
        </div>
      </div>
      <hr />
    </div>

    <!-- Elevation values -->
    <div v-if="(elePresent || compareElePresent) && !activityTypeIsSwimming(activity)">
      <span class="fw-normal">
        {{ $t('activityBellowMPillsComponent.subTitleElevation') }}
      </span>
      <div style="height: 400px; margin: 20px 0">
        <ActivityCompareStreamsLineChartComponent
          :activity="activity"
          :comparedActivity="compareActivity"
          :graphSelection="'ele'"
          :activityStreams="activityActivityStreams"
          :comparedActivityStreams="compareActivityActivityStreams"
        />
      </div>

      <!-- Primary Activity Stats -->
      <div v-if="elePresent" class="mb-3">
        <div class="text-muted small mb-2">{{ activity.name || 'Activity 1' }}</div>
        <div class="d-flex justify-content-between mt-2" v-if="activity.elevation_gain">
          <span>{{ $t('activityBellowMPillsComponent.labelElevationGain') }}</span>
          <span v-if="Number(units) === 1">
            <b>{{ activity.elevation_gain }} {{ $t('generalItems.unitsM') }}</b>
          </span>
          <span v-else>
            <b
              >{{ metersToFeet(activity.elevation_gain) }}
              {{ $t('generalItems.unitsFeetShort') }}</b
            >
          </span>
        </div>
        <div class="d-flex justify-content-between mt-2" v-if="activity.elevation_loss">
          <span>{{ $t('activityBellowMPillsComponent.labelElevationLoss') }}</span>
          <span v-if="Number(units) === 1">
            <b>{{ activity.elevation_loss }} {{ $t('generalItems.unitsM') }}</b>
          </span>
          <span v-else>
            <b
              >{{ metersToFeet(activity.elevation_loss) }}
              {{ $t('generalItems.unitsFeetShort') }}</b
            >
          </span>
        </div>
      </div>

      <!-- Compared Activity Stats -->
      <div v-if="compareElePresent && compareActivity" class="mb-3">
        <div class="text-muted small mb-2">{{ compareActivity.name || 'Activity 2' }}</div>
        <div class="d-flex justify-content-between mt-2" v-if="compareActivity.elevation_gain">
          <span>{{ $t('activityBellowMPillsComponent.labelElevationGain') }}</span>
          <span v-if="Number(units) === 1">
            <b>{{ compareActivity.elevation_gain }} {{ $t('generalItems.unitsM') }}</b>
          </span>
          <span v-else>
            <b
              >{{ metersToFeet(compareActivity.elevation_gain) }}
              {{ $t('generalItems.unitsFeetShort') }}</b
            >
          </span>
        </div>
        <div class="d-flex justify-content-between mt-2" v-if="compareActivity.elevation_loss">
          <span>{{ $t('activityBellowMPillsComponent.labelElevationLoss') }}</span>
          <span v-if="Number(units) === 1">
            <b>{{ compareActivity.elevation_loss }} {{ $t('generalItems.unitsM') }}</b>
          </span>
          <span v-else>
            <b
              >{{ metersToFeet(compareActivity.elevation_loss) }}
              {{ $t('generalItems.unitsFeetShort') }}</b
            >
          </span>
        </div>
      </div>
      <hr />
    </div>

    <!-- sets -->
    <ActivityWorkoutStepsComponent
      :activity="activity"
      :activityActivityWorkoutSteps="activityActivityWorkoutSteps"
      :units="units"
      :activityActivityExerciseTitles="activityActivityExerciseTitles"
      :activityActivitySets="activityActivitySets"
      v-if="activityActivityWorkoutSteps && activityActivityWorkoutSteps.length > 0"
    />
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useI18n } from 'vue-i18n'
// Importing the components
import ActivityLapsComponent from '@/components/Activities/ActivityLapsComponent.vue'
import ActivityCompareStreamsLineChartComponent from '@/components/Activities/ActivityCompareStreamsLineChartComponent.vue'
import ActivityWorkoutStepsComponent from '@/components/Activities/ActivityWorkoutStepsComponent.vue'
import BarChartComponent from '@/components/GeneralComponents/BarChartComponent.vue'
// Import Notivue push
import { push } from 'notivue'
// Import the utils
import { getHrBarChartData } from '@/utils/chartUtils'
import {
  formatPaceMetric,
  formatPaceImperial,
  formatPaceSwimMetric,
  formatPaceSwimImperial,
  formatAverageSpeedMetric,
  formatAverageSpeedImperial,
  activityTypeIsCycling,
  activityTypeNotCycling,
  activityTypeIsSwimming,
  activityTypeIsRowing,
  activityTypeIsSailing,
  activityTypeNotSailing,
  activityTypeIsWindsurf,
  activityTypeNotWindsurf
} from '@/utils/activityUtils'
import { formatSecondsToMinutes } from '@/utils/dateTimeUtils'
import { metersToFeet } from '@/utils/unitsUtils'

// Define props
const props = defineProps({
  activity: {
    type: Object,
    required: true
  },
  activityActivityLaps: {
    type: [Object, null],
    required: true
  },
  activityActivityWorkoutSteps: {
    type: [Object, null],
    required: true
  },
  activityActivityStreams: {
    type: [Object, null],
    required: true
  },
  units: {
    type: Number,
    default: 1
  },
  activityActivityExerciseTitles: {
    type: [Object, null],
    required: true
  },
  activityActivitySets: {
    type: [Object, null],
    required: true
  },
  compareActivity: {
    type: Object,
    required: true
  },
  compareActivityActivityLaps: {
    type: [Object, null],
    required: true
  },
  compareActivityActivityWorkoutSteps: {
    type: [Object, null],
    required: true
  },
  compareActivityActivityStreams: {
    type: [Object, null],
    required: true
  },
  units: {
    type: Number,
    default: 1
  },
  compareActivityActivityExerciseTitles: {
    type: [Object, null],
    required: true
  },
  compareActivityActivitySets: {
    type: [Object, null],
    required: true
  }
})

// Setup composables and reactive data
const { t } = useI18n()
const hrPresent = ref(false)
const powerPresent = ref(false)
const elePresent = ref(false)
const cadPresent = ref(false)
const velPresent = ref(false)
const pacePresent = ref(false)
const formattedPace = ref(null)
const hrZones = ref({})

const compareHrPresent = ref(false)
const comparePowerPresent = ref(false)
const compareElePresent = ref(false)
const compareCadPresent = ref(false)
const compareVelPresent = ref(false)
const comparePacePresent = ref(false)
const compareFormattedPace = ref(null)
const compareHrZones = ref({})

console.log('compareActivity: ', props.compareActivity)

onMounted(async () => {
  try {
    if (props.activityActivityStreams && props.activityActivityStreams.length > 0) {
      // Check if the activity has the streams
      for (let i = 0; i < props.activityActivityStreams.length; i++) {
        if (props.activityActivityStreams[i].stream_type === 1) {
          hrPresent.value = true
          // If HR zones are present, add them to the hrZones object
          const hrStream = props.activityActivityStreams.find(
            (stream) => stream.hr_zone_percentages
          )
          hrZones.value =
            hrStream && hrStream.hr_zone_percentages ? hrStream.hr_zone_percentages : {}
        }
        if (props.activityActivityStreams[i].stream_type === 2) {
          powerPresent.value = true
        }
        if (props.activityActivityStreams[i].stream_type === 3) {
          cadPresent.value = true
        }
        if (props.activityActivityStreams[i].stream_type === 4) {
          elePresent.value = true
        }
        if (props.activityActivityStreams[i].stream_type === 5) {
          if (
            activityTypeIsCycling(props.activity) ||
            activityTypeIsSailing(props.activity) ||
            activityTypeIsWindsurf(props.activity)
          ) {
            velPresent.value = true
          }
        }
        if (props.activityActivityStreams[i].stream_type === 6) {
          if (
            activityTypeNotCycling(props.activity) &&
            activityTypeNotSailing(props.activity) &&
            activityTypeNotWindsurf(props.activity)
          ) {
            pacePresent.value = true
          }
        }
      }
    }
  } catch (error) {
    // If there is an error, set the error message and show the error alert.
    push.error(
      `${t('activityMandAbovePillsComponent.errorMessageProcessingActivityStreams')} - ${error}`
    )
  }

  try {
    if (props.compareActivityActivityStreams && props.compareActivityActivityStreams.length > 0) {
      // Check if the compareActivity has the streams
      for (let i = 0; i < props.compareActivityActivityStreams.length; i++) {
        if (props.compareActivityActivityStreams[i].stream_type === 1) {
          compareHrPresent.value = true
          // If HR zones are present, add them to the hrZones object
          const hrStream = props.compareActivityActivityStreams.find(
            (stream) => stream.hr_zone_percentages
          )
          compareHrZones.value =
            hrStream && hrStream.hr_zone_percentages ? hrStream.hr_zone_percentages : {}
        }
        if (props.compareActivityActivityStreams[i].stream_type === 2) {
          comparePowerPresent.value = true
        }
        if (props.compareActivityActivityStreams[i].stream_type === 3) {
          compareCadPresent.value = true
        }
        if (props.compareActivityActivityStreams[i].stream_type === 4) {
          compareElePresent.value = true
        }
        if (props.compareActivityActivityStreams[i].stream_type === 5) {
          if (
            activityTypeIsCycling(props.compareActivity) ||
            activityTypeIsSailing(props.compareActivity) ||
            activityTypeIsWindsurf(props.compareActivity)
          ) {
            compareVelPresent.value = true
          }
        }
        if (props.compareActivityActivityStreams[i].stream_type === 6) {
          if (
            activityTypeNotCycling(props.compareActivity) &&
            activityTypeNotSailing(props.compareActivity) &&
            activityTypeNotWindsurf(props.compareActivity)
          ) {
            comparePacePresent.value = true
          }
        }
      }
    }
  } catch (error) {
    // If there is an error, set the error message and show the error alert.
    push.error(
      `${t('activityMandAbovePillsComponent.errorMessageProcessingActivityStreams')} - ${error}`
    )
  }

  try {
    if (activityTypeIsSwimming(props.activity) || activityTypeIsRowing(props.activity)) {
      if (Number(props.units) === 1) {
        formattedPace.value = computed(() => formatPaceSwimMetric(props.activity.pace))
      } else {
        formattedPace.value = computed(() => formatPaceSwimImperial(props.activity.pace))
      }
    } else {
      if (Number(props.units) === 1) {
        formattedPace.value = computed(() => formatPaceMetric(props.activity.pace))
      } else {
        formattedPace.value = computed(() => formatPaceImperial(props.activity.pace))
      }
    }
  } catch (error) {
    push.error(`${t('activitySummaryComponent.errorFetchingUserById')} - ${error}`)
  }

  try {
    if (
      activityTypeIsSwimming(props.compareActivity) ||
      activityTypeIsRowing(props.compareActivity)
    ) {
      if (Number(props.units) === 1) {
        compareFormattedPace.value = computed(() =>
          formatPaceSwimMetric(props.compareActivity.pace)
        )
      } else {
        compareFormattedPace.value = computed(() =>
          formatPaceSwimImperial(props.compareActivity.pace)
        )
      }
    } else {
      if (Number(props.units) === 1) {
        compareFormattedPace.value = computed(() => formatPaceMetric(props.compareActivity.pace))
      } else {
        compareFormattedPace.value = computed(() => formatPaceImperial(props.compareActivity.pace))
      }
    }
  } catch (error) {
    push.error(`${t('activitySummaryComponent.errorFetchingUserById')} - ${error}`)
  }
})
</script>
