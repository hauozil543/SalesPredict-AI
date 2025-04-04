const API_URL = "http://localhost:5000";

export async function fetchForecastData(inputData) {
    const response = await fetch(`${API_URL}/predict`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(inputData),
    });
    return response.json();
}
