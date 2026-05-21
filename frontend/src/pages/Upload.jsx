import { useState, useEffect } from "react";
import { API_BASE } from "../config";
import PageContainer from "../components/PageContainer";
import Card from "../components/Card";

export default function Upload() {

  // Main Upload
  const [file, setFile] = useState(null);

  const [uploadId, setUploadId] = useState(null);

  const [status, setStatus] = useState(null);

  const [loading, setLoading] = useState(false);

  // Unsubscribe Upload
  const [unsubscribeFile, setUnsubscribeFile] =
    useState(null);

  const [unsubscribeLoading, setUnsubscribeLoading] =
    useState(false);

  const [unsubscribeResult, setUnsubscribeResult] =
    useState(null);

  // ====================================
  // MAIN CONTACT UPLOAD
  // ====================================

  const handleUpload = async () => {

    if (!file) return;

    setLoading(true);

    setStatus("uploading");

    const formData = new FormData();

    formData.append("file", file);

    try {

      const res = await fetch(
        `${API_BASE}/upload`,
        {
          method: "POST",
          body: formData,
        }
      );

      const data = await res.json();

      setUploadId(data.upload_id);

    } catch (err) {

      setStatus("failed");

      setLoading(false);
    }
  };

  // ====================================
  // STATUS TRACKING
  // ====================================

  useEffect(() => {

    if (!uploadId) return;

    const interval = setInterval(async () => {

      const res = await fetch(
        `${API_BASE}/upload/status/${uploadId}`
      );

      const data = await res.json();

      setStatus(data.status);

      if (
        data.status === "completed"
        || data.status === "failed"
      ) {

        clearInterval(interval);

        setLoading(false);
      }

    }, 2000);

    return () => clearInterval(interval);

  }, [uploadId]);

  // ====================================
  // UNSUBSCRIBE UPLOAD
  // ====================================

  const handleUnsubscribeUpload = async () => {

    if (!unsubscribeFile) return;

    setUnsubscribeLoading(true);

    const formData = new FormData();

    formData.append("file", unsubscribeFile);

    try {

      const res = await fetch(
        `${API_BASE}/upload/unsubscribed`,
        {
          method: "POST",
          body: formData,
        }
      );

      const data = await res.json();

      setUnsubscribeResult(data);

    } catch (err) {

      console.error(err);

    } finally {

      setUnsubscribeLoading(false);
    }
  };

  return (

    <PageContainer title="Upload Center">

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">

        {/* Main Upload Section */}
        <Card className="border border-gray-200 space-y-5">

          <div>

            <h2 className="
              text-xl
              font-semibold
              text-gray-800
            ">
              Upload Contacts
            </h2>

            <p className="
              text-sm
              text-gray-500
              mt-1
            ">
              Upload CSV/XLSX files for filtering and suppression.
            </p>

          </div>

          <input
            type="file"
            onChange={(e) =>
              setFile(e.target.files[0])
            }
            className="
              block
              w-full
              text-sm
              text-gray-600
            "
          />

          <button
            onClick={handleUpload}
            disabled={!file || loading}
            className="
              bg-slate-900
              text-white
              px-5
              py-3
              rounded-lg
              hover:bg-slate-800
              transition
              disabled:opacity-50
            "
          >
            {loading
              ? "Uploading..."
              : "Upload File"}
          </button>

          {uploadId && (

            <div className="
              border-t
              pt-5
              space-y-3
            ">

              <div className="text-sm">
                <span className="font-medium">
                  Upload ID:
                </span>
                {" "}
                {uploadId}
              </div>

              <div className="text-sm">
                <span className="font-medium">
                  Status:
                </span>
                {" "}
                <span className="capitalize">
                  {status}
                </span>
              </div>

              {status === "processing" && (
                <div className="text-blue-600 text-sm">
                  Processing file...
                </div>
              )}

              {status === "completed" && (

                <a
                  href={
                    `${API_BASE}/download/filtered_${uploadId}.csv`
                  }
                  target="_blank"
                  rel="noreferrer"
                  className="
                    inline-block
                    bg-green-600
                    text-white
                    px-5
                    py-3
                    rounded-lg
                    hover:bg-green-700
                    transition
                  "
                >
                  Download Filtered File
                </a>

              )}

              {status === "failed" && (
                <div className="text-red-600 text-sm">
                  Upload failed
                </div>
              )}

            </div>

          )}

        </Card>

        {/* Unsubscribe Upload Section */}
        <Card className="border border-gray-200 space-y-5">

          <div>

            <h2 className="
              text-xl
              font-semibold
              text-gray-800
            ">
              Upload Unsubscribed Contacts
            </h2>

            <p className="
              text-sm
              text-gray-500
              mt-1
            ">
              Required column: Email
            </p>

          </div>

          <input
            type="file"
            onChange={(e) =>
              setUnsubscribeFile(
                e.target.files[0]
              )
            }
            className="
              block
              w-full
              text-sm
              text-gray-600
            "
          />

          <button
            onClick={handleUnsubscribeUpload}
            disabled={
              !unsubscribeFile
              || unsubscribeLoading
            }
            className="
              bg-red-600
              text-white
              px-5
              py-3
              rounded-lg
              hover:bg-red-700
              transition
              disabled:opacity-50
            "
          >
            {unsubscribeLoading
              ? "Uploading..."
              : "Upload Unsubscribed List"}
          </button>

          {unsubscribeResult && (

            <div className="
              border-t
              pt-5
              space-y-2
              text-sm
            ">

              <div>
                <span className="font-medium">
                  Total Uploaded:
                </span>
                {" "}
                {unsubscribeResult.total_uploaded}
              </div>

              <div>
                <span className="font-medium">
                  Inserted:
                </span>
                {" "}
                {unsubscribeResult.inserted}
              </div>

            </div>

          )}

        </Card>

      </div>

    </PageContainer>
  );
}