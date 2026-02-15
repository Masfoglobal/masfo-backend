import React, { useEffect, useState } from "react";

function App() {
  const [message, setMessage] = useState("");

  useEffect(() => {
    fetch("https://masfo-backend.onrender.com/")
      .then(res => res.json())
      .then(data => setMessage(data.message))
      .catch(err => console.log(err));
  }, []);

  return (
    <div style={{ textAlign: "center", marginTop: "100px" }}>
      <h1>MASFO GLOBAL CONNECT LTD 🚀</h1>
      <p>{message}</p>
    </div>
  );
}

export default App;