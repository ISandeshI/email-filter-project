import { useEffect, useState } from "react";

export default function History() {
  const [history, setHistory] = useState([]);

  useEffect(() => {
    const fetchHistory = async () => {
      const res = await fetch(
        "http://127.0.0.1:8000/upload/history?page=1&limit=10"
      );
      const data = await res.json();
      setHistory(data.items || []);
    };

    fetchHistory();
  }, []);

  return (
    <div>
      <h2>Upload History</h2>

      {history.length === 0 ? (
        <p>No history found</p>
      ) : (
        <table border="1" cellPadding="8" style={{ marginTop: "20px" }}>
          <thead>
            <tr>
              <th>File Name</th>
              <th>Total Rows</th>
              <th>Valid Rows</th>
              <th>Time</th>
            </tr>
          </thead>

          <tbody>
            {history.map((item, index) => (
              <tr key={index}>
                <td>{item.filename}</td>
                <td>{item.total_rows}</td>
                <td>{item.valid_rows}</td>
                <td>{item.processing_time}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}