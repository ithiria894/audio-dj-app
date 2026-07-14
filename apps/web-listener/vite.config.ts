import { defineConfig } from 'vite'

// host 0.0.0.0 so a second phone can open http://<LAN-IP>:5173 for subjective listening.
// Objective PCM/AudioWorklet analysis must use http://localhost:5173 (secure-context exemption).
export default defineConfig({
  server: { host: '0.0.0.0', port: 5173, strictPort: true },
})
