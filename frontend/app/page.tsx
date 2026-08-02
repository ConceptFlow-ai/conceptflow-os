"use client";

import { useState } from "react";

export default function Home() {
  const [message, setMessage] = useState("");

  const testBackend = async () => {
    try {
      const response = await fetch("http://localhost:8000/health");

      const data = await response.json();

      setMessage(data.message);
    } catch (error) {
      console.error(error);
      setMessage("Could not connect to backend");
    }
  };

  return (
    <main className="p-10">
      <h1 className="text-3xl font-bold">
        ConceptFlow
      </h1>

      <button
        onClick={testBackend}
        className="mt-5 rounded bg-black px-4 py-2 text-white"
      >
        Test Backend
      </button>

      <p className="mt-5">
        {message}
      </p>
    </main>
  );
}
