<template>
  <div class="col">
    <span class="fw-lighter">
      {{ label }}
    </span>

    <div v-if="compare" class="d-flex align-items-stretch mt-1">
      <span class="flex-fill text-center">{{ value }}</span>

      <div class="px-2 d-flex align-items-stretch">
        <div class="border-start border-opacity-50"></div>
      </div>

      <span class="flex-fill text-center">{{ comparedValue }}</span>
    </div>

    <div v-else class="mt-1">
      {{ value }}
    </div>
  </div>
</template>

<script setup>
defineProps({
  label: String,
  value: String,
  comparedValue: String,
  compare: Boolean
})
</script>
