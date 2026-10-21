const API_BASE_URL =
    import.meta.env.VITE_API_BASE_URL ||
    "https://stabilityatlas-api.onrender.com";
    

export async function fetchGridPrediction(scenarioData) {
  try {
    const response = await fetch(`${API_BASE_URL}/predict`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(scenarioData),
    });

    if (!response.ok) {
      throw new Error(`Server returned status: ${response.status}`);
    }

    return await response.json();
    
  } catch (error) {
    console.error("Error communicating with FastAPI backend:", error);
    throw error;
  }
}
