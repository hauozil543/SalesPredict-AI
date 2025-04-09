import React from "react";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Tooltip,
  Legend,
} from "chart.js";
import { Bar } from "react-chartjs-2";

// Đăng ký các thành phần cần thiết cho Bar chart
ChartJS.register(CategoryScale, LinearScale, BarElement, Tooltip, Legend);

const HomePage = () => {
  const barChartData = {
    labels: ["Electronics", "Clothing", "Groceries", "Books"],
    datasets: [
      {
        label: "Sales by Category",
        data: [300, 200, 150, 100],
        backgroundColor: [
          "rgba(255, 99, 132, 0.6)",
          "rgba(54, 162, 235, 0.6)",
          "rgba(255, 206, 86, 0.6)",
          "rgba(75, 192, 192, 0.6)",
        ],
        borderColor: [
          "rgba(255, 99, 132, 1)",
          "rgba(54, 162, 235, 1)",
          "rgba(255, 206, 86, 1)",
          "rgba(75, 192, 192, 1)",
        ],
        borderWidth: 1,
      },
    ],
  };

  return (
    <div style={{ width: "600px", margin: "auto" }}>
      <h2 style={{ textAlign: "center" }}>Sales by Category</h2>
      <Bar data={barChartData} options={{ responsive: true }} />
    </div>
  );
};

export default HomePage;
