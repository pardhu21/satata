<template>
  <!-- Compare button -->
  <div class="d-flex justify-content-end">
    <button class="btn btn-primary" data-bs-toggle="modal" data-bs-target="#compareModal">
      {{ $t('activityCompare.compareButton') }}
    </button>
  </div>

  <!-- Modal -->
  <div class="modal fade" id="compareModal" tabindex="-1" aria-hidden="true">
    <div class="modal-dialog modal-dialog-centered modal-lg">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title">
            {{ $t('activityCompare.selectTitle') }}
          </h5>
          <button
            type="button"
            class="btn-close"
            data-bs-dismiss="modal"
            aria-label="Close"
          ></button>
        </div>

        <div class="modal-body">
          <div class="p-3 mb-3 bg-body-tertiary border-0 rounded">
            <div class="row align-items-end">
              <!-- Activity Type -->
              <div class="col-md-3">
                <label for="activityTypeFilter" class="form-label">{{
                  $t('activitiesView.filterLabelType')
                }}</label>
                <select
                  id="activityTypeFilter"
                  class="form-select"
                  v-model="selectedType"
                  @change="applyFilters"
                  disabled="true"
                >
                  <option value="">{{ $t('activitiesView.filterOptionAllTypes') }}</option>
                  <option v-for="(value, key) in activityTypes" :key="key" :value="key">
                    {{ value }}
                  </option>
                </select>
              </div>
              <!-- Start Date -->
              <div class="col-md-3">
                <label for="startDateFilter" class="form-label">{{
                  $t('activitiesView.filterLabelFromDate')
                }}</label>
                <input type="date" id="startDateFilter" class="form-control" v-model="startDate" />
              </div>
              <!-- End Date -->
              <div class="col-md-3">
                <label for="endDateFilter" class="form-label">{{
                  $t('activitiesView.filterLabelToDate')
                }}</label>
                <input type="date" id="endDateFilter" class="form-control" v-model="endDate" />
              </div>
              <!-- Name Search -->
              <div class="col-md-3">
                <label for="nameSearchFilter" class="form-label">{{
                  $t('activitiesView.filterLabelNameLocation')
                }}</label>
                <input
                  type="text"
                  id="nameSearchFilter"
                  class="form-control"
                  v-model="nameSearch"
                  :placeholder="$t('activitiesView.filterPlaceholderNameLocation')"
                />
              </div>
              <!-- Buttons -->
              <div class="col-12 mt-3 d-flex justify-content-end gap-3">
                <button type="button" class="btn btn-secondary" @click="clearFilters">
                  {{ $t('activitiesView.buttonClear') }}
                </button>
                <button type="submit" class="btn btn-primary" disabled v-if="isLoading">
                  <span class="spinner-border spinner-border-sm me-1" aria-hidden="true"></span>
                  <span role="status">{{ $t('activitiesView.buttonApply') }}</span>
                </button>
                <button type="submit" class="btn btn-primary" v-else>
                  {{ $t('activitiesView.buttonApply') }}
                </button>
              </div>
            </div>
          </div>
          <!-- End Filter Section -->

          <LoadingComponent v-if="isLoading" />
          <div
            class="p-3 bg-body-tertiary rounded shadow-sm"
            v-else-if="activities && activities.length"
          >
            <!-- Activities Table -->
            <ActivitiesTableComponent
              :activities="activities"
              :sort-by="sortBy"
              :sort-order="sortOrder"
              :selected-activity-id="selectedActivityId"
              :current-activity-id="props.activity.id"
              :compare-mode="true"
              @rowSelected="selectActivity"
              @sortChanged="handleSort"
              v-if="activities && activities.length"
            />

            <PaginationComponent
              :totalPages="totalPages"
              :pageNumber="pageNumber"
              @pageNumberChanged="setPageNumber"
              v-if="activities && activities.length"
            />
          </div>

          <NoItemsFoundComponents v-else />
        </div>

        <div class="modal-footer">
          <button class="btn btn-secondary" data-bs-dismiss="modal">
            {{ $t('generalItems.cancel') }}
          </button>

          <button class="btn btn-primary" :disabled="!selectedActivityId" @click="confirmCompare">
            {{ $t('activityCompare.compareButton') }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import ActivitiesTableComponent from '@/components/Activities/ActivitiesTableComponent.vue'
import PaginationComponent from '@/components/GeneralComponents/PaginationComponent.vue'
import LoadingComponent from '@/components/GeneralComponents/LoadingComponent.vue'
import NoItemsFoundComponents from '@/components/GeneralComponents/NoItemsFoundComponents.vue'
import { useActivities } from '@/composables/useActivities'
import { ref, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'

const props = defineProps({
  activity: {
    type: Object,
    required: true
  }
})

const {
  activities,
  activityTypes,
  selectedType,
  startDate,
  endDate,
  totalPages,
  isLoading,
  sortBy,
  sortOrder,
  nameSearch,
  performNameSearch,
  pageNumber,
  fetchActivityTypes,
  updateActivities,
  applyFilters,
  handleSort,
  clearFilters,
  setPageNumber
} = useActivities()

const router = useRouter()
const selectedActivityId = ref(null)

function selectActivity(id) {
  selectedActivityId.value = id
}

function confirmCompare() {
  router.push(`/activity-compare/${props.activity.id}/${selectedActivityId.value}`)
}

onMounted(async () => {
  await fetchActivityTypes()
  await updateActivities(props.activity.activity_type)
})

watch(nameSearch, performNameSearch, { immediate: false })
watch(pageNumber, updateActivities, { immediate: false })
</script>
