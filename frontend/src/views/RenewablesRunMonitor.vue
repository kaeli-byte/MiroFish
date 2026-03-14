<template>
  <div class="page">
    <h1>Renewable Fuels · Run Monitor</h1>
    <p><strong>Simulation:</strong> {{ props.simulationId }}</p>
    <div class="actions">
      <button :disabled="loading" @click="run">Run Simulation</button>
      <button :disabled="loading" @click="refresh">Refresh Status</button>
      <button :disabled="!props.simulationId" @click="goDashboard">Open Results Dashboard</button>
    </div>
    <p v-if="loading">Loading...</p>
    <p v-if="error" class="error">{{ error }}</p>
    <pre v-if="statusJson">{{ statusJson }}</pre>
  </div>
</template>

<script setup>
import { onMounted, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { getEngineSimulationStatus, runEngineSimulation } from '../api/simulation'

const props = defineProps({
  simulationId: {
    type: [String, Number],
    required: true
  }
})

const router = useRouter()
const statusJson = ref('')
const loading = ref(false)
const error = ref('')
const requestGen = ref(0)

const loadStatus = async () => {
  requestGen.value += 1
  const currentRequestGen = requestGen.value
  loading.value = true
  try {
    const res = await getEngineSimulationStatus(props.simulationId)
    if (currentRequestGen !== requestGen.value) {
      return
    }
    statusJson.value = JSON.stringify(res.data, null, 2)
    error.value = ''
  } catch (err) {
    if (currentRequestGen !== requestGen.value) {
      return
    }
    error.value = err?.message || 'Failed to load simulation status.'
  } finally {
    if (currentRequestGen === requestGen.value) {
      loading.value = false
    }
  }
}

const run = async () => {
  requestGen.value += 1
  const currentRequestGen = requestGen.value
  loading.value = true
  try {
    const res = await runEngineSimulation(props.simulationId)
    if (currentRequestGen !== requestGen.value) {
      return
    }
    statusJson.value = JSON.stringify(res.data, null, 2)
    error.value = ''
  } catch (err) {
    if (currentRequestGen !== requestGen.value) {
      return
    }
    error.value = err?.message || 'Failed to run simulation.'
  } finally {
    if (currentRequestGen === requestGen.value) {
      loading.value = false
    }
  }
}

const refresh = () => loadStatus()

const goDashboard = () => router.push(`/renewables/${props.simulationId}/dashboard`)

onMounted(loadStatus)
watch(() => props.simulationId, loadStatus)
</script>

<style scoped>
.page { max-width: 900px; margin: 24px auto; padding: 16px; }
.actions { display:flex; gap:10px; margin: 12px 0; }
button { border:1px solid #111; background:#fff; padding:8px 12px; cursor:pointer; }
.error { color: #b91c1c; }
pre { background:#fafafa; border:1px solid #eee; padding:10px; }
</style>
