import React, { StrictMode } from 'react'
import ReactDOM from 'react-dom/client'
import App from './App'
import './styles/global.css'

console.log('PulseTask Frontend: v2 (Interactive Mode Active)');
ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
)
