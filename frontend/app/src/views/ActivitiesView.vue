<template>
  <h1>{{ $t('activitiesView.title') }}</h1>
  <!-- Filter Section -->
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
        >
          <option value="">{{ $t('activitiesView.filterOptionAllTypes') }}</option>
          <option v-for="(value, key) in activityTypes" :key="key" :value="key">{{ value }}</option>
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
  <div class="p-3 bg-body-tertiary rounded shadow-sm" v-else-if="activities && activities.length">
    <!-- Activities Table -->
    <ActivitiesTableComponent
      :activities="activities"
      :sort-by="sortBy"
      :sort-order="sortOrder"
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
</template>

<script setup>
// Switch to <script setup> composition API
import { onMounted, watch } from 'vue'
import ActivitiesTableComponent from '@/components/Activities/ActivitiesTableComponent.vue'
import PaginationComponent from '@/components/GeneralComponents/PaginationComponent.vue'
import LoadingComponent from '@/components/GeneralComponents/LoadingComponent.vue'
import NoItemsFoundComponents from '@/components/GeneralComponents/NoItemsFoundComponents.vue'
import { useActivities } from '@/composables/useActivities.js'

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

onMounted(async () => {
  await fetchActivityTypes()
  await updateActivities()
})

watch(nameSearch, performNameSearch, { immediate: false })
watch(pageNumber, updateActivities, { immediate: false })
</script>
