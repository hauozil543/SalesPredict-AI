import React, { useState, useEffect } from 'react';
import { Bar, Line, Pie } from 'react-chartjs-2';
import 'chart.js/auto';

const HomePage = () => {
  const [overview, setOverview] = useState({});
  const [salesByDate, setSalesByDate] = useState([]);
  const [topProducts, setTopProducts] = useState([]);
  const [salesByStore, setSalesByStore] = useState([]);

  // State cho bộ lọc
  const [states, setStates] = useState([]);
  const [stores, setStores] = useState([]);
  const [dates, setDates] = useState([]);
  const [selectedState, setSelectedState] = useState('');
  const [selectedStore, setSelectedStore] = useState('');
  const [selectedDate, setSelectedDate] = useState('');

  // Lấy danh sách bang, cửa hàng, ngày khi component mount
  useEffect(() => {
    const fetchFilters = async () => {
      try {
        const [statesRes, datesRes] = await Promise.all([
          fetch('http://localhost:5000/states'),
          fetch('http://localhost:5000/dates'),
        ]);
        const statesData = await statesRes.json();
        const datesData = await datesRes.json();
        setStates(statesData);
        setDates(datesData);

        // Đặt giá trị mặc định cho state và date nếu có dữ liệu
        if (statesData.length > 0) setSelectedState(statesData[0]);
        if (datesData.length > 0) setSelectedDate(datesData[0]);
      } catch (err) {
        console.error('Lỗi khi lấy dữ liệu bộ lọc:', err);
      }
    };
    fetchFilters();
  }, []);

  // Lấy danh sách cửa hàng khi bang thay đổi
  useEffect(() => {
    if (selectedState) {
      const fetchStores = async () => {
        try {
          const storesRes = await fetch(`http://localhost:5000/stores?state=${selectedState}`);
          const storesData = await storesRes.json();
          setStores(storesData);
          if (storesData.length > 0) setSelectedStore(storesData[0]);
          else setSelectedStore('');
        } catch (err) {
          console.error('Lỗi khi lấy danh sách cửa hàng:', err);
        }
      };
      fetchStores();
    }
  }, [selectedState]);

  // Lấy dữ liệu chính khi bộ lọc thay đổi
  useEffect(() => {
    const fetchData = async () => {
      try {
        // Xây dựng query string từ các bộ lọc
        const queryParams = new URLSearchParams();
        if (selectedState) queryParams.append('state', selectedState);
        if (selectedStore) queryParams.append('store_id', selectedStore);
        if (selectedDate) queryParams.append('date', selectedDate);

        const [overviewRes, salesByDateRes, topProductsRes, salesByStoreRes] = await Promise.all([
          fetch(`http://localhost:5000/overview?${queryParams.toString()}`),
          fetch(`http://localhost:5000/sales_by_date?${queryParams.toString()}`),
          fetch(`http://localhost:5000/top_products?${queryParams.toString()}`),
          fetch(`http://localhost:5000/sales_by_store?${queryParams.toString()}`),
        ]);

        const overviewData = await overviewRes.json();
        const salesByDateData = await salesByDateRes.json();
        const topProductsData = await topProductsRes.json();
        const salesByStoreData = await salesByStoreRes.json();

        setOverview(overviewData);
        setSalesByDate(salesByDateData);
        setTopProducts(topProductsData);
        setSalesByStore(salesByStoreData);
      } catch (err) {
        console.error('Lỗi khi lấy dữ liệu:', err);
      }
    };

    fetchData();
  }, [selectedState, selectedStore, selectedDate]);

  const salesByDateChart = {
    labels: salesByDate.map((d) => d.date),
    datasets: [
      {
        label: 'Doanh thu theo ngày',
        data: salesByDate.map((d) => d.revenue),
        borderColor: 'rgba(75,192,192,1)',
        fill: false,
      },
    ],
  };

  const topProductsChart = {
    labels: topProducts.map((p) => p.item_id),
    datasets: [
      {
        label: 'Top 10 sản phẩm (doanh thu)',
        data: topProducts.map((p) => p.total_revenue),
        backgroundColor: 'rgba(54,162,235,0.6)',
      },
    ],
  };

  const salesByStoreChart = {
    labels: salesByStore.map((s) => s.store_id),
    datasets: [
      {
        label: 'Doanh thu theo cửa hàng',
        data: salesByStore.map((s) => s.total_revenue),
        backgroundColor: ['#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF'],
      },
    ],
  };

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-3xl font-bold mb-6">Tổng quan hệ thống</h1>

      {/* Bộ lọc */}
      <div className="mb-6 grid grid-cols-1 md:grid-cols-3 gap-4">
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
          <label className="block text-lg font-semibold mb-2">Lọc theo ngày</label>
          <select
            value={selectedDate}
            onChange={(e) => setSelectedDate(e.target.value)}
            className="w-full p-2 border rounded"
          >
            <option value="">Chọn ngày</option>
            {dates.map((date) => (
              <option key={date} value={date}>{date}</option>
            ))}
          </select>
        </div>
      </div>

      {/* Thẻ thông tin tổng quan */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        <div className="p-4 rounded-lg shadow-md bg-blue-100">
          <h3 className="text-lg font-semibold">Tổng doanh thu</h3>
          <p className="text-2xl">{overview.total_revenue?.toLocaleString()} VNĐ</p>
        </div>
        <div className="p-4 rounded-lg shadow-md bg-green-100">
          <h3 className="text-lg font-semibold">Sản phẩm bán ra</h3>
          <p className="text-2xl">{overview.total_products_sold}</p>
        </div>
        <div className="p-4 rounded-lg shadow-md bg-yellow-100">
          <h3 className="text-lg font-semibold">Số cửa hàng</h3>
          <p className="text-2xl">{overview.total_stores}</p>
        </div>
      </div>

      {/* Biểu đồ */}
      <div className="mb-6">
        <h2 className="text-xl font-semibold mb-2">Doanh thu theo thời gian</h2>
        <Line data={salesByDateChart} />
      </div>
      <div className="mb-6">
        <h2 className="text-xl font-semibold mb-2">Top 10 sản phẩm bán chạy</h2>
        <Bar data={topProductsChart} />
      </div>
      <div className="mb-6">
        <h2 className="text-xl font-semibold mb-2">Doanh thu theo cửa hàng</h2>
        <Pie data={salesByStoreChart} />
      </div>
    </div>
  );
};

export default HomePage;