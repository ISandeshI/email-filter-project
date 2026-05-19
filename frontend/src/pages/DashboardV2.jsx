import React, { useEffect, useState } from "react";

import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  ResponsiveContainer
} from "recharts";

import { API_BASE } from "../config";
import KpiCard from "../components/KpiCard";

export default function DashboardV2() {

  const [stats, setStats] = useState(null);

  const [uploadTrend, setUploadTrend] = useState([]);

  useEffect(() => {

    fetch(`${API_BASE}/dashboard/stats`)
      .then((res) => res.json())
      .then((data) => setStats(data))
      .catch((err) => console.log(err));

    fetch(`${API_BASE}/dashboard/upload-trend`)
      .then((res) => res.json())
      .then((data) => setUploadTrend(data))
      .catch((err) => console.log(err));

  }, []);

  return (
    <div className="p-6 space-y-6">

      <h1 className="text-2xl font-bold">
        Dashboard V2
      </h1>

      {!stats ? (
        <p>Loading...</p>
      ) : (
        <>

          {/* Primary KPI Row */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">

            <KpiCard
              title="Master Contacts"
              value={stats.total_master_contacts}
            />

            <KpiCard
              title="Unsubscribed"
              value={stats.total_unsubscribed}
            />

            <KpiCard
              title="Active Usage (90D)"
              value={stats.used_last_90_days}
            />

          </div>

          {/* Secondary KPI Row */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">

            <KpiCard
              title="Total Uploads"
              value={stats.total_uploads}
            />

            <KpiCard
              title="Filtered Contacts"
              value={stats.total_filtered_contacts}
            />

          </div>

          {/* Suppression Analytics */}
          <div>

            <h2 className="text-lg font-semibold mb-4">
              Suppression Analytics
            </h2>

            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">

              <KpiCard
                title="Duplicates Removed"
                value={stats.total_duplicates_removed}
              />

              <KpiCard
                title="Invalid Emails Removed"
                value={stats.total_invalid_removed}
              />

              <KpiCard
                title="Unsubscribed Removed"
                value={stats.total_unsubscribed_removed}
              />

              <KpiCard
                title="Recent Usage Removed"
                value={stats.total_recent_removed}
              />

            </div>

          </div>

          {/* Upload Trend Chart */}
          <div className="p-4 border rounded-lg">

            <h2 className="text-lg font-semibold mb-4">
              Upload Trend
            </h2>

            <div style={{ width: "100%", height: 300 }}>

              <ResponsiveContainer>

                <LineChart data={uploadTrend}>

                  <CartesianGrid strokeDasharray="3 3" />

                  <XAxis
                    dataKey="date"
                    tick={{ fontSize: 12 }}
                  />

                  <YAxis
                    tick={{ fontSize: 12 }}
                  />

                  <Tooltip />

                  <Line
                    type="monotone"
                    dataKey="uploads"
                  />

                </LineChart>

              </ResponsiveContainer>

            </div>

          </div>

        </>
      )}

    </div>
  );
}