import { Outlet } from "react-router-dom"
import AppSidebar from "./AppSidebar"
import ChatFab from "./ChatFab"
import { usePresentation } from "@/contexts/PresentationContext"

export default function AppLayout() {
  const { isPresentation } = usePresentation()

  return (
    <div className="flex min-h-screen">
      {!isPresentation && <AppSidebar />}
      <main className="flex-1 overflow-auto bg-background">
        <Outlet />
      </main>
      {!isPresentation && <ChatFab />}
    </div>
  )
}
