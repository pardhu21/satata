<template>
  <div class="container">
    <div class="column">
      <div class="col-md-4 mb-3">
        <label for="activitySelect" class="form-label"><b>Activity</b></label>
        <select
          id="activitySelect"
          class="form-select"
          v-model="selectedActivityId"
          aria-label="Select activity"
        >
          <option v-for="act in activities" :key="act.id" :value="act.id">
            {{ act.name }}
          </option>
        </select>
        <div class="form-text mt-2">
          Select an activity to edit its category parameter defaults.
        </div>

        <div
          v-if="message"
          class="alert mt-3"
          :class="messageClass"
          role="status"
          aria-live="polite"
        >
          {{ message }}
        </div>
      </div>

      <div>
        <div class="card">
          <div class="card-body">
            <h5 class="card-title">Category parameter defaults</h5>
            <p class="card-text">
              Category is fixed per row. Edit numeric fields and Save to persist locally.
            </p>

            <div v-for="category in categories" :key="category.id" class="mb-4">
              <h6 class="mb-2">{{ category.display_name }}</h6>

              <div class="row g-2">
                <div class="col-12 col-md-4">
                  <div class="form-floating">
                    <input
                      type="number"
                      class="form-control"
                      :id="`distance_${category.id}`"
                      v-model.number="ruleFor(category.id).distance"
                      aria-label="Distance in meters"
                    />
                    <label :for="`distance_${category.id}`">Distance (m)</label>
                  </div>
                </div>

                <div class="col-12 col-md-4">
                  <div class="form-floating">
                    <input
                      type="number"
                      class="form-control"
                      :id="`hr_${category.id}`"
                      v-model.number="ruleFor(category.id).hr"
                      aria-label="Heart rate"
                    />
                    <label :for="`hr_${category.id}`">HR</label>
                  </div>
                </div>

                <div class="col-12 col-md-4">
                  <div class="form-floating">
                    <input
                      type="number"
                      class="form-control"
                      :id="`ele_${category.id}`"
                      v-model.number="ruleFor(category.id).elevation_gain"
                      aria-label="Elevation gain in meters"
                    />
                    <label :for="`ele_${category.id}`">Elev Gain (m)</label>
                  </div>
                </div>
              </div>

              <hr />
            </div>

            <!-- Save/Reset buttons placed at bottom of fields -->
            <div class="d-flex justify-content-end mt-3">
              <button
                type="button"
                class="btn btn-secondary me-2"
                @click="resetCurrentRules"
                :disabled="isSaving"
                aria-label="Reset rules to defaults for selected activity"
              >
                Reset
              </button>

              <button
                type="button"
                class="btn btn-primary"
                :disabled="isSaving"
                @click="saveCurrentRules"
                aria-label="Save rules for selected activity"
              >
                <span
                  v-if="isSaving"
                  class="spinner-border spinner-border-sm me-2"
                  aria-hidden="true"
                ></span>
                Save
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, watch } from 'vue'

/**
 * Temporary local types for the component
 */
interface Activity {
  id: number
  name: string
}
interface Category {
  id: number
  name: string
  display_name: string
}
interface RuleValues {
  distance: number | null
  hr: number | null
  elevation_gain: number | null
}

// Temporary activity list (will be fetched from backend later)
const activities = ref<Activity[]>([
  { id: 1, name: 'Running' },
  { id: 2, name: 'Cycling' },
  { id: 3, name: 'Swimming' }
])

// Canonical categories (will be fetched from backend later)
const categories = ref<Category[]>([
  { id: 1, name: 'recovery', display_name: 'Recovery' },
  { id: 2, name: 'easy', display_name: 'Easy' },
  { id: 3, name: 'steady', display_name: 'Steady' },
  { id: 4, name: 'tempo', display_name: 'Tempo' },
  { id: 5, name: 'threshold', display_name: 'Threshold' },
  { id: 6, name: 'vo2_max', display_name: 'VO₂ Max' },
  { id: 7, name: 'anaerobic', display_name: 'Anaerobic' },
  { id: 8, name: 'long', display_name: 'Long' },
  { id: 9, name: 'race', display_name: 'Race / Event' },
  { id: 10, name: 'mixed', display_name: 'Mixed / Structured' }
])

// Default rule values per category (single-value; will be provided by backend later)
const defaultRules: Record<number, RuleValues> = {
  1: { distance: 5000, hr: 105, elevation_gain: 75 },
  2: { distance: 9000, hr: 125, elevation_gain: 150 },
  3: { distance: 11500, hr: 143, elevation_gain: 250 },
  4: { distance: 12500, hr: 160, elevation_gain: 300 },
  5: { distance: 9500, hr: 173, elevation_gain: 350 },
  6: { distance: 6000, hr: 183, elevation_gain: 400 },
  7: { distance: 3250, hr: 190, elevation_gain: 250 },
  8: { distance: 27500, hr: 138, elevation_gain: 600 },
  9: { distance: 22500, hr: 180, elevation_gain: 1000 },
  10: { distance: 14000, hr: 155, elevation_gain: 500 }
}

function makeEmptyRule(): RuleValues {
  return {
    distance: null,
    hr: null,
    elevation_gain: null
  }
}

function getDefaultForCategory(catId: number): RuleValues {
  const d = defaultRules[catId]
  return d ? { ...d } : makeEmptyRule()
}

// Per-activity rules stored locally in the component state
// Initialize fully to avoid undefined accesses
const activityRules = reactive<Record<number, Record<number, RuleValues>>>(
  Object.fromEntries(
    activities.value.map((act) => [
      act.id,
      Object.fromEntries(
        categories.value.map((cat) => [cat.id, getDefaultForCategory(cat.id)])
      ) as Record<number, RuleValues>
    ])
  ) as Record<number, Record<number, RuleValues>>
)

// Ensure we have a safe selectedActivityId (fallback to first id or 0)
const selectedActivityId = ref<number>(activities.value[0]?.id ?? 0)

// workingRules will always return a defined object for the selected activity
const workingRules = computed<Record<number, RuleValues>>(() => {
  const aid = selectedActivityId.value
  // Lazily initialize activity rules for the selected activity to ensure all
  // category entries exist and are reactive. This prevents template v-model
  // errors when switching activities.
  if (!activityRules[aid]) {
    activityRules[aid] = Object.fromEntries(
      categories.value.map((cat) => [cat.id, getDefaultForCategory(cat.id)])
    ) as Record<number, RuleValues>
  }
  // Ensure every category key exists for this activity (handles dynamic categories)
  for (const cat of categories.value) {
    if (!activityRules[aid][cat.id]) {
      activityRules[aid][cat.id] = getDefaultForCategory(cat.id)
    }
  }
  return activityRules[aid] as Record<number, RuleValues>
})

const isSaving = ref(false)
const message = ref('')
const messageClass = ref('alert-success')

watch(selectedActivityId, () => {
  // Clear messages when switching
  message.value = ''
})

/**
 * Save current activity rules to local store (no backend yet).
 */
function saveCurrentRules(): void {
  isSaving.value = true
  message.value = ''
  // Simulate save delay
  setTimeout(() => {
    isSaving.value = false
    messageClass.value = 'alert-success'
    message.value = 'Rules saved locally.'
  }, 500)
}

/**
 * Reset current activity rules to canonical defaults.
 */
function resetCurrentRules(): void {
  const aid = selectedActivityId.value
  if (!activityRules[aid]) {
    activityRules[aid] = {} as Record<number, RuleValues>
  }
  for (const cat of categories.value) {
    const def = getDefaultForCategory(cat.id)
    activityRules[aid][cat.id] = { ...def }
  }
  messageClass.value = 'alert-info'
  message.value = 'Rules reset to defaults for selected activity.'
}

function ruleFor(catId: number): RuleValues {
  // Ensure workingRules for selected activity is initialized
  const wr = workingRules.value
  if (!wr[catId]) {
    wr[catId] = getDefaultForCategory(catId)
  }
  return wr[catId]
}
</script>
