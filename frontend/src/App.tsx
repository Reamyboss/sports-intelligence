import { Route, Routes } from 'react-router-dom'
import { MatchListPage } from './pages/MatchListPage'
import { MatchDetailPage } from './pages/MatchDetailPage'

export default function App() {
  return (
    <div className="min-h-screen bg-[var(--bg)]">
      <Routes>
        <Route path="/" element={<MatchListPage />} />
        <Route path="/matches/:id" element={<MatchDetailPage />} />
      </Routes>
    </div>
  )
}
