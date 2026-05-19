import { useEffect, useState } from "react";

export default function Dashboard() {
  const [stats, setStats] = useState(null);

  useEffect(() => {
    const fetchStats = async () => {
      const res = await fetch("http://127.0.0.1:8000/dashboard/stats");
      const data = await res.json();
      setStats(data);
    };

    fetchStats();
  }, []);

  return (
    <div>
      <h2>Dashboard</h2>

      {!stats ? (
        <p>Loading...</p>
      ) : (
        <div style={{ marginTop: "20px" }}>
          <p><b>Total Contacts:</b> {stats.total_master_contacts}</p>
          <p><b>Total Unsubscribed:</b> {stats.total_unsubscribed}</p>
          <p><b>Used Last 90 Days:</b> {stats.used_last_90_days}</p>
          <p><b>Total Uploads:</b> {stats.total_uploads}</p>
        </div>
      )}
    </div>
  );
}