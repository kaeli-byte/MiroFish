<template>
  <div class="page">
    <h1>Renewable Fuels · Run Monitor</h1>
    <p><strong>Simulation:</strong> {{ simulationId }}</p>
    <div class="actions">
      <button @click="run">Run Simulation</button>
      <button @click="refresh">Refresh Status</button>
      <button @click="goDashboard">Open Results Dashboard</button>
    </div>
    <pre v-if="statusJson">{{ statusJson }}</pre>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getEngineSimulationStatus, runEngineSimulation } from '../api/simulation'

const route = useRoute()
const router = useRouter()
const simulationId = route.params.simulationId
const statusJson = ref('')

const refresh = async () => {
  const res = await getEngineSimulationStatus(simulationId)
  statusJson.value = JSON.stringify(res.data, null, 2)
}

const run = async () => {
  const res = await runEngineSimulation(simulationId)
  statusJson.value = JSON.stringify(res.data, null, 2)
}

const goDashboard = () => router.push(`/renewables/${simulationId}/dashboard`)

onMounted(refresh)
</script>

<style scoped>
.page { max-width: 900px; margin: 24px auto; padding: 16px; }
.actions { display:flex; gap:10px; margin: 12px 0; }
button { border:1px solid #111; background:#fff; padding:8px 12px; cursor:pointer; }
pre { background:#fafafa; border:1px solid #eee; padding:10px; }
</style>
