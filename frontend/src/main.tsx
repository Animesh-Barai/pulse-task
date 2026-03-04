import { StrictMode } from 'react-dom/client'
import { router } from './App'
import './styles/global.css'

ReactDOM.createRoot(
  document.getElementById('root')!,
  <React.StrictMode>
    {router}
  </React.StrictMode>
)
