<template>
  <div>
    <div class="section">
      <h2>新建岗位</h2>
      <div class="form-row">
        <input v-model="form.title" placeholder="岗位名称" class="w-40" />
        <input v-model="form.preferences" placeholder="HR偏好（可选）" class="w-30" />
        <button @click="createJob">添加岗位</button>
      </div>
      <textarea v-model="form.requirements" placeholder="岗位要求（自然语言即可）" />
      <p v-if="msg" class="msg">{{ msg }}</p>
    </div>
    <div class="section">
      <div class="section-header"><h2>岗位列表</h2><button @click="fetchJobs" class="secondary" style="font-size:0.75rem;">刷新</button></div>
      <div v-for="job in jobs" :key="job.id" class="job-row">
        <div><router-link :to="'/job/'+job.id" class="job-title">{{ job.title }}</router-link><span class="job-date">{{ job.created_at?.slice(0,10) }}</span></div>
        <button @click="deleteJob(job.id)" class="secondary" style="font-size:0.7rem;padding:0.15rem 0.5rem;">删除</button>
      </div>
      <p v-if="jobs.length===0" class="empty">暂无岗位</p>
    </div>
  </div>
</template>

<script setup>
import { ref, inject, onMounted } from 'vue'
import axios from 'axios'
const { showLoading, hideLoading } = inject('loading')
const jobs = ref([])
const form = ref({ title:'', requirements:'', preferences:'' })
const msg = ref('')
const fetchJobs = async () => { const res = await axios.get('/api/jobs'); jobs.value = res.data }
const createJob = async () => {
  showLoading()
  try { const res = await axios.post('/api/jobs', form.value); msg.value='创建成功'; form.value={title:'',requirements:'',preferences:''}; fetchJobs() }
  catch(e) { msg.value='失败：'+(e.response?.data?.detail||e.message) }
  finally { hideLoading() }
}
const deleteJob = async (id) => { await axios.delete('/api/jobs/'+id); fetchJobs() }
onMounted(fetchJobs)
</script>

<style scoped>
.section { background:#fff; border-radius:var(--radius); padding:1.5rem 1.75rem; margin-bottom:1rem; }
.section h2 { font-size:1rem; font-weight:600; color:var(--slate-900); margin-bottom:1rem; }
.form-row { display:flex; gap:0.75rem; align-items:flex-start; }
.w-40 { flex:2; } .w-30 { flex:1; }
.msg { font-size:0.8rem; color:var(--slate-500); margin-top:0.5rem; }
.section-header { display:flex; align-items:center; justify-content:space-between; margin-bottom:0.75rem; }
.section-header h2 { margin-bottom:0; }
.job-row { display:flex; align-items:center; justify-content:space-between; padding:0.6rem 0; border-bottom:1px solid var(--slate-100); }
.job-row:last-child { border-bottom:none; }
.job-title { font-weight:500; color:var(--slate-700); font-size:0.9rem; }
.job-date { font-size:0.75rem; color:var(--slate-400); margin-left:1rem; }
.empty { color:var(--slate-400); text-align:center; padding:1.5rem 0; font-size:0.85rem; }
</style>
