<script setup>
import { ref, provide } from 'vue'
import { RouterLink, RouterView } from 'vue-router'

const isLoading = ref(false)
provide('loading', {
  showLoading: () => { isLoading.value = true },
  hideLoading: () => { isLoading.value = false }
})
</script>

<template>
  <div class="app">
    <header>
      <span class="logo">HR-Match</span>
      <nav><RouterLink to="/">岗位管理</RouterLink></nav>
    </header>
    <main><RouterView /></main>
    <Teleport to="body">
      <div v-if="isLoading" class="loading-overlay"><div class="loading-spinner" /></div>
    </Teleport>
  </div>
</template>

<style>
:root {
  --cream: #faf7f2; --cream-dark: #f2eee6; --slate-100: #eef0f2; --slate-200: #e2e5e9;
  --slate-400: #a4abb3; --slate-500: #6c7480; --slate-700: #3a4048; --slate-900: #1a1d21;
  --accent: #5b7fbd; --accent-hover: #4a6da8; --radius: 8px;
}
*, *::before, *::after { margin:0; padding:0; box-sizing:border-box; }
body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: var(--cream); color: var(--slate-700); line-height: 1.5; -webkit-font-smoothing: antialiased; }
.app { min-height: 100vh; }
header { background:var(--cream); padding:0 1.75rem; height:52px; display:flex; align-items:center; gap:2.5rem; border-bottom:1px solid var(--slate-200); position:sticky; top:0; z-index:10; }
.logo { font-weight:650; font-size:1rem; letter-spacing:-0.02em; color:var(--slate-900); }
nav a { color:var(--slate-500); text-decoration:none; font-size:0.85rem; font-weight:500; }
nav a:hover, nav a.router-link-exact-active { color:var(--slate-900); }
main { max-width: 1400px; margin: 0 auto; padding: 2rem 1.75rem; }
input, textarea { width:100%; padding:0.55rem 0.65rem; margin-bottom:0.65rem; background:#fff; border:1px solid var(--slate-200); border-radius:6px; color:var(--slate-700); font-size:0.85rem; font-family:inherit; }
input:focus, textarea:focus { outline:none; border-color:var(--accent); }
textarea { min-height:100px; font-family:'SF Mono','Fira Code',monospace; font-size:0.8rem; }
button { background:var(--accent); color:#fff; border:none; padding:0.45rem 1rem; border-radius:7px; cursor:pointer; font-size:0.8125rem; font-weight:500; letter-spacing:0.01em; transition:all 0.18s cubic-bezier(0.16,1,0.3,1); }
button:hover { background:var(--accent-hover); box-shadow:0 2px 8px rgba(91,127,189,0.18); }
button:active { transform:scale(0.97); box-shadow:none; }
button.secondary { background:transparent; color:var(--slate-500); border:1px solid var(--slate-200); }
button.secondary:hover { background:var(--slate-100); box-shadow:none; }
a { color:var(--accent); text-decoration:none; }
.loading-overlay { position:fixed; inset:0; z-index:100; display:flex; align-items:center; justify-content:center; background:rgba(250,247,242,0.65); backdrop-filter:blur(6px); }
.loading-spinner { width:36px; height:36px; border:3px solid var(--slate-200); border-top-color:var(--accent); border-radius:50%; animation:spin 0.7s linear infinite; }
@keyframes spin { to { transform:rotate(360deg); } }
</style>
