<template>
  <div v-if="isLoading">
    <LoadingComponent />
  </div>

  <div v-else>
    <div ref="activityMap" class="map rounded w-100" style="height: 500px"></div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch, nextTick } from 'vue'
import L from 'leaflet'
import LoadingComponent from '@/components/GeneralComponents/LoadingComponent.vue'
import { activityStreams } from '@/services/activityStreams'
import { useAuthStore } from '@/stores/authStore'
import { push } from 'notivue'
import { useI18n } from 'vue-i18n'

const props = defineProps({
  activity: { type: Object, required: true },
  comparedActivity: { type: Object, required: true },
  source: { type: String, required: true }
})

const { t } = useI18n()
const authStore = useAuthStore()
const isLoading = ref(true)
const activityStreamLatLng = ref(null)
const comparedActivityStreamLatLng = ref(null)
const activityMap = ref(null)
const leafletMap = ref(null)

onMounted(async () => {
  try {
    if (authStore.isAuthenticated) {
      activityStreamLatLng.value = await activityStreams.getActivitySteamByStreamTypeByActivityId(
        props.activity.id,
        7
      )
      comparedActivityStreamLatLng.value =
        await activityStreams.getActivitySteamByStreamTypeByActivityId(props.comparedActivity.id, 7)
    } else {
      activityStreamLatLng.value =
        await activityStreams.getPublicActivitySteamByStreamTypeByActivityId(props.activity.id, 7)
      comparedActivityStreamLatLng.value =
        await activityStreams.getPublicActivitySteamByStreamTypeByActivityId(
          props.comparedActivity.id,
          7
        )
    }
  } catch (error) {
    push.error(`${t('activityMapComponent.errorFetchingActivityStream')} - ${error}`)
  } finally {
    isLoading.value = false
    nextTick(() => {
      nextTick(() => {
        if (activityStreamLatLng.value && comparedActivityStreamLatLng.value) {
          initMap()
        }
      })
    })
  }
})

onUnmounted(() => {
  if (leafletMap.value) {
    leafletMap.value.remove()
    leafletMap.value = null
  }
})

const initMap = () => {
  if (!activityMap.value) return

  // Destroy previous map instance if exists
  if (leafletMap.value) {
    leafletMap.value.remove()
    leafletMap.value = null
  }

  leafletMap.value = L.map(activityMap.value, {
    dragging: props.source === 'activity',
    touchZoom: props.source === 'activity',
    scrollWheelZoom: props.source === 'activity',
    zoomControl: props.source === 'activity'
  }).fitWorld()

  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '© OpenStreetMap contributors'
  }).addTo(leafletMap.value)

  const bounds = []

  // -------- Primary activity route (blue) --------
  if (activityStreamLatLng.value?.stream_waypoints) {
    const latlngs = activityStreamLatLng.value.stream_waypoints
      .filter((wp) => wp.lat && wp.lon)
      .map((wp) => [wp.lat, wp.lon])

    if (latlngs.length) {
      L.polyline(latlngs, {
        color: '#2563eb',
        weight: 4,
        opacity: 0.8,
        lineJoin: 'round',
        lineCap: 'round'
      }).addTo(leafletMap.value)

      bounds.push(...latlngs)

      L.circleMarker(latlngs[0], {
        radius: 5,
        color: '#2563eb',
        fillColor: '#2563eb',
        fillOpacity: 1
      }).addTo(leafletMap.value)

      L.circleMarker(latlngs[latlngs.length - 1], {
        radius: 5,
        color: '#2563eb',
        fillColor: '#2563eb',
        fillOpacity: 1
      }).addTo(leafletMap.value)
    }
  }

  // -------- Compared activity route (red) --------
  if (comparedActivityStreamLatLng.value?.stream_waypoints) {
    const latlngs = comparedActivityStreamLatLng.value.stream_waypoints
      .filter((wp) => wp.lat && wp.lon)
      .map((wp) => [wp.lat, wp.lon])

    if (latlngs.length) {
      L.polyline(latlngs, {
        color: '#ef4444',
        weight: 4,
        opacity: 0.8,
        lineJoin: 'round',
        lineCap: 'round'
      }).addTo(leafletMap.value)

      bounds.push(...latlngs)

      L.circleMarker(latlngs[0], {
        radius: 5,
        color: '#ef4444',
        fillColor: '#ef4444',
        fillOpacity: 1
      }).addTo(leafletMap.value)

      L.circleMarker(latlngs[latlngs.length - 1], {
        radius: 5,
        color: '#ef4444',
        fillColor: '#ef4444',
        fillOpacity: 1
      }).addTo(leafletMap.value)
    }
  }

  // Fit map to both routes
  if (bounds.length) {
    leafletMap.value.fitBounds(bounds)
  }
}

watch(
  () => props.activityActivityMedia,
  async (newVal, oldVal) => {
    await nextTick() // wait for DOM to update with the new v-if block
    if (activityStreamLatLng.value) {
      initMap()
    }
  },
  { deep: true }
)
</script>

<style scoped>
/* Start marker - green dot */
:deep(.start-marker) {
  width: 16px;
  height: 16px;
  border-radius: 50%;
  background-color: #28a745;
  border: 3px solid white;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.4);
  margin-left: -8px;
  margin-top: -8px;
}

/* End marker - red dot */
:deep(.end-marker) {
  width: 16px;
  height: 16px;
  border-radius: 50%;
  background-color: #dc3545;
  border: 3px solid white;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.4);
  margin-left: -8px;
  margin-top: -8px;
}
</style>
