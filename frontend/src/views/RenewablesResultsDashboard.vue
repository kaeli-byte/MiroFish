<template>
  <div class="page">
    <h1>Renewable Fuels · Results Dashboard</h1>
    <p><strong>Simulation:</strong> {{ simulationId }}</p>
    <button @click="load">Load Results JSON</button>

    <div v-if="results.summary" class="cards">
      <div class="card">Final Price: {{ results.summary.final_price }}</div>
      <div class="card">Final Supply: {{ results.summary.final_supply }}</div>
      <div class="card">Final Inventory: {{ results.summary.final_inventory }}</div>
      <div class="card">Final Demand: {{ results.summary.final_demand }}</div>
      <div class="card">Final Capital Pool: {{ results.summary.final_capital_pool }}</div>
    </div>

    <h3>Time Series (JSON for custom charts)</h3>
    <pre v-if="resultsJson">{{ resultsJson }}</pre>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'
import { useRoute } from 'vue-router'
import { getEngineSimulationResults } from '../api/simulation'

const route = useRoute()
const simulationId = computed(() => route.params.simulationId)
const results = ref({})
const resultsJson = ref('')

const load = async () => {
  try {
    const res = await getEngineSimulationResults(simulationId.value)
    if (res?.data?.data) {
      results.value = res.data.data
      resultsJson.value = JSON.stringify(results.value, null, 2)
      return
    }

    results.value = {}
    resultsJson.value = 'Unable to load simulation results.'
  } catch (error) {
    results.value = {}
    resultsJson.value = `Failed to load results: ${error?.message || 'Unknown error'}`
  }
}
</script>

<style scoped>
.page { max-width: 980px; margin: 24px auto; padding: 16px; }
button { border:1px solid #111; background:#fff; padding:8px 12px; cursor:pointer; margin: 8px 0 12px; }
.cards { display:grid; grid-template-columns: repeat(3, minmax(0,1fr)); gap:10px; margin-bottom: 12px; }
.card { border:1px solid #ddd; padding:10px; background:#fff; }
pre { background:#fafafa; border:1px solid #eee; padding:10px; overflow:auto; }
</style>
