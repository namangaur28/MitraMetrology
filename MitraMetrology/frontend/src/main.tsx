import React from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { ScanProvider } from './contexts/ScanContext'
import { Landing, Scan, Results } from './pages'
import './index.css'

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <ScanProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Landing />} />
          <Route path="/scan" element={<Scan />} />
          <Route path="/results/:id" element={<Results />} />
        </Routes>
      </BrowserRouter>
    </ScanProvider>
  </React.StrictMode>,
)
