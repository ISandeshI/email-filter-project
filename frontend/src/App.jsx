import { useEffect, useState } from "react";

function App() {
  const [stats, setStats] = useState(null);

  const [activePage, setActivePage] = useState("dashboard");

  const [selectedFile, setSelectedFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [uploadMessage, setUploadMessage] = useState("");
  const [uploadError, setUploadError] = useState("");
  const [uploadStats, setUploadStats] = useState(null);
  const [uploadProgress, setUploadProgress] = useState(0);

  const [uploadHistory, setUploadHistory] = useState([]);

  const [searchEmail, setSearchEmail] = useState("");
  const [searchResults, setSearchResults] = useState([]);
  const [searchLoading, setSearchLoading] = useState(false);

  useEffect(() => {
    const loadData = async () => {
      const statsRes = await fetch(
        "http://127.0.0.1:8000/dashboard/stats"
      );
      const statsData = await statsRes.json();
      setStats(statsData);

      const historyRes = await fetch(
        "http://127.0.0.1:8000/upload/history"
      );
      const historyData = await historyRes.json();
      setUploadHistory(historyData.results);
    };

    loadData();
  }, [activePage]);

  // =========================
  // UPLOAD
  // =========================
  const handleUpload = async () => {
    if (!selectedFile) {
      setUploadError("Please select a file");
      return;
    }

    const formData = new FormData();
    formData.append("file", selectedFile);

    try {
      setUploading(true);
      setUploadError("");
      setUploadMessage("");
      setUploadStats(null);
      setUploadProgress(10);

      const response = await fetch(
        "http://127.0.0.1:8000/upload",
        {
          method: "POST",
          body: formData,
        }
      );

      setUploadProgress(60);

      if (!response.ok) {
        const err = await response.json();
        throw new Error(err.error || "Upload failed");
      }

      const data = await response.json();

      setUploadProgress(90);

      setUploadStats({
        originalRows: data.stats.original_rows,
        validRows: data.stats.valid_rows,
        removedRows: data.stats.removed_rows,
        processingTime: `${data.stats.processing_time_seconds} sec`,
      });

      window.open(data.download_url, "_blank");

      setUploadProgress(100);

      setUploadMessage("Filtering completed successfully");

      // refresh dashboard + history
      const statsRes = await fetch(
        "http://127.0.0.1:8000/dashboard/stats"
      );
      setStats(await statsRes.json());

      const historyRes = await fetch(
        "http://127.0.0.1:8000/upload/history"
      );
      setUploadHistory((await historyRes.json()).results);

    } catch (error) {
      setUploadError(error.message);
    } finally {
      setUploading(false);
    }
  };

  // =========================
  // SEARCH
  // =========================
  const handleSearch = async () => {
    if (!searchEmail) return;

    try {
      setSearchLoading(true);

      const response = await fetch(
        `http://127.0.0.1:8000/contacts/search?email=${searchEmail}`
      );

      const data = await response.json();

      setSearchResults(data.results);
    } catch (error) {
      console.error(error);
    } finally {
      setSearchLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex bg-gray-100">

      {/* SIDEBAR */}
      <div className="w-64 bg-white shadow-lg p-6">

        <h1 className="text-2xl font-bold text-blue-600 mb-10">
          Contact Filter
        </h1>

        <nav className="space-y-4">

          <button
            onClick={() => setActivePage("dashboard")}
            className={`w-full text-left px-4 py-3 rounded-xl ${
              activePage === "dashboard"
                ? "bg-blue-100 text-blue-700 font-semibold"
                : "hover:bg-gray-100"
            }`}
          >
            Dashboard
          </button>

          <button
            onClick={() => setActivePage("upload")}
            className={`w-full text-left px-4 py-3 rounded-xl ${
              activePage === "upload"
                ? "bg-blue-100 text-blue-700 font-semibold"
                : "hover:bg-gray-100"
            }`}
          >
            Upload Contacts
          </button>

          <button
            onClick={() => setActivePage("search")}
            className={`w-full text-left px-4 py-3 rounded-xl ${
              activePage === "search"
                ? "bg-blue-100 text-blue-700 font-semibold"
                : "hover:bg-gray-100"
            }`}
          >
            Contact Search
          </button>

          <button
            onClick={() => setActivePage("history")}
            className={`w-full text-left px-4 py-3 rounded-xl ${
              activePage === "history"
                ? "bg-blue-100 text-blue-700 font-semibold"
                : "hover:bg-gray-100"
            }`}
          >
            Upload History
          </button>

        </nav>

      </div>

      {/* MAIN CONTENT */}
      <div className="flex-1 p-10">

        {/* DASHBOARD */}
        {activePage === "dashboard" && stats && (
          <div className="grid grid-cols-4 gap-6">
            <div className="bg-white p-6 rounded-xl shadow">
              Total Master Contacts
              <h2 className="text-2xl font-bold">
                {stats.total_master_contacts}
              </h2>
            </div>

            <div className="bg-white p-6 rounded-xl shadow">
              Unsubscribed
              <h2 className="text-2xl font-bold">
                {stats.total_unsubscribed}
              </h2>
            </div>

            <div className="bg-white p-6 rounded-xl shadow">
              Used 90 Days
              <h2 className="text-2xl font-bold">
                {stats.used_last_90_days}
              </h2>
            </div>

            <div className="bg-white p-6 rounded-xl shadow">
              Uploads
              <h2 className="text-2xl font-bold">
                {stats.total_uploads}
              </h2>
            </div>
          </div>
        )}

        {/* UPLOAD */}
        {activePage === "upload" && (
          <div className="max-w-xl bg-white p-6 rounded-xl shadow">

            <input
              type="file"
              onChange={(e) => setSelectedFile(e.target.files[0])}
              className="mb-4"
            />

            {/* PROGRESS BAR */}
            {uploading && (
              <div className="w-full bg-gray-200 rounded-full h-2 mb-4">
                <div
                  className="bg-blue-600 h-2 rounded-full transition-all"
                  style={{ width: `${uploadProgress}%` }}
                />
              </div>
            )}

            <button
              onClick={handleUpload}
              disabled={uploading}
              className="bg-blue-600 text-white px-6 py-2 rounded"
            >
              {uploading ? "Processing..." : "Upload"}
            </button>

            {uploadMessage && (
              <p className="text-green-600 mt-3">
                {uploadMessage}
              </p>
            )}

            {uploadError && (
              <p className="text-red-600 mt-3">
                {uploadError}
              </p>
            )}

            {uploadStats && (
              <div className="mt-6 space-y-2">
                <p>Original: {uploadStats.originalRows}</p>
                <p>Valid: {uploadStats.validRows}</p>
                <p>Removed: {uploadStats.removedRows}</p>
                <p>Time: {uploadStats.processingTime}</p>
              </div>
            )}

          </div>
        )}

        {/* SEARCH */}
        {activePage === "search" && (
          <div className="bg-white p-6 rounded-xl shadow max-w-xl">

            <input
              type="text"
              placeholder="Enter email"
              value={searchEmail}
              onChange={(e) => setSearchEmail(e.target.value)}
              className="border p-2 w-full mb-3"
            />

            <button
              onClick={handleSearch}
              className="bg-blue-600 text-white px-4 py-2 rounded"
            >
              Search
            </button>

            <div className="mt-4">
              {searchResults.map((item, i) => (
                <div key={i} className="border-b py-2">
                  <p>{item.email}</p>
                  <p>
                    {item.first_name} {item.last_name}
                  </p>
                  <p>
                    {item.unsubscribed
                      ? "Unsubscribed"
                      : "Active"}
                  </p>
                </div>
              ))}
            </div>

          </div>
        )}

        {/* HISTORY */}
        {activePage === "history" && (
          <div className="bg-white p-6 rounded-xl shadow">

            <table className="w-full">

              <thead>
                <tr>
                  <th>File</th>
                  <th>Rows</th>
                  <th>Valid</th>
                  <th>Time</th>
                </tr>
              </thead>

              <tbody>
                {uploadHistory.map((h, i) => (
                  <tr key={i}>
                    <td>{h.filename}</td>
                    <td>{h.total_rows}</td>
                    <td>{h.valid_rows}</td>
                    <td>
                      {h.processing_time_seconds}s
                    </td>
                  </tr>
                ))}
              </tbody>

            </table>

          </div>
        )}

      </div>
    </div>
  );
}

export default App;