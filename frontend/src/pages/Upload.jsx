import { useState, useEffect } from "react";

import { API_BASE } from "../config";

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

    const res = await fetch(
      `${API_BASE}/upload`,
      {
        method: "POST",
        body: formData,
      }
    );

    const data = await res.json();

    setUploadId(data.upload_id);
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

    const res = await fetch(
      `${API_BASE}/upload/unsubscribed`,
      {
        method: "POST",
        body: formData,
      }
    );

    const data = await res.json();

    setUnsubscribeResult(data);

    setUnsubscribeLoading(false);
  };

  return (

    <div className="space-y-8">

      <h1 className="text-2xl font-bold">
        Upload Center
      </h1>

      {/* Main Upload Section */}
      <div className="
        bg-white
        border
        border-gray-200
        rounded-xl
        shadow-sm
        p-6
      ">

        <h2 className="
          text-xl
          font-semibold
          mb-4
        ">
          Upload Contacts
        </h2>

        <input
          type="file"
          onChange={(e) =>
            setFile(e.target.files[0])
          }
          className="mb-4"
        />

        <div>

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
            "
          >
            {loading
              ? "Uploading..."
              : "Upload File"}
          </button>

        </div>

        {uploadId && (

          <div className="mt-6 space-y-2">

            <p>
              <strong>Upload ID:</strong>
              {" "}
              {uploadId}
            </p>

            <p>
              <strong>Status:</strong>
              {" "}
              {status}
            </p>

            {status === "processing" && (
              <p>Processing...</p>
            )}

            {status === "completed" && (

              <div>

                <p className="mb-3">
                  Done ✔
                </p>

                <a
                  href={
                    `${API_BASE}/download/filtered_${uploadId}.xlsx`
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

              </div>

            )}

            {status === "failed" && (
              <p>
                Failed ❌
              </p>
            )}

          </div>

        )}

      </div>

      {/* Unsubscribe Upload Section */}
      <div className="
        bg-white
        border
        border-gray-200
        rounded-xl
        shadow-sm
        p-6
      ">

        <h2 className="
          text-xl
          font-semibold
          mb-4
        ">
          Upload Unsubscribed Contacts
        </h2>

        <p className="
          text-sm
          text-gray-500
          mb-4
        ">
          Required column:
          {" "}
          <strong>Email</strong>
        </p>

        <input
          type="file"
          onChange={(e) =>
            setUnsubscribeFile(
              e.target.files[0]
            )
          }
          className="mb-4"
        />

        <div>

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
            "
          >
            {unsubscribeLoading
              ? "Uploading..."
              : "Upload Unsubscribed List"}
          </button>

        </div>

        {unsubscribeResult && (

          <div className="
            mt-6
            space-y-2
          ">

            <p>
              <strong>Total Uploaded:</strong>
              {" "}
              {unsubscribeResult.total_uploaded}
            </p>

            <p>
              <strong>Inserted:</strong>
              {" "}
              {unsubscribeResult.inserted}
            </p>

          </div>

        )}

      </div>

    </div>
  );
}