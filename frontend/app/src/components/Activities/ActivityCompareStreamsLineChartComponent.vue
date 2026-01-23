<template>
  <div style="position: relative; width: 100%; height: 100%">
    <canvas ref="chartCanvas"></canvas>
  </div>
</template>

<script>
import { ref, onMounted, onUnmounted, computed, watch } from 'vue'
import { useI18n } from 'vue-i18n'
// Importing the stores
import { useAuthStore } from '@/stores/authStore'
import { useServerSettingsStore } from '@/stores/serverSettingsStore'
import { Chart, registerables } from 'chart.js'
import zoomPlugin from 'chartjs-plugin-zoom'
Chart.register(...registerables, zoomPlugin)

import {
  formatAverageSpeedMetric,
  formatAverageSpeedImperial,
  activityTypeIsSwimming,
  activityTypeIsRunning,
  activityTypeIsRowing,
  activityTypeIsWalking
} from '@/utils/activityUtils'
import { metersToFeet, kmToMiles } from '@/utils/unitsUtils'

export default {
  props: {
    activity: {
      type: Object,
      required: true
    },
    comparedActivity: {
      type: Object,
      default: null
    },
    graphSelection: {
      type: String,
      required: true
    },
    activityStreams: {
      type: Array,
      required: true
    },
    comparedActivityStreams: {
      type: Array,
      default: () => []
    }
  },
  setup(props) {
    const { t } = useI18n()
    const authStore = useAuthStore()
    const serverSettingsStore = useServerSettingsStore()
    const chartCanvas = ref(null)
    const units = ref(1)
    let myChart = null

    // Function to create gradient fill for chart
    function createGradient(ctx, chartArea, graphSelection, isCompared = false) {
      if (!chartArea) {
        const colors = getGraphColors(graphSelection, isCompared)
        return colors.gradientStart
      }

      const colors = getGraphColors(graphSelection, isCompared)
      const gradient = ctx.createLinearGradient(0, chartArea.top, 0, chartArea.bottom)
      gradient.addColorStop(0, colors.gradientStart)
      gradient.addColorStop(1, colors.gradientEnd)
      return gradient
    }

    // Function to format pace values as MM:SS
    function formatPaceForTooltip(value) {
      if (value === null || value === undefined) return 'N/A'
      const totalMinutes = Math.floor(value)
      let seconds = Math.round((value - totalMinutes) * 60)

      let minutes = totalMinutes
      if (seconds >= 60) {
        minutes += 1
        seconds = 0
      }

      return `${minutes}:${seconds.toString().padStart(2, '0')}`
    }

    // Function to get colors based on graph type and whether it's a comparison
    function getGraphColors(graphSelection, isCompared = false) {
      const colors = {
        hr: {
          border: isCompared ? 'rgba(147, 51, 234, 0.8)' : 'rgba(239, 68, 68, 0.8)',
          gradientStart: isCompared ? 'rgba(147, 51, 234, 0.4)' : 'rgba(239, 68, 68, 0.4)',
          gradientEnd: isCompared ? 'rgba(147, 51, 234, 0.0)' : 'rgba(239, 68, 68, 0.0)'
        },
        power: {
          border: isCompared ? 'rgba(234, 88, 12, 0.8)' : 'rgba(251, 191, 36, 0.8)',
          gradientStart: isCompared ? 'rgba(234, 88, 12, 0.4)' : 'rgba(251, 191, 36, 0.4)',
          gradientEnd: isCompared ? 'rgba(234, 88, 12, 0.0)' : 'rgba(251, 191, 36, 0.0)'
        },
        cad: {
          border: isCompared ? 'rgba(236, 72, 153, 0.8)' : 'rgba(168, 85, 247, 0.8)',
          gradientStart: isCompared ? 'rgba(236, 72, 153, 0.4)' : 'rgba(168, 85, 247, 0.4)',
          gradientEnd: isCompared ? 'rgba(236, 72, 153, 0.0)' : 'rgba(168, 85, 247, 0.0)'
        },
        ele: {
          border: isCompared ? 'rgba(20, 184, 166, 0.8)' : 'rgba(34, 197, 94, 0.8)',
          gradientStart: isCompared ? 'rgba(20, 184, 166, 0.4)' : 'rgba(34, 197, 94, 0.4)',
          gradientEnd: isCompared ? 'rgba(20, 184, 166, 0.0)' : 'rgba(34, 197, 94, 0.0)'
        },
        vel: {
          border: isCompared ? 'rgba(6, 182, 212, 0.8)' : 'rgba(59, 130, 246, 0.8)',
          gradientStart: isCompared ? 'rgba(6, 182, 212, 0.4)' : 'rgba(59, 130, 246, 0.4)',
          gradientEnd: isCompared ? 'rgba(6, 182, 212, 0.0)' : 'rgba(59, 130, 246, 0.0)'
        },
        pace: {
          border: isCompared ? 'rgba(244, 63, 94, 0.8)' : 'rgba(236, 72, 153, 0.8)',
          gradientStart: isCompared ? 'rgba(244, 63, 94, 0.4)' : 'rgba(236, 72, 153, 0.4)',
          gradientEnd: isCompared ? 'rgba(244, 63, 94, 0.0)' : 'rgba(236, 72, 153, 0.0)'
        }
      }
      return colors[graphSelection] || colors.vel
    }

    // Helper function to process activity data
    function processActivityData(activity, activityStreams, isCompared = false) {
      const data = []
      let label = ''
      const cadData = []
      let cadLabel = ''

      for (const stream of activityStreams) {
        if (stream.stream_type === 3) {
          for (const streamPoint of stream.stream_waypoints) {
            cadData.push(Number.parseInt(streamPoint.cad))
          }
          if (cadData.length > 0) {
            cadLabel = activityTypeIsSwimming(activity)
              ? t('generalItems.labelStrokeRateInSpm')
              : t('generalItems.labelCadenceInRpm')
          }
        }
        if (stream.stream_type === 1 && props.graphSelection === 'hr') {
          for (const streamPoint of stream.stream_waypoints) {
            data.push(Number.parseInt(streamPoint.hr))
            label = t('generalItems.labelHRinBpm')
          }
        } else if (stream.stream_type === 2 && props.graphSelection === 'power') {
          for (const streamPoint of stream.stream_waypoints) {
            data.push(Number.parseInt(streamPoint.power))
            label = t('generalItems.labelPowerInWatts')
          }
        } else if (stream.stream_type === 3 && props.graphSelection === 'cad') {
          for (const streamPoint of stream.stream_waypoints) {
            let cadence = Number.parseInt(streamPoint.cad)
            if (activityTypeIsRunning(activity)) {
              cadence = cadence * 2
            }
            data.push(cadence)
            label = activityTypeIsSwimming(activity)
              ? t('generalItems.labelStrokeRateInSpm')
              : t('generalItems.labelCadenceInRpm')
          }
        } else if (stream.stream_type === 4 && props.graphSelection === 'ele') {
          for (const streamPoint of stream.stream_waypoints) {
            if (Number(units.value) === 1) {
              data.push(Number.parseFloat(streamPoint.ele))
              label = t('generalItems.labelElevationInMeters')
            } else {
              data.push(Number.parseFloat(metersToFeet(streamPoint.ele)))
              label = t('generalItems.labelElevationInFeet')
            }
          }
        } else if (stream.stream_type === 5 && props.graphSelection === 'vel') {
          if (Number(units.value) === 1) {
            data.push(
              ...stream.stream_waypoints.map((velData) =>
                Number.parseFloat(formatAverageSpeedMetric(velData.vel))
              )
            )
            label = t('generalItems.labelVelocityInKmH')
          } else {
            data.push(
              ...stream.stream_waypoints.map((velData) =>
                Number.parseFloat(formatAverageSpeedImperial(velData.vel))
              )
            )
            label = t('generalItems.labelVelocityInMph')
          }
        } else if (stream.stream_type === 6 && props.graphSelection === 'pace') {
          for (const paceData of stream.stream_waypoints) {
            if (paceData.pace === 0 || paceData.pace === null) {
              data.push(null)
            } else {
              let converted = null
              if (
                activityTypeIsRunning(activity) ||
                activityTypeIsWalking(activity) ||
                activityTypeIsRowing(activity)
              ) {
                if (Number(units.value) === 1) {
                  converted = (paceData.pace * 1000) / 60
                } else {
                  converted = (paceData.pace * 1609.34) / 60
                }
                const threshold = Number(units.value) === 1 ? 20 : 20 * 1.60934
                if (converted > threshold || Number.isNaN(converted)) {
                  data.push(null)
                } else {
                  data.push(converted)
                }
              } else if (activityTypeIsSwimming(activity)) {
                if (Number(units.value) === 1) {
                  converted = (paceData.pace * 100) / 60
                } else {
                  converted = (paceData.pace * 100 * 0.9144) / 60
                }
                const swimThreshold = Number(units.value) === 1 ? 10 : 10 * 1.0936
                if (converted > swimThreshold || Number.isNaN(converted)) {
                  data.push(null)
                } else {
                  data.push(converted)
                }
              }
            }
          }
          if (
            activityTypeIsRunning(activity) ||
            activityTypeIsWalking(activity) ||
            activityTypeIsRowing(activity)
          ) {
            if (Number(units.value) === 1) {
              label = t('generalItems.labelPaceInMinKm')
            } else {
              label = t('generalItems.labelPaceInMinMile')
            }
          } else if (activityTypeIsSwimming(activity)) {
            if (Number(units.value) === 1) {
              label = t('generalItems.labelPaceInMin100m')
            } else {
              label = t('generalItems.labelPaceInMin100yd')
            }
          }
        }
      }

      return { data, label, cadData, cadLabel }
    }

    // Function to pad arrays to the same length
    function padToLength(arr, len) {
      return arr.length < len ? arr.concat(Array(len - arr.length).fill(null)) : arr
    }

    const computedChartData = computed(() => {
      if (authStore.isAuthenticated) {
        units.value = authStore.user.units
      } else {
        units.value = serverSettingsStore.serverSettings.units
      }

      const primaryResult = processActivityData(props.activity, props.activityStreams, false)

      const totalDistance =
        Math.max(props.activity?.distance, props.comparedActivity?.distance) / 1000
      const numberOfDataPoints = Math.max(
        props.activityStreams[0]['stream_waypoints'].length || 0,
        props.comparedActivityStreams[0]['stream_waypoints'].length || 0
      )
      const distanceInterval = totalDistance / numberOfDataPoints
      const labels = []

      for (let i = 0; i < numberOfDataPoints; i++) {
        if (Number(units.value) === 1) {
          if (activityTypeIsSwimming(props.activity)) {
            labels.push(`${(i * distanceInterval).toFixed(1)}km`)
          } else {
            labels.push(`${(i * distanceInterval).toFixed(0)}km`)
          }
        } else {
          if (activityTypeIsSwimming(props.activity)) {
            labels.push(`${(i * kmToMiles(distanceInterval)).toFixed(1)}mi`)
          } else {
            labels.push(`${(i * kmToMiles(distanceInterval)).toFixed(0)}mi`)
          }
        }
      }

      const datasets = []

      datasets.push({
        label: primaryResult.label,
        data: primaryResult.data,
        yAxisID: 'y',
        backgroundColor: function (context) {
          const chart = context.chart
          const { ctx, chartArea } = chart
          if (!chartArea) {
            const colors = getGraphColors(props.graphSelection, false)
            return colors.gradientStart
          }
          return createGradient(ctx, chartArea, props.graphSelection, false)
        },
        borderColor: getGraphColors(props.graphSelection, false).border,
        fill: props.graphSelection === 'pace' ? 'start' : true,
        pointHoverRadius: 4,
        pointHoverBackgroundColor: getGraphColors(props.graphSelection, false).border
      })

      if (props.comparedActivity && props.comparedActivityStreams.length > 0) {
        const comparedResult = processActivityData(
          props.comparedActivity,
          props.comparedActivityStreams,
          true
        )

        datasets.push({
          label: `${comparedResult.label} (Compared)`,
          data: comparedResult.data,
          yAxisID: 'y',
          backgroundColor: function (context) {
            const chart = context.chart
            const { ctx, chartArea } = chart
            if (!chartArea) {
              const colors = getGraphColors(props.graphSelection, true)
              return colors.gradientStart
            }
            return createGradient(ctx, chartArea, props.graphSelection, true)
          },
          borderColor: getGraphColors(props.graphSelection, true).border,
          fill: props.graphSelection === 'pace' ? 'start' : true,
          pointHoverRadius: 4,
          pointHoverBackgroundColor: getGraphColors(props.graphSelection, true).border
        })
      }

      const validData = primaryResult.data.filter((v) => v !== null && !Number.isNaN(v))
      let avgValue = null
      let extremeValue = null
      let extremeLabel = ''

      if (validData.length > 0) {
        avgValue = validData.reduce((a, b) => a + b, 0) / validData.length

        if (props.graphSelection === 'pace') {
          extremeValue = Math.min(...validData)
          extremeLabel = 'Best'
        } else {
          extremeValue = Math.max(...validData)
          extremeLabel = 'Maximum'
        }
      }

      if (avgValue !== null) {
        datasets.push({
          label: t('generalItems.labelAverage'),
          data: Array(primaryResult.data.length).fill(avgValue),
          yAxisID: 'y',
          borderColor: 'rgba(156, 163, 175, 0.6)',
          borderWidth: 2,
          borderDash: [10, 5],
          fill: false,
          pointRadius: 0,
          pointHoverRadius: 0,
          tension: 0
        })
      }

      if (extremeValue !== null) {
        datasets.push({
          label: extremeLabel,
          data: Array(primaryResult.data.length).fill(extremeValue),
          yAxisID: 'y',
          borderColor: 'rgba(220, 38, 38, 0.5)',
          borderWidth: 1.5,
          borderDash: [5, 5],
          fill: false,
          pointRadius: 0,
          pointHoverRadius: 0,
          tension: 0
        })
      }

      if (primaryResult.cadData.length > 0 && props.activity.activity_type === 8) {
        datasets.push({
          type: 'bar',
          label: t('generalItems.labelLaps'),
          data: primaryResult.cadData.map((d) => (d === 0 ? 0 : 1)),
          yAxisID: 'y1',
          backgroundColor: 'rgba(0, 0, 0, 0.2)',
          fill: true,
          fillColor: 'rgba(0, 0, 0, 0.2)',
          borderWidth: 0,
          barThickness: 5
        })
      }

      return {
        datasets: datasets,
        labels: labels
      }
    })

    watch(
      computedChartData,
      (newChartData) => {
        if (myChart) {
          myChart.data.datasets = newChartData.datasets
          myChart.data.labels = newChartData.labels
          if (myChart.options && myChart.options.scales && myChart.options.scales.y) {
            myChart.options.scales.y.reverse = props.graphSelection === 'pace'
          }
          myChart.update()
        }
      },
      { deep: true }
    )

    const crosshairPlugin = {
      id: 'customCrosshair',
      afterDraw: (chart) => {
        if (chart.tooltip?._active && chart.tooltip._active.length) {
          const ctx = chart.ctx
          const activePoint = chart.tooltip._active[0]
          const x = activePoint.element.x
          const topY = chart.scales.y.top
          const bottomY = chart.scales.y.bottom

          ctx.save()
          ctx.beginPath()
          ctx.setLineDash([5, 5])
          ctx.moveTo(x, topY)
          ctx.lineTo(x, bottomY)
          ctx.lineWidth = 1
          ctx.strokeStyle = 'rgba(0, 0, 0, 0.3)'
          ctx.stroke()
          ctx.restore()
        }
      }
    }

    onMounted(() => {
      myChart = new Chart(chartCanvas.value.getContext('2d'), {
        type: 'line',
        data: computedChartData.value,
        plugins: [crosshairPlugin],
        options: {
          responsive: true,
          maintainAspectRatio: false,
          animation: false,
          interaction: {
            mode: 'index',
            intersect: false
          },
          elements: {
            point: {
              radius: 0,
              hitRadius: 10,
              hoverRadius: 4
            },
            line: {
              tension: 0.4
            }
          },
          scales: {
            y: {
              beginAtZero: false,
              position: 'left',
              reverse: props.graphSelection === 'pace',
              grid: {
                lineWidth: 1,
                drawBorder: true,
                borderWidth: 1
              }
            },
            y1: {
              beginAtZero: true,
              max: 1,
              display: false
            },
            x: {
              ticks: {
                maxTicksLimit: 10,
                autoSkip: true
              },
              grid: {
                lineWidth: 1,
                drawBorder: true,
                borderWidth: 1
              }
            }
          },
          plugins: {
            legend: {
              display: true,
              position: 'top'
            },
            tooltip: {
              enabled: true,
              callbacks: {
                title: function (context) {
                  return context[0].label
                },
                label: function (context) {
                  const label = context.dataset.label || ''
                  let value = context.parsed.y

                  if (value === null || value === undefined) {
                    return `${label}: N/A`
                  }

                  if (props.graphSelection === 'pace') {
                    const formatted = formatPaceForTooltip(value)
                    return `${label}: ${formatted}`
                  } else if (props.graphSelection === 'hr') {
                    return `${label}: ${Math.round(value)}`
                  } else if (props.graphSelection === 'power') {
                    return `${label}: ${Math.round(value)} W`
                  } else if (props.graphSelection === 'cad') {
                    return `${label}: ${Math.round(value)}`
                  } else if (props.graphSelection === 'ele') {
                    return `${label}: ${value.toFixed(1)}`
                  } else if (props.graphSelection === 'vel') {
                    return `${label}: ${value.toFixed(1)}`
                  }

                  return `${label}: ${value}`
                }
              }
            },
            zoom: {
              pan: {
                enabled: true,
                mode: 'x',
                modifierKey: 'shift'
              },
              zoom: {
                wheel: {
                  enabled: true,
                  speed: 0.1
                },
                pinch: {
                  enabled: true
                },
                mode: 'x'
              },
              limits: {
                x: {
                  min: 'original',
                  max: 'original'
                }
              }
            }
          }
        }
      })
    })

    onUnmounted(() => {
      if (myChart) {
        myChart.destroy()
      }
    })

    return {
      chartCanvas,
      activityTypeIsSwimming
    }
  }
}
</script>
