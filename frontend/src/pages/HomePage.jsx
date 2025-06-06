import React, { useState, useEffect, use } from "react";
import { Bar, Line, Pie } from "react-chartjs-2";
import "chart.js/auto";

// Dữ liệu bang và cửa hàng cố định
const states = ["CA", "TX", "WI"];
const storesByState = {
  CA: ["CA_1", "CA_2", "CA_3", "CA_4"],
  TX: ["TX_1", "TX_2", "TX_3"],
  WI: ["WI_1", "WI_2", "WI_3"],
};

const HomePage = () => {
  const [overview, setOverview] = useState({});
  const [salesByDate, setSalesByDate] = useState([]);
  const [topProducts, setTopProducts] = useState([]);
  const [productCategories, setProductCategories] = useState([]);
  const [stores, setStores] = useState([]);
  const [dates, setDates] = useState([]);
  const [selectedState, setSelectedState] = useState("CA");
  const [selectedStore, setSelectedStore] = useState("CA_1");
  const [startDate, setStartDate] = useState("2016-01-01");
  const [endDate, setEndDate] = useState("2016-04-24");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchDates = async () => {
      setLoading(true);
      setError(null);
      try {
        const datesRes = await fetch("http://localhost:5000/dates");
        if (!datesRes.ok) throw new Error("Lỗi khi lấy danh sách ngày");
        const datesData = await datesRes.json();
        setDates(datesData);
      } catch (err) {
        setError("Không thể lấy danh sách ngày. Vui lòng thử lại.");
        console.error("Lỗi khi lấy danh sách ngày:", err);
      } finally {
        setLoading(false);
      }
    };
    fetchDates();
  }, []);

  useEffect(() => {
    setStores(storesByState[selectedState] || []);
    if (storesByState[selectedState] && storesByState[selectedState].length > 0) {
      setSelectedStore(storesByState[selectedState][0]);
    } else {
      setSelectedStore("");
    }
  }, [selectedState]);

  const handleSearch = async () => {
    if (!selectedState || !selectedStore || !startDate || !endDate) {
      setError("Vui lòng điền đầy đủ thông tin lọc.");
      return;
    }

    const start = new Date(startDate);
    const end = new Date(endDate);
    if (isNaN(start.getTime()) || isNaN(end.getTime()) || start > end) {
      setError("Ngày kết thúc phải lớn hơn hoặc bằng ngày bắt đầu và định dạng hợp lệ.");
      return;
    }

    setLoading(true);
    setError(null);
    try {
      const queryParams = new URLSearchParams();
      if (selectedState) queryParams.append("state", selectedState);
      if (selectedStore) queryParams.append("store_id", selectedStore);
      if (startDate) queryParams.append("startDate", startDate);
      if (endDate) queryParams.append("endDate", endDate);

      console.log(`Fetching with params: ${queryParams.toString()}`);
      const dashboardRes = await fetch(`http://localhost:5000/dashboard?${queryParams.toString()}`);
      if (!dashboardRes.ok) throw new Error("Lỗi khi lấy dữ liệu từ dashboard");
      const data = await dashboardRes.json();
      console.log("API Response:", data);

      setOverview(data.overview);
      setSalesByDate(data.sales_by_date);
      setTopProducts(data.top_products);
      setProductCategories(data.product_categories);
    } catch (err) {
      setError("Không thể lấy dữ liệu. Vui lòng thử lại.");
      console.error("Lỗi khi lấy dữ liệu:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    handleSearch(); // Gọi hàm tìm kiếm khi component được mount
  },[])

  const salesByDateChart = {
    labels: salesByDate.map((d) => d.date),
    datasets: [
      {
        label: "Doanh thu theo ngày",
        data: salesByDate.map((d) => d.revenue),
        borderColor: "rgba(75,192,192,1)",
        fill: false,
      },
    ],
  };

  const topProductsChart = {
    labels: topProducts.map((p) => p.item_id),
    datasets: [
      {
        label: "Top 10 sản phẩm bán chạy",
        data: topProducts.map((p) => p.total_sales),
        backgroundColor: [
          "#FF6384", "#36A2EB", "#FFCE56", "#4BC0C0", "#9966FF",
          "#FF9F40", "#FFCD56", "#4BC0C0", "#36A2EB", "#FF6384",
        ],
      },
    ],
  };

  const productCategoriesChart = {
    labels: productCategories.map((p) => p.category),
    datasets: [
      {
        label: "Tỷ lệ doanh số theo loại sản phẩm",
        data: productCategories.map((p) => p.total_sales),
        backgroundColor: [
          "#FF6384", "#36A2EB", "#FFCE56", "#4BC0C0", "#9966FF",
          "#FF9F40", "#FFCD56",
        ],
      },
    ],
  };

  const pieChartOptions = {
    plugins: {
      legend: {
        display: false, // Tắt chú thích
      },
    },
  };

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-3xl font-bold mb-6">Tổng quan hệ thống</h1>

      <div className="grid grid-cols-3 gap-4 sm:grid-cols-2 md:gap-6">
        <div>
          <label className="block text-lg font-semibold mb-2">Lọc theo bang</label>
          <select
            value={selectedState}
            onChange={(e) => setSelectedState(e.target.value)}
            className="w-full p-2 border rounded"
          >
            <option value="">Chọn bang</option>
            {states.map((state) => (
              <option key={state} value={state}>{state}</option>
            ))}
          </select>
        </div>
        <div>
          <label className="block text-lg font-semibold mb-2">Lọc theo cửa hàng</label>
          <select
            value={selectedStore}
            onChange={(e) => setSelectedStore(e.target.value)}
            className="w-full p-2 border rounded"
            disabled={!selectedState}
          >
            <option value="">Chọn cửa hàng</option>
            {stores.map((store) => (
              <option key={store} value={store}>{store}</option>
            ))}
          </select>
        </div>
        <div>
          <label className="block text-lg font-semibold mb-2">Lọc theo khoảng thời gian</label>
          <div className="flex gap-2">
            <input
              type="date"
              value={startDate}
              onChange={(e) => setStartDate(e.target.value)}
              className="w-full p-2 border rounded"
              min={dates[0] || "2016-01-01"}
              max={endDate || "2016-04-24"}
            />
            <span className="self-center">đến</span>
            <input
              type="date"
              value={endDate}
              onChange={(e) => setEndDate(e.target.value)}
              className="w-full p-2 border rounded"
              min={startDate || "2016-01-01"}
              max={dates[dates.length - 1] || "2016-04-24"}
            />
          </div>
        </div>
      </div>

      <button
        onClick={handleSearch}
        className="mb-6 bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"
      >
        Tìm kiếm
      </button>
      {loading && <p className="text-center">Đang tải dữ liệu...</p>}
      {error && <p className="text-red-500 text-center">{error}</p>}

      {/* Thẻ tổng quan */}
      <div className="grid grid-cols-3 gap-4 sm:grid-cols-2 md:gap-6">
        <div className="rounded-2xl border border-gray-200 bg-white p-5 dark:border-gray-800 dark:bg-white/[0.03] md:p-6">
          <div className="mt-5 flex items-end justify-between">
            <div>
              <span className="text-sm text-gray-500 dark:text-gray-400">
                Tổng doanh thu
              </span>
              <h4 className="mt-2 text-2xl font-bold text-gray-800">
                {overview.total_revenue?.toLocaleString() || 0} USD
              </h4>
            </div>
          </div>
        </div>

        <div className="rounded-2xl border border-gray-200 bg-white p-5 dark:border-gray-800 dark:bg-white/[0.03] md:p-6">
          <div className="mt-5 flex items-end justify-between">
            <div>
              <span className="text-sm text-gray-500 dark:text-gray-400">
                Số sản phẩm mà cửa hàng đó bán
              </span>
              <h4 className="mt-2 text-2xl font-bold text-gray-800">
                {overview.total_products_sold_by_store || 0}
              </h4>
            </div>
          </div>
        </div>
        <div className="rounded-2xl border border-gray-200 bg-white p-5 dark:border-gray-800 dark:bg-white/[0.03] md:p-6">
          <div className="mt-5 flex items-end justify-between">
            <div>
              <span className="text-sm text-gray-500 dark:text-gray-400">
                Số loại sản phẩm mà cửa hàng đó bán
              </span>
              <h4 className="mt-2 text-2xl font-bold text-gray-800">
                <p className="text-2xl">
                  {overview.total_product_categories || 0}
                </p>
              </h4>
            </div>
          </div>
        </div>
      </div>

      {/* Biểu đồ */}
      <div className="mb-6">
        <h2 className="text-xl font-semibold mb-2">Doanh thu theo thời gian</h2>
        <Line data={salesByDateChart} height={100} />
      </div>
      <div className="grid grid-cols-2 gap-4 sm:grid-cols-2 md:gap-6">
        <div className="mb-6">
          <h2 className="text-xl font-semibold mb-2">Top 10 sản phẩm bán chạy</h2>
          <Bar data={topProductsChart} height={300}/>
        </div>
        <div className="mb-6">
          <h2 className="text-xl font-semibold mb-2">Tỷ lệ doanh số theo loại sản phẩm</h2>
          <Pie data={productCategoriesChart} options={pieChartOptions} width={50} height={50} />
        </div>
      </div>
    </div>
  );
};

export default HomePage;