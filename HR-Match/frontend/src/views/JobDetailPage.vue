<template>
  <div>
    <div class="section">
      <router-link to="/" class="back">← 岗位列表</router-link>
      <h2>{{ job?.title || '加载中...' }}</h2>
      <div class="controls">
        <div class="ctrl">
          <p class="ctrl-label">权重设置</p>
          <div class="slider-row"><span>技能</span><input type="range" min="0" max="100" v-model.number="weights.skills" /><span class="val">{{ weights.skills }}%</span></div>
          <div class="slider-row"><span>学历</span><input type="range" min="0" max="100" v-model.number="weights.education" /><span class="val">{{ weights.education }}%</span></div>
          <div class="slider-row"><span>经验</span><input type="range" min="0" max="100" v-model.number="weights.experience" /><span class="val">{{ weights.experience }}%</span></div>
          <button @click="updateWeights" class="secondary" style="margin-top:0.5rem;">保存</button>
        </div>
        <div class="ctrl">
          <p class="ctrl-label">HR偏好</p>
          <input v-model="preferences" placeholder="如：希望有开源经验" />
          <button @click="updatePreferences" class="secondary" style="margin-top:0.25rem;">保存</button>
        </div>
        <div class="ctrl">
          <p class="ctrl-label">上传简历</p>
          <input type="file" @change="handleFile" accept=".pdf,.docx" />
          <button @click="upload" style="margin-top:0.25rem;">上传并分析</button>
          <p v-if="uploadMsg" class="msg">{{ uploadMsg }}</p>
        </div>
      </div>
    </div>

    <div class="section">
      <div class="section-header"><h2>候选人排名</h2><div><button @click="fetchRanking">刷新</button><button @click="clearResumes" class="secondary" style="margin-left:0.5rem;">清空</button></div></div>
      <p v-if="ranking.length===0" class="empty">暂无候选人数据，请上传简历</p>
      <div v-for="(r,i) in ranking" :key="r.resume_id" class="rank-card">
        <div class="rank-top">
          <span class="rank-num">#{{ i+1 }}</span><span class="rank-name">{{ r.parsed?.candidate_name||'未知' }}</span>
          <span class="rank-file">{{ r.filename }}</span><span class="rank-score">{{ r.parsed?.overall_score||0 }}%</span>
        </div>
        <p class="rank-strength">{{ (r.parsed?.strengths||[]).slice(0,2).join('；')||'无' }}</p>
        <details><summary>展开详细报告</summary>
          <div class="detail-grid">
            <div class="detail-block"><p class="d-label">计算过程</p><p>{{ r.parsed?.calculation||'无' }}</p></div>
            <div class="detail-block"><p class="d-label">不足之处</p><p>{{ (r.parsed?.gaps||[]).join('；')||'无' }}</p></div>
            <div class="detail-block"><p class="d-label">含金量评估</p><p>{{ (r.parsed?.quality_notes||[]).join('；')||'无' }}</p></div>
            <div class="detail-block"><p class="d-label">面试建议</p><ul><li v-for="q in (r.parsed?.interview_questions||[])":key="q">{{ q }}</li></ul></div>
          </div>
        </details>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, inject, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import axios from 'axios'
const route = useRoute(); const jobId = route.params.id
const { showLoading, hideLoading } = inject('loading')
const job = ref(null); const weights = ref({skills:50,education:20,experience:30})
const preferences = ref(''); const uploadMsg = ref(''); const ranking = ref([]); const selectedFile = ref(null)
const fetchJob = async () => { const res = await axios.get('/api/jobs/'+jobId); job.value=res.data; weights.value=res.data.weights||weights.value; preferences.value=res.data.preferences||'' }
const updateWeights = async () => { await axios.put('/api/jobs/'+jobId+'/weights', weights.value) }
const updatePreferences = async () => { await axios.post('/api/jobs/'+jobId+'/preferences', {text:preferences.value}) }
const handleFile = (e) => { selectedFile.value = e.target.files[0] }
const upload = async () => {
  if(!selectedFile.value) return; showLoading(); const fd = new FormData(); fd.append('file',selectedFile.value)
  try { const res = await axios.post('/api/jobs/'+jobId+'/upload',fd); uploadMsg.value='上传成功：'+res.data.filename; fetchRanking() }
  catch(e) { uploadMsg.value='失败：'+(e.response?.data?.detail||e.message) }
  finally { hideLoading() }
}
const fetchRanking = async () => { showLoading(); try { const res = await axios.get('/api/jobs/'+jobId+'/ranking'); ranking.value=res.data } finally { hideLoading() } }
const clearResumes = async () => { if(!confirm('确认清空？')) return; showLoading(); try { await axios.delete('/api/jobs/'+jobId+'/resumes'); ranking.value=[] } finally { hideLoading() } }
onMounted(()=>{fetchJob();fetchRanking()})
</script>

<style scoped>
.section { background:#fff; border-radius:var(--radius); padding:1.5rem 1.75rem; margin-bottom:1rem; }
.section h2 { font-size:1rem; font-weight:600; color:var(--slate-900); margin-bottom:1rem; }
.back { font-size:0.8rem; color:var(--slate-400); }
.controls { display:flex; gap:1.5rem; flex-wrap:wrap; margin-top:1rem; }
.ctrl { flex:1; min-width:200px; }
.ctrl-label { font-size:0.78rem; text-transform:uppercase; letter-spacing:0.06em; color:var(--slate-400); margin-bottom:0.5rem; }
.slider-row { display:flex; align-items:center; gap:0.5rem; font-size:0.82rem; color:var(--slate-600); margin-bottom:0.3rem; }
.slider-row input { flex:1; margin-bottom:0; }
.val { font-size:0.78rem; color:var(--slate-400); min-width:2.5rem; text-align:right; }
.msg { font-size:0.8rem; color:var(--slate-500); margin-top:0.5rem; }
.section-header { display:flex; align-items:center; justify-content:space-between; margin-bottom:0.75rem; }
.section-header h2 { margin-bottom:0; }
.empty { color:var(--slate-400); text-align:center; padding:2rem; }
.rank-card { background:var(--cream); border-radius:6px; padding:1.25rem 1.5rem; margin-bottom:0.625rem; }
.rank-top { display:flex; align-items:center; gap:0.75rem; margin-bottom:0.4rem; flex-wrap:wrap; }
.rank-num { font-weight:650; color:var(--accent); }
.rank-name { font-weight:600; color:var(--slate-900); }
.rank-file { font-size:0.78rem; color:var(--slate-400); }
.rank-score { font-size:1.3rem; font-weight:700; color:var(--accent); margin-left:auto; }
.rank-strength { font-size:0.85rem; color:var(--slate-500); margin-bottom:0.5rem; }
details summary { font-size:0.82rem; color:var(--slate-400); cursor:pointer; }
.detail-grid { display:grid; grid-template-columns:1fr 1fr; gap:0.75rem; margin-top:0.75rem; }
.detail-block { background:#fff; border-radius:6px; padding:0.875rem 1rem; }
.d-label { font-size:0.72rem; text-transform:uppercase; letter-spacing:0.06em; color:var(--slate-400); margin-bottom:0.25rem; }
.detail-block p { font-size:0.85rem; color:var(--slate-600); line-height:1.6; }
.detail-block ul { padding-left:1.2rem; }
.detail-block li { font-size:0.85rem; color:var(--slate-600); margin-bottom:0.25rem; }
</style>
