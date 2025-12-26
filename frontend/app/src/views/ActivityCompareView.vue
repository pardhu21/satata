<template>
  <div
    class="bg-body-tertiary rounded p-3 shadow-sm flex-fill"
    :class="{ 'border border-warning border-2': activity?.is_hidden }"
  >
    <LoadingComponent v-if="isLoading" />

    <div v-else>
      <ActivityCompareSummaryComponent
        v-if="activity"
        :activity="activity"
        :comparedActivity="comparedActivity"
        :source="'activity'"
        :units="units"
      />
      <AlertComponent
        v-if="activity && activity.user_id === authStore.user.id && activity.is_hidden"
        :message="isHiddenMessage"
        :dismissible="true"
        :type="'warning'"
        class="mt-2"
      />
      <AlertComponent
        v-if="
          activity &&
          activity.user_id === authStore.user.id &&
          (activity.hide_start_time ||
            activity.hide_location ||
            activity.hide_map ||
            activity.hide_hr ||
            activity.hide_power ||
            activity.hide_cadence ||
            activity.hide_elevation ||
            activity.hide_speed ||
            activity.hide_pace ||
            activity.hide_laps ||
            activity.hide_workout_sets_steps)
        "
        :message="alertPrivacyMessage"
        :dismissible="true"
        class="mt-2"
      />
    </div>

    <!-- map zone -->
    <div class="mt-3 mb-3" v-if="isLoading">
      <LoadingComponent />
    </div>
    <div
      class="mt-3 mb-3"
      v-else-if="
        activity &&
        ((authStore.isAuthenticated && authStore.user.id === activity.user_id) ||
          (authStore.isAuthenticated &&
            authStore.user.id !== activity.user_id &&
            activity.hide_map === false) ||
          (!authStore.isAuthenticated && activity.hide_map === false))
      "
    >
      <ActivityMapCompareComponent
        :activity="activity"
        :comparedActivity="comparedActivity"
        source="activity"
      />
    </div>

    <!-- graphs -->
    <hr
      class="mb-2 mt-2"
      v-if="
        activity &&
        ((activityActivityLaps && activityActivityLaps.length > 0) ||
          (activityActivityWorkoutSteps && activityActivityWorkoutSteps.length > 0) ||
          (activityActivitySets && activityActivitySets.length > 0) ||
          (activityActivityStreams && activityActivityStreams.length > 0))
      "
    />

    <!-- graphs and laps medium and above screens -->
    <div class="d-none d-lg-block" v-if="isLoading">
      <LoadingComponent />
    </div>
    <div
      class="d-none d-lg-block"
      v-else-if="
        activity &&
        ((activityActivityLaps && activityActivityLaps.length > 0) ||
          (activityActivityWorkoutSteps && activityActivityWorkoutSteps.length > 0) ||
          (activityActivitySets && activityActivitySets.length > 0) ||
          (activityActivityStreams && activityActivityStreams.length > 0))
      "
    >
      <ActivityMandAbovePillsComponent
        :activity="activity"
        :activityActivityLaps="activityActivityLaps"
        :activityActivityWorkoutSteps="activityActivityWorkoutSteps"
        :activityActivityStreams="activityActivityStreams"
        :units="units"
        :activityActivityExerciseTitles="activityActivityExerciseTitles"
        :activityActivitySets="activityActivitySets"
      />
    </div>

    <!-- graphs and laps screens bellow medium -->
    <div class="d-lg-none d-block" v-if="isLoading">
      <LoadingComponent />
    </div>
    <div
      class="d-lg-none d-block"
      v-else-if="
        activity &&
        ((activityActivityLaps && activityActivityLaps.length > 0) ||
          (activityActivityWorkoutSteps && activityActivityWorkoutSteps.length > 0) ||
          (activityActivitySets && activityActivitySets.length > 0) ||
          (activityActivityStreams && activityActivityStreams.length > 0))
      "
    >
      <ActivityCompareBellowMPillsComponent
        :activity="activity"
        :activityActivityLaps="activityActivityLaps"
        :activityActivityWorkoutSteps="activityActivityWorkoutSteps"
        :activityActivityStreams="activityActivityStreams"
        :units="units"
        :activityActivityExerciseTitles="activityActivityExerciseTitles"
        :activityActivitySets="activityActivitySets"
        :compareActivity="comparedActivity"
        :compareActivityActivityLaps="comparedActivityActivityLaps"
        :compareActivityActivityWorkoutSteps="comparedActivityActivityWorkoutSteps"
        :compareActivityActivityStreams="comparedActivityActivityStreams"
        :compareActivityActivityExerciseTitles="comparedActivityActivityExerciseTitles"
        :compareActivityActivitySets="comparedActivityActivitySets"
      />
    </div>

    <!-- back button -->
    <BackButtonComponent />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRoute, useRouter } from 'vue-router'
// Importing the stores
import { useAuthStore } from '@/stores/authStore'
import { useServerSettingsStore } from '@/stores/serverSettingsStore'
// Import Notivue push
import { push } from 'notivue'
// Importing the components
import ActivityCompareSummaryComponent from '@/components/Activities/ActivityCompareSummaryComponent.vue'
import ActivityMapCompareComponent from '@/components/Activities/ActivityMapCompareComponent.vue'
import ActivityMandAbovePillsComponent from '@/components/Activities/ActivityMandAbovePillsComponent.vue'
import ActivityCompareBellowMPillsComponent from '@/components/Activities/ActivityCompareBellowMPillsComponent.vue'
import LoadingComponent from '@/components/GeneralComponents/LoadingComponent.vue'
import BackButtonComponent from '@/components/GeneralComponents/BackButtonComponent.vue'
import AlertComponent from '@/components/GeneralComponents/AlertComponent.vue'
// Importing the services
import { activities } from '@/services/activitiesService'
import { activityStreams } from '@/services/activityStreams'
import { activityLaps } from '@/services/activityLapsService'
import { activityWorkoutSteps } from '@/services/activityWorkoutStepsService'
import { activityExerciseTitles } from '@/services/activityExerciseTitlesService'
import { activitySets } from '@/services/activitySetsService'
import { activityMedia } from '@/services/activityMediaService'

const { t } = useI18n()
const authStore = useAuthStore()
const serverSettingsStore = useServerSettingsStore()
const route = useRoute()
const router = useRouter()
const isLoading = ref(true)
const activity = ref(null)
const activityActivityStreams = ref([])
const activityActivityLaps = ref([])
const activityActivityWorkoutSteps = ref([])
const activityActivityMedia = ref([])
const activityActivityExerciseTitles = ref([])
const activityActivitySets = ref([])
const comparedActivity = ref(null)
const comparedActivityActivityStreams = ref([])
const comparedActivityActivityLaps = ref([])
const comparedActivityActivityWorkoutSteps = ref([])
const comparedActivityActivityMedia = ref([])
const comparedActivityActivityExerciseTitles = ref([])
const comparedActivityActivitySets = ref([])
const units = ref(1)
const alertPrivacyMessage = ref(null)
const isHiddenMessage = ref(null)

const activityId = route.params.id1

const compareActivityId = route.params.id2

onMounted(async () => {
  try {
    // Get the activity by id
    if (authStore.isAuthenticated) {
      activity.value = await activities.getActivityById(activityId)
      comparedActivity.value = await activities.getActivityById(compareActivityId)
    } else {
      if (serverSettingsStore.serverSettings.public_shareable_links) {
        activity.value = await activities.getPublicActivityById(activityId)
        comparedActivity.value = await activities.getPublicActivityById(compareActivityId)
        if (!activity.value) {
          return router.push({
            path: '/login',
            query: { errorPublicActivityNotFound: 'true' }
          })
        }
        if (!comparedActivity.value) {
          return router.push({
            path: '/login',
            query: { errorPublicActivityNotFound: 'true' }
          })
        }
      } else {
        return router.push({
          path: '/login',
          query: { errorpublic_shareable_links: 'true' }
        })
      }
    }

    // Check if the activities exists
    if (!activity.value || !comparedActivity.value) {
      return router.push({
        path: '/',
        query: { activityFound: 'false', id: !activityId ? activityId : compareActivityId }
      })
    }

    if (authStore.isAuthenticated) {
      // Set the units
      units.value = authStore.user.units

      // Get the activity streams by activity id
      activityActivityStreams.value =
        await activityStreams.getActivitySteamsByActivityId(activityId)

      // Get the compared activity streams by compared activity id
      comparedActivityActivityStreams.value =
        await activityStreams.getActivitySteamsByActivityId(compareActivityId)

      // Get the activity laps by activity id
      activityActivityLaps.value = await activityLaps.getActivityLapsByActivityId(activityId)

      // Get the compared activity laps by compared activity id
      comparedActivityActivityLaps.value =
        await activityLaps.getActivityLapsByActivityId(compareActivityId)

      // Get the activity workout steps by activity id
      activityActivityWorkoutSteps.value =
        await activityWorkoutSteps.getActivityWorkoutStepsByActivityId(activityId)

      // Get the compared activity workout steps by compared activity id
      comparedActivityActivityWorkoutSteps.value =
        await activityWorkoutSteps.getActivityWorkoutStepsByActivityId(compareActivityId)

      // Get the activity exercise titles
      activityActivityExerciseTitles.value =
        await activityExerciseTitles.getActivityExerciseTitlesAll()

      // Get the compared activity exercise titles
      comparedActivityActivityExerciseTitles.value =
        await activityExerciseTitles.getActivityExerciseTitlesAll()

      // Get the activity sets by activity id
      activityActivitySets.value = await activitySets.getActivitySetsByActivityId(activityId)

      // Get the compared activity sets by compared activity id
      comparedActivityActivitySets.value =
        await activitySets.getActivitySetsByActivityId(compareActivityId)

      // Get the activity media by activity id
      activityActivityMedia.value = await activityMedia.getUserActivityMediaByActivityId(activityId)

      // Get the compared activity media by compared activity id
      comparedActivityActivityMedia.value =
        await activityMedia.getUserActivityMediaByActivityId(compareActivityId)
    } else {
      // Set the units
      units.value = serverSettingsStore.serverSettings.units

      // Get the activity streams by activity id
      activityActivityStreams.value =
        await activityStreams.getPublicActivityStreamsByActivityId(activityId)

      // Get the compared activity streams by compared activity id
      comparedActivityActivityStreams.value =
        await activityStreams.getPublicActivityStreamsByActivityId(compareActivityId)

      // Get the activity laps by activity id
      activityActivityLaps.value = await activityLaps.getPublicActivityLapsByActivityId(activityId)

      // Get the compared activity laps by compared activity id
      comparedActivityActivityLaps.value =
        await activityLaps.getPublicActivityLapsByActivityId(compareActivityId)

      // Get the activity workout steps by activity id
      activityActivityWorkoutSteps.value =
        await activityWorkoutSteps.getPublicActivityWorkoutStepsByActivityId(activityId)

      // Get the compared activity workout steps by compared activity id
      comparedActivityActivityWorkoutSteps.value =
        await activityWorkoutSteps.getPublicActivityWorkoutStepsByActivityId(compareActivityId)

      // Get the activity exercise titles
      activityActivityExerciseTitles.value =
        await activityExerciseTitles.getPublicActivityExerciseTitlesAll()

      // Get the compared activity exercise titles
      comparedActivityActivityExerciseTitles.value =
        await activityExerciseTitles.getPublicActivityExerciseTitlesAll()

      // Get the activity sets by activity id
      activityActivitySets.value = await activitySets.getPublicActivitySetsByActivityId(activityId)

      // Get the compared activity sets by compared activity id
      comparedActivityActivitySets.value =
        await activitySets.getPublicActivitySetsByActivityId(compareActivityId)
    }
  } catch (error) {
    if (error.toString().includes('422')) {
      router.push({
        path: '/',
        query: { activityFound: 'false', id: activityId }
      })
    }
    // If there is an error, set the error message and show the error alert.
    push.error(`${t('activityView.errorMessageActivityNotFound')} - ${error}`)
  }

  isLoading.value = false
  if (authStore.user.id === activity.value.user_id) {
    alertPrivacyMessage.value = t('activityView.alertPrivacyMessage')
    isHiddenMessage.value = t('activityView.isHiddenMessage')
  }
})
</script>
