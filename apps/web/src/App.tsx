import { BrowserRouter, Routes, Route } from "react-router-dom"
import AppLayout from "@/components/AppLayout"
import Dashboard from "@/pages/Dashboard"
import Feedback from "@/pages/Feedback"
import Roadmap from "@/pages/Roadmap"
import Stories from "@/pages/Stories"
import NotFound from "@/pages/NotFound"

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<AppLayout />}>
          <Route index element={<Dashboard />} />
          <Route path="/feedback" element={<Feedback />} />
          <Route path="/roadmap" element={<Roadmap />} />
          <Route path="/stories" element={<Stories />} />
        </Route>
        <Route path="*" element={<NotFound />} />
      </Routes>
    </BrowserRouter>
  )
}
