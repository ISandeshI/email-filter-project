import { Routes, Route, Link } from "react-router-dom";

import Upload from "./pages/Upload.jsx";
import Dashboard from "./pages/Dashboard.jsx";
import History from "./pages/History.jsx";
import DashboardV2 from "./pages/DashboardV2";

export default function App() {

  return (

    <div className="
      flex
      min-h-screen
      bg-gray-100
    ">

      {/* Sidebar */}
      <aside className="
        w-[240px]
        bg-slate-900
        text-white
        p-6
        shadow-lg
      ">

        <h1 className="
          text-2xl
          font-bold
          mb-8
        ">
          Email SaaS
        </h1>

        <nav className="space-y-3">

          <Link
            className="
              block
              px-4
              py-3
              rounded-lg
              hover:bg-slate-800
              transition
            "
            to="/"
          >
            Dashboard
          </Link>

          <Link
            className="
              block
              px-4
              py-3
              rounded-lg
              hover:bg-slate-800
              transition
            "
            to="/upload"
          >
            Upload
          </Link>

          <Link
            className="
              block
              px-4
              py-3
              rounded-lg
              hover:bg-slate-800
              transition
            "
            to="/history"
          >
            History
          </Link>

          <Link
            className="
              block
              px-4
              py-3
              rounded-lg
              hover:bg-slate-800
              transition
            "
            to="/dashboard-v2"
          >
            Dashboard V2
          </Link>

        </nav>

      </aside>

      {/* Main Content */}
      <main className="
        flex-1
        p-8
        overflow-auto
      ">

        <Routes>

          <Route
            path="/"
            element={<Dashboard />}
          />

          <Route
            path="/upload"
            element={<Upload />}
          />

          <Route
            path="/history"
            element={<History />}
          />

          <Route
            path="/dashboard-v2"
            element={<DashboardV2 />}
          />

        </Routes>

      </main>

    </div>
  );
}