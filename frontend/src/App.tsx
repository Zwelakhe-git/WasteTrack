import { useEffect, useState } from "react";
import { apiClient } from "./api/client";

function App() {
  const [status, setStatus] = useState<string>("...");

  useEffect(() => {
    apiClient
      .get("/health")
      .then((res) => setStatus(res.data.status))
      .catch(() => setStatus("error"));
  }, []);

  return (
    <div style={{ padding: 24, fontFamily: "sans-serif" }}>
      <h1>WasteTrack</h1>
      <p>Backend status: {status}</p>
    </div>
  );
}

export default App;
