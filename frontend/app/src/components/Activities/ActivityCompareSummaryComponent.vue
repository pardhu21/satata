<template>
  <div v-if="isLoading">
    <LoadingComponent />
  </div>
  <div v-else>
    <div
      class="d-flex flex-column flex-md-row align-items-stretch justify-content-between w-100 gap-4"
    >
      <!-- Activity one -->
      <div class="d-flex flex-md-grow-0 justify-content-between w-100 w-lg-50">
        <!-- user name and photo zone -->
        <div class="d-flex align-items-center">
          <UserAvatarComponent :user="userActivity" :width="55" :height="55" />
          <div class="ms-3 me-3">
            <div class="fw-bold">
              <span v-if="userActivity">
                <router-link
                  :to="{ name: 'user', params: { id: userActivity.id } }"
                  class="link-body-emphasis link-underline-opacity-0 link-underline-opacity-100-hover"
                >
                  {{ userActivity.name }}
                </router-link>
              </span>
              <span v-else>
                {{ $t('activitySummaryComponent.userNameHidden') }}
              </span>
            </div>
            <h6>
              <!-- Display the visibility of the activity -->
              <span v-if="activity.visibility == 0">
                <font-awesome-icon :icon="['fas', 'globe']" />
                {{ $t('activitySummaryComponent.visibilityPublic') }}
              </span>
              <span v-if="activity.visibility == 1">
                <font-awesome-icon :icon="['fas', 'users']" v-if="activity.visibility == 1" />
                {{ $t('activitySummaryComponent.visibilityFollowers') }}
              </span>
              <span v-if="activity.visibility == 2">
                <font-awesome-icon :icon="['fas', 'lock']" v-if="activity.visibility == 2" />
                {{ $t('activitySummaryComponent.visibilityPrivate') }}
              </span>
              <span> - </span>

              <!-- Display the activity type -->
              <span>
                <font-awesome-icon class="me-1" :icon="getIcon(activity.activity_type)" />
                <span v-if="activity.activity_type === 3 || activity.activity_type === 7">{{
                  $t('activitySummaryComponent.labelVirtual')
                }}</span>
              </span>

              <!-- Display the date and time -->
              <span v-if="activity.start_time_tz_applied">
                {{ formatDateMed(activity.start_time_tz_applied) }} @
                {{ formatTime(activity.start_time_tz_applied) }}
              </span>
              <!-- Conditionally display city and country -->
              <span v-if="activity.city || activity.town || activity.country">
                -
                <span>{{ formatLocation(t, activity) }}</span>
              </span>
            </h6>
          </div>
        </div>
        <div class="dropdown d-flex" v-if="activity.user_id == authStore.user.id">
          <a
            class="btn btn-link btn-lg link-body-emphasis"
            :href="`https://www.strava.com/activities/${activity.strava_activity_id}`"
            role="button"
            v-if="activity.strava_activity_id"
          >
            <font-awesome-icon :icon="['fab', 'fa-strava']" />
          </a>
          <a
            class="btn btn-link btn-lg link-body-emphasis"
            :href="`https://connect.garmin.com/modern/activity/${activity.garminconnect_activity_id}`"
            role="button"
            v-if="activity.garminconnect_activity_id"
          >
            <img :src="INTEGRATION_LOGOS.garminConnectApp" alt="Garmin Connect logo" height="22" />
          </a>
        </div>
      </div>

      <!-- Mobile -->
      <div class="d-block d-md-none border-top w-100"></div>

      <!-- Desktop -->
      <div class="d-none d-md-flex align-items-stretch">
        <div class="border-start"></div>
      </div>

      <!-- Compared Activity -->
      <div class="d-flex flex-md-grow-0 justify-content-between w-100 w-lg-50">
        <!-- user name and photo zone -->
        <div class="d-flex align-items-center">
          <UserAvatarComponent :user="userActivity" :width="55" :height="55" />
          <div class="ms-3 me-3">
            <div class="fw-bold">
              <span v-if="userActivity">
                <router-link
                  :to="{ name: 'user', params: { id: userActivity.id } }"
                  class="link-body-emphasis link-underline-opacity-0 link-underline-opacity-100-hover"
                >
                  {{ userActivity.name }}
                </router-link>
              </span>
              <span v-else>
                {{ $t('activitySummaryComponent.userNameHidden') }}
              </span>
            </div>
            <h6>
              <!-- Display the visibility of the activity -->
              <span v-if="comparedActivity.visibility == 0">
                <font-awesome-icon :icon="['fas', 'globe']" />
                {{ $t('activitySummaryComponent.visibilityPublic') }}
              </span>
              <span v-if="comparedActivity.visibility == 1">
                <font-awesome-icon
                  :icon="['fas', 'users']"
                  v-if="comparedActivity.visibility == 1"
                />
                {{ $t('activitySummaryComponent.visibilityFollowers') }}
              </span>
              <span v-if="comparedActivity.visibility == 2">
                <font-awesome-icon
                  :icon="['fas', 'lock']"
                  v-if="comparedActivity.visibility == 2"
                />
                {{ $t('activitySummaryComponent.visibilityPrivate') }}
              </span>
              <span> - </span>

              <!-- Display the activity type -->
              <span>
                <font-awesome-icon class="me-1" :icon="getIcon(comparedActivity.activity_type)" />
                <span
                  v-if="
                    comparedActivity.activity_type === 3 || comparedActivity.activity_type === 7
                  "
                  >{{ $t('activitySummaryComponent.labelVirtual') }}</span
                >
              </span>

              <!-- Display the date and time -->
              <span v-if="comparedActivity.start_time_tz_applied">
                {{ formatDateMed(comparedActivity.start_time_tz_applied) }} @
                {{ formatTime(comparedActivity.start_time_tz_applied) }}
              </span>
              <!-- Conditionally display city and country -->
              <span
                v-if="comparedActivity.city || comparedActivity.town || comparedActivity.country"
              >
                -
                <span>{{ formatLocation(t, comparedActivity) }}</span>
              </span>
            </h6>
          </div>
        </div>
        <div class="dropdown d-flex" v-if="comparedActivity.user_id == authStore.user.id">
          <a
            class="btn btn-link btn-lg link-body-emphasis"
            :href="`https://www.strava.com/activities/${comparedActivity.strava_activity_id}`"
            role="button"
            v-if="comparedActivity.strava_activity_id"
          >
            <font-awesome-icon :icon="['fab', 'fa-strava']" />
          </a>
          <a
            class="btn btn-link btn-lg link-body-emphasis"
            :href="`https://connect.garmin.com/modern/activity/${comparedActivity.garminconnect_activity_id}`"
            role="button"
            v-if="comparedActivity.garminconnect_activity_id"
          >
            <img :src="INTEGRATION_LOGOS.garminConnectApp" alt="Garmin Connect logo" height="22" />
          </a>
        </div>
      </div>
    </div>

    <!-- Activity title -->
    <div class="d-flex flex-row align-items-stretch justify-content-between w-100 gap-4">
      <!-- Activiy one -->
      <div class="d-flex flex-md-grow-0 justify-content-between w-50">
        <h1>
          <span v-if="activity.name === 'Workout'">{{ formatName(activity, t) }}</span>
          <span v-else>{{ activity.name }}</span>
        </h1>
      </div>

      <!-- Desktop -->
      <div class="d-flex align-items-stretch">
        <div class="border-start"></div>
      </div>

      <!-- Compared Activity -->
      <div class="d-flex flex-md-grow-0 justify-content-between w-50">
        <h1>
          <span v-if="comparedActivity.name === 'Workout'">{{
            formatName(comparedActivity, t)
          }}</span>
          <span v-else>{{ comparedActivity.name }}</span>
        </h1>
      </div>
    </div>

    <!-- Activity description -->
    <div
      class="d-flex flex-column flex-md-row align-items-stretch justify-content-between w-100 gap-4 mt-3"
    >
      <!-- Activity one description -->
      <div class="w-100 w-md-50">
        <p v-if="activity.description" class="mb-0">
          {{ activity.description }}
        </p>

        <div v-if="activity.private_notes" class="mt-3">
          <h6 class="text-body-secondary">
            {{ $t('activitySummaryComponent.privateNotes') }}
          </h6>
          <p class="mb-0">{{ activity.private_notes }}</p>
        </div>
      </div>

      <!-- Divider -->
      <div class="d-flex align-items-stretch justify-content-center">
        <div class="border-top border-md-start w-100 align-self-md-stretch"></div>
      </div>

      <!-- Compared activity description -->
      <div class="w-100 w-md-50">
        <p v-if="comparedActivity.description" class="mb-0">
          {{ comparedActivity.description }}
        </p>

        <div v-if="comparedActivity.private_notes" class="mt-3">
          <h6 class="text-body-secondary">
            {{ $t('activitySummaryComponent.privateNotes') }}
          </h6>
          <p class="mb-0">{{ comparedActivity.private_notes }}</p>
        </div>
      </div>
    </div>

    <!-- Activity summary -->
    <!-- distance -->
    <div class="row mt-3 align-items-center text-start">
      <ActivityCompareMetricComponent
        v-if="
          activity.activity_type != 10 &&
          activity.activity_type != 14 &&
          activity.activity_type != 18 &&
          activity.activity_type != 19 &&
          activity.activity_type != 20 &&
          activity.activity_type != 41 &&
          activityTypeNotRacquet(activity)
        "
        :label="$t('activitySummaryComponent.activityDistance')"
        :value="formatDistance(t, activity, units)"
        :comparedValue="formatDistance(t, comparedActivity, units)"
        :compare="true"
      />

      <!-- calories -->
      <ActivityCompareSummaryComponent
        v-else
        :label="$t('activitySummaryComponent.activityCalories')"
        :value="formatCalories(t, activity.calories)"
        :comparedValue="formatCalories(t, comparedActivity.calories)"
        :compare="true"
      />
      <!-- activity time-->
      <ActivityCompareMetricComponent
        :label="$t('activitySummaryComponent.activityTime')"
        :value="formatSecondsToMinutes(activity.total_elapsed_time)"
        :comparedValue="formatSecondsToMinutes(comparedActivity.total_elapsed_time)"
        :compare="true"
      />
      <div class="col border-start border-opacity-50">
        <!-- elevation -->
        <ActivityCompareMetricComponent
          v-if="activityTypeIsCycling(activity)"
          :label="$t('activitySummaryComponent.activityEleGain')"
          :value="formatElevation(t, activity.elevation_gain, units)"
          :comparedValue="formatElevation(t, comparedActivity.elevation_gain, units)"
          :compare="true"
        />
        <!-- pace -->
        <ActivityCompareMetricComponent
          v-else-if="
            activity.activity_type != 10 &&
            activity.activity_type != 14 &&
            activity.activity_type != 18 &&
            activity.activity_type != 19 &&
            activity.activity_type != 20 &&
            activityTypeNotWindsurf(activity) &&
            activity.activity_type != 41 &&
            activityTypeNotSailing(activity) &&
            activityTypeNotRacquet(activity)
          "
          :label="$t('activitySummaryComponent.activityPace')"
          :value="formatPace(t, activity, units)"
          :comparedValue="formatPace(t, comparedActivity, units)"
          :compare="true"
        />
        <!-- avg_speed sailing activities -->
        <ActivityCompareMetricComponent
          v-else-if="activityTypeIsSailing(activity)"
          :label="$t('activitySummaryComponent.activityAvgSpeed')"
          :value="formatAverageSpeed(t, activity, units)"
          :comparedValue="formatAverageSpeed(t, comparedActivity, units)"
          :compare="true"
        />
        <!-- avg_hr -->
        <ActivityCompareMetricComponent
          v-else
          :label="$t('activitySummaryComponent.activityAvgHR')"
          :value="formatHr(t, activity.average_hr)"
          :comparedValue="formatHr(t, comparedActivity.average_hr)"
          :compare="true"
        />
      </div>
    </div>
    <div
      class="row d-flex mt-3"
      v-if="
        source === 'activity' &&
        activity.activity_type != 10 &&
        activity.activity_type != 14 &&
        activity.activity_type != 18 &&
        activity.activity_type != 19 &&
        activity.activity_type != 20 &&
        activity.activity_type != 41 &&
        activityTypeNotRacquet(activity)
      "
    >
      <!-- avg_power (running & cycling) -->
      <ActivityCompareMetricComponent
        v-if="activityTypeIsCycling(activity) || activityTypeIsRunning(activity)"
        :label="$t('activitySummaryComponent.activityAvgPower')"
        :value="formatPower(t, activity.average_power)"
        :comparedValue="formatPower(t, comparedActivity.average_power)"
        :compare="true"
      />

      <!-- avg_hr (non running & cycling) -->
      <ActivityCompareMetricComponent
        v-if="activityTypeNotCycling(activity) && activityTypeNotRunning(activity)"
        :label="$t('activitySummaryComponent.activityAvgHR')"
        :value="formatHr(t, activity.average_hr)"
        :comparedValue="formatHr(t, comparedActivity.average_hr)"
        :compare="true"
      />

      <!-- max_hr -->
      <ActivityCompareMetricComponent
        v-if="activityTypeNotCycling(activity) && activityTypeNotRunning(activity)"
        class="border-start border-opacity-50"
        :label="$t('activitySummaryComponent.activityMaxHR')"
        :value="formatHr(t, activity.max_hr)"
        :comparedValue="formatHr(t, comparedActivity.max_hr)"
        :compare="true"
      />

      <!-- elevation gain (running) -->
      <ActivityCompareMetricComponent
        v-if="activityTypeIsRunning(activity)"
        class="border-start border-opacity-50"
        :label="$t('activitySummaryComponent.activityEleGain')"
        :value="formatElevation(t, activity.elevation_gain, units)"
        :comparedValue="formatElevation(t, comparedActivity.elevation_gain, units)"
        :compare="true"
      />

      <!-- avg_speed (cycling) -->
      <ActivityCompareMetricComponent
        v-if="activityTypeIsCycling(activity)"
        class="border-start border-opacity-50"
        :label="$t('activitySummaryComponent.activityAvgSpeed')"
        :value="formatAverageSpeed(t, activity, units)"
        :comparedValue="formatAverageSpeed(t, comparedActivity, units)"
        :compare="true"
      />

      <!-- calories -->
      <ActivityCompareMetricComponent
        class="border-start border-opacity-50"
        :label="$t('activitySummaryComponent.activityCalories')"
        :value="formatCalories(t, activity.calories)"
        :comparedValue="formatCalories(t, comparedActivity.calories)"
        :compare="true"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
// Importing the stores
import { useAuthStore } from '@/stores/authStore'
import { useServerSettingsStore } from '@/stores/serverSettingsStore'
// Import Notivue push
import { push } from 'notivue'
// Importing the components
import LoadingComponent from '@/components/GeneralComponents/LoadingComponent.vue'
import UserAvatarComponent from '@/components/Users/UserAvatarComponent.vue'
import ActivityCompareMetricComponent from './ActivityCompareMetricComponent.vue'
// Importing constants
import { INTEGRATION_LOGOS } from '@/constants/integrationLogoConstants'
// Importing the services
import { users } from '@/services/usersService'
// Importing the utils
import {
  formatDistance,
  formatElevation,
  formatPace,
  formatHr,
  formatCalories,
  getIcon,
  formatLocation,
  formatAverageSpeed,
  formatPower,
  activityTypeIsCycling,
  activityTypeNotCycling,
  activityTypeIsRunning,
  activityTypeNotRunning,
  activityTypeNotRacquet,
  activityTypeNotWindsurf,
  activityTypeIsWindsurf,
  activityTypeNotSailing,
  activityTypeIsSailing,
  formatName
} from '@/utils/activityUtils'
import { formatDateMed, formatTime, formatSecondsToMinutes } from '@/utils/dateTimeUtils'

// Props
const props = defineProps({
  activity: {
    type: Object,
    required: true
  },
  comparedActivity: {
    type: Object,
    required: true
  },
  source: {
    type: String,
    required: true
  },
  units: {
    type: String,
    default: 'metric'
  }
})

// Composables
const authStore = useAuthStore()
const serverSettingsStore = useServerSettingsStore()
const { t } = useI18n()

// Reactive data
const isLoading = ref(true)
const userActivity = ref(null)

// Lifecycle
onMounted(async () => {
  try {
    if (authStore.isAuthenticated) {
      userActivity.value = await users.getUserById(props.activity.user_id)
    } else {
      if (serverSettingsStore.serverSettings.public_shareable_links_user_info) {
        userActivity.value = await users.getPublicUserById(props.activity.user_id)
      }
    }
  } catch (error) {
    push.error(`${t('activitySummaryComponent.errorFetchingUserById')} - ${error}`)
  } finally {
    isLoading.value = false
  }
})
</script>
