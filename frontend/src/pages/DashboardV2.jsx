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

import PageContainer from "../components/PageContainer";

export default function DashboardV2() {

  const [stats, setStats] = useState(null);

  const [uploadTrend, setUploadTrend] = useState([]);

  const [loading, setLoading] = useState(true);

  useEffect(() => {

    const fetchDashboardData = async () => {

      try {

        const statsRes = await fetch(
          `${API_BASE}/dashboard/stats`
        );

        const statsData = await statsRes.json();

        setStats(statsData);

        const trendRes = await fetch(
          `${API_BASE}/dashboard/upload-trend`
        );

        const trendData = await trendRes.json();

        setUploadTrend(trendData);

      } catch (err) {

        console.log(err);

      } finally {

        setLoading(false);
      }
    };

    fetchDashboardData();

  }, []);

  return (

    <PageContainer title="Analytics Dashboard">

      {loading ? (

        <div className="
          bg-white
          p-6
          rounded-xl
          shadow-sm
          text-gray-500
        ">
          Loading dashboard...
        </div>

      ) : (

        <div className="space-y-8">

          {/* Primary KPI Row */}
          <div>

            <h2 className="
              text-lg
              font-semibold
              text-gray-800
              mb-4
            ">
              Overview
            </h2>

            <div className="
              grid
              grid-cols-1
              md:grid-cols-3
              gap-4
            ">

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

          </div>

          {/* Secondary KPI Row */}
          <div>

            <h2 className="
              text-lg
              font-semibold
              text-gray-800
              mb-4
            ">
              Upload Analytics
            </h2>

            <div className="
              grid
              grid-cols-1
              md:grid-cols-2
              gap-4
            ">

              <KpiCard
                title="Total Uploads"
                value={stats.total_uploads}
              />

              <KpiCard
                title="Filtered Contacts"
                value={stats.total_filtered_contacts}
              />

            </div>

          </div>

          {/* Suppression Analytics */}
          <div>

            <h2 className="
              text-lg
              font-semibold
              text-gray-800
              mb-4
            ">
              Suppression Analytics
            </h2>

            <div className="
              grid
              grid-cols-1
              md:grid-cols-2
              xl:grid-cols-4
              gap-4
            ">

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

          {/* Upload Trend */}
          <div className="
            bg-white
            p-6
            rounded-xl
            shadow-sm
          ">

            <div className="mb-6">

              <h2 className="
                text-lg
                font-semibold
                text-gray-800
              ">
                Upload Trend
              </h2>

              <p className="
                text-sm
                text-gray-500
                mt-1
              ">
                Upload activity trend over time.
              </p>

            </div>

            <div style={{ width: "100%", height: 320 }}>

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

        </div>

      )}

    </PageContainer>
  );
}