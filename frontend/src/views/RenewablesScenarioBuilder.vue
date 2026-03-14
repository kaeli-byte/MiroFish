<template>
  <div class="page">
    <h1>Renewable Fuels · Scenario Builder</h1>
    <p class="desc">Configure Mesa renewable-fuels scenarios and ingest report assumptions via backend APIs.</p>

    <div class="grid">
      <label>Project ID <input v-model="form.project_id" /></label>
      <label>Steps <input v-model.number="form.steps" type="number" min="1" /></label>
      <label>Producers <input v-model.number="form.producers" type="number" min="1" /></label>
      <label>Suppliers <input v-model.number="form.suppliers" type="number" min="1" /></label>
      <label>Buyers <input v-model.number="form.buyers" type="number" min="1" /></label>
      <label>Investors <input v-model.number="form.investors" type="number" min="1" /></label>
      <label>Initial Price <input v-model.number="form.initial_price" type="number" step="0.01" /></label>
      <label>Initial Capital <input v-model.number="form.initial_capital" type="number" step="0.1" /></label>
    </div>

    <label>Report Text (optional for assumption extraction)</label>
    <textarea v-model="reportText" rows="8" />

    <div class="actions">
      <button @click="create">1) Create</button>
      <button :disabled="!simulationId" @click="prepare">2) Prepare</button>
      <button :disabled="!simulationId" @click="goMonitor">Go to Run Monitor</button>
    </div>

    <p v-if="simulationId"><strong>Simulation ID:</strong> {{ simulationId }}</p>
    <pre v-if="responseJson">{{ responseJson }}</pre>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { createEngineSimulation, prepareEngineSimulation } from '../api/simulation'

const router = useRouter()
const simulationId = ref('')
const reportText = ref('')
const responseJson = ref('')

const form = ref({
  project_id: '',
  steps: 24,
  producers: 5,
  suppliers: 3,
  buyers: 8,
  investors: 4,
  initial_price: 1.8,
  initial_capital: 250
})

const create = async () => {
  const res = await createEngineSimulation({ project_id: form.value.project_id, engine: 'mesa_renewable_fuels' })
  simulationId.value = res.data.data.simulation_id
  responseJson.value = JSON.stringify(res.data, null, 2)
}

const prepare = async () => {
  const payload = {
    scenario: {
      steps: form.value.steps,
      producers: form.value.producers,
      suppliers: form.value.suppliers,
      buyers: form.value.buyers,
      investors: form.value.investors,
      initial_price: form.value.initial_price,
      initial_capital: form.value.initial_capital
    },
    report_text: reportText.value
  }
  const res = await prepareEngineSimulation(simulationId.value, payload)
  responseJson.value = JSON.stringify(res.data, null, 2)
}

const goMonitor = () => {
  router.push(`/renewables/${simulationId.value}/monitor`)
}
</script>

<style scoped>
.page { max-width: 980px; margin: 24px auto; padding: 16px; }
.desc { margin-bottom: 12px; color: #555; }
.grid { display: grid; gap: 10px; grid-template-columns: repeat(2, minmax(0,1fr)); margin-bottom: 12px; }
label { display:flex; flex-direction:column; gap:6px; font-size:14px; }
input, textarea { border:1px solid #ddd; padding:8px; }
.actions { display:flex; gap:10px; margin: 12px 0; }
button { border:1px solid #111; background:#fff; padding:8px 12px; cursor:pointer; }
pre { background:#fafafa; border:1px solid #eee; padding:10px; overflow:auto; }
</style>
