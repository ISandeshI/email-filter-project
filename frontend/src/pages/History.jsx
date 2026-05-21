import { useEffect, useState } from "react";
import PageContainer from "../components/PageContainer";
import { cleanFilename } from "../utils/fileUtils";
import DataTable from "../components/DataTable";
import { API_BASE } from "../config";

export default function History() {
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState("");

  useEffect(() => {
    const fetchHistory = async () => {
      try {
        const res = await fetch(
          `${API_BASE}/upload/history?page=1&limit=10`
        );

        const data = await res.json();

        setHistory(data.results || []);
      } catch (err) {
        setHistory([]);
      } finally {
        setLoading(false);
      }
    };

    fetchHistory();
  }, []);

  const filteredHistory = history.filter((item) =>
    cleanFilename(item.filename)
      .toLowerCase()
      .includes(searchTerm.toLowerCase())
  );

  return (
    <PageContainer title="Upload History">
      <div className="bg-white p-4 rounded-xl shadow-sm mb-6">
        <input
          type="text"
          placeholder="Search by filename..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="w-full border border-gray-200 rounded-lg px-4 py-2 outline-none focus:ring-2 focus:ring-blue-500"
        />
      </div>

      {loading ? (
        <div className="bg-white p-6 rounded-xl shadow-sm text-gray-500">
          Loading history...
        </div>
      ) : filteredHistory.length === 0 ? (
        <div className="bg-white p-8 rounded-xl shadow-sm text-center text-gray-500">
          No upload history found
        </div>
      ) : (
        <DataTable
          columns={[
            { label: "File Name" },
            { label: "Total Rows" },
            { label: "Valid Rows" },
            { label: "Uploaded At" },
            { label: "Processing Time" },
          ]}
          data={filteredHistory}
          renderRow={(item, index) => (
            <tr key={index} className="hover:bg-gray-50 transition-colors">
              <td className="px-6 py-4 text-gray-700">
                {cleanFilename(item.filename)}
              </td>

              <td className="px-6 py-4 text-gray-700">
                {item.total_rows}
              </td>

              <td className="px-6 py-4 text-gray-700">
                {item.valid_rows}
              </td>

              <td className="px-6 py-4 text-gray-700">
                {new Date(item.uploaded_at).toLocaleString()}
              </td>

              <td className="px-6 py-4 text-gray-700">
                {item.processing_time_seconds}s
              </td>
            </tr>
          )}
        />
      )}
    </PageContainer>
  );
}