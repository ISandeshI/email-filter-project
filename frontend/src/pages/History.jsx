import { useEffect, useState } from "react";
import PageContainer from "../components/PageContainer";
import { cleanFilename } from "../utils/fileUtils";
import DataTable from "../components/DataTable";
import { API_BASE } from "../config";

export default function History() {
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);

  const [searchTerm, setSearchTerm] = useState("");

  const [page, setPage] = useState(1);

  const [totalPages, setTotalPages] = useState(1);

  const LIMIT = 10;

  useEffect(() => {
    const delayDebounce = setTimeout(() => {
      fetchHistory();
    }, 400);

    return () => clearTimeout(delayDebounce);
  }, [searchTerm, page]);

  const fetchHistory = async () => {
    try {
      setLoading(true);

      const searchQuery = encodeURIComponent(searchTerm);

      const res = await fetch(
        `${API_BASE}/upload/history?page=${page}&limit=${LIMIT}&search=${searchQuery}`
      );

      const data = await res.json();

      setHistory(data.results || []);

      setTotalPages(data.total_pages || 1);

    } catch (err) {

      setHistory([]);

    } finally {

      setLoading(false);

    }
  };

  const handleDownload = (uploadId) => {
    if (!uploadId) return;

    window.open(
      `${API_BASE}/download/${uploadId}`,
      "_blank"
    );
  };

  const handleSearchChange = (value) => {

    setPage(1);

    setSearchTerm(value);

  };

  return (
    <PageContainer title="Upload History">

      <div className="bg-white p-4 rounded-xl shadow-sm mb-6">

        <input
          type="text"
          placeholder="Search by filename or upload ID..."
          value={searchTerm}
          onChange={(e) => handleSearchChange(e.target.value)}
          className="w-full border border-gray-200 rounded-lg px-4 py-2 outline-none focus:ring-2 focus:ring-blue-500"
        />

      </div>

      {loading ? (

        <div className="bg-white p-6 rounded-xl shadow-sm text-gray-500">
          Loading history...
        </div>

      ) : history.length === 0 ? (

        <div className="bg-white p-8 rounded-xl shadow-sm text-center text-gray-500">
          No upload history found
        </div>

      ) : (

        <>
          <DataTable
            columns={[
              { label: "File Name" },
              { label: "Campaign ID" },
              { label: "Total Rows" },
              { label: "Valid Rows" },
              { label: "Uploaded At" },
              { label: "Processing Time" },
              { label: "Actions" },
            ]}
            data={history}
            renderRow={(item, index) => (
              <tr key={index} className="hover:bg-gray-50 transition-colors">

                <td className="px-6 py-4 text-gray-700">
                  {cleanFilename(item.filename)}
                </td>

                <td className="px-6 py-4 text-gray-700 font-mono">
                  {item.upload_id}
                </td>

                <td className="px-6 py-4 text-gray-700">
                  {item.total_rows}
                </td>

                <td className="px-6 py-4 text-gray-700">
                  {item.valid_rows}
                </td>

                <td className="px-6 py-4 text-gray-700">
                  {new Intl.DateTimeFormat("en-IN", {
                    timeZone: "Asia/Kolkata",
                    day: "2-digit",
                    month: "short",
                    year: "numeric",
                    hour: "2-digit",
                    minute: "2-digit",
                    second: "2-digit",
                    hour12: true
                  }).format(new Date(item.uploaded_at))}
                </td>

                <td className="px-6 py-4 text-gray-700">
                  {item.processing_time_seconds}s
                </td>

                <td className="px-6 py-4">

                  <button
                    onClick={() => handleDownload(item.upload_id)}
                    disabled={!item.upload_id}
                    className="bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white px-4 py-2 rounded-lg text-sm"
                  >
                    Download
                  </button>

                </td>

              </tr>
            )}
          />

          <div className="flex items-center justify-between mt-6 bg-white p-4 rounded-xl shadow-sm">

            <button
              onClick={() => setPage((prev) => prev - 1)}
              disabled={page === 1}
              className="px-4 py-2 rounded-lg bg-gray-200 hover:bg-gray-300 disabled:opacity-50"
            >
              Previous
            </button>

            <div className="text-gray-700 font-medium">
              Page {page} of {totalPages}
            </div>

            <button
              onClick={() => setPage((prev) => prev + 1)}
              disabled={page >= totalPages}
              className="px-4 py-2 rounded-lg bg-gray-200 hover:bg-gray-300 disabled:opacity-50"
            >
              Next
            </button>

          </div>
        </>
      )}
    </PageContainer>
  );
}