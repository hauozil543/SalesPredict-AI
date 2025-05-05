import React, { useState, useEffect } from 'react';
import { saveAs } from 'file-saver';

const History = () => {
  const [formData, setFormData] = useState({
    item_id: '',
    store_id: '',
    start_date: '',
    end_date: '',
    limit: '50',
  });
  const [forecastHistory, setForecastHistory] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const fetchHistory = async (params) => {
    setLoading(true);
    setError(null);
    console.log('Fetching history with params:', params); // Debug

    try {
      const query = new URLSearchParams();
      Object.entries(params).forEach(([key, value]) => {
        if (value) query.append(key, value);
      });

      const response = await fetch(`http://localhost:5000/history?${query.toString()}`, {
        method: 'GET',
        headers: { 'Content-Type': 'application/json' },
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.error || 'Lỗi khi gọi API');
      }

      const data = await response.json();
      console.log('API response:', data); // Debug
      if (data.status === 'success') {
        setForecastHistory(data.forecast_history || []);
      } else {
        setError(data.error || 'Không có dữ liệu');
      }
    } catch (err) {
      console.error('Fetch error:', err); // Debug
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    fetchHistory(formData);
  };

  useEffect(() => {
    fetchHistory({});
  }, []);

  const exportReport = () => {
    if (forecastHistory.length === 0) {
      setError('Không có dữ liệu để xuất báo cáo.');
      return;
    }

    const csvData = [];
    csvData.push(['Item ID', 'Store ID', 'Ngày', 'Dự báo', 'Thời gian thực hiện']); // Header

    forecastHistory.forEach((forecast) => {
      forecast.forecasts.forEach((pred) => {
        csvData.push([
          pred.item_id,
          pred.store_id,
          pred.date,
          pred.prediction.toFixed(2),
          forecast.timestamp,
        ]);
      });
    });

    const csvContent = csvData.map(row => row.join(',')).join('\n');
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    saveAs(blob, 'history_forecast_report.csv');
  };

  return (
    <div className="max-w-4xl mx-auto">
      <h1 className="text-2xl font-bold mb-4">Lịch Sử Dự Báo</h1>
      <form onSubmit={handleSubmit} className="bg-white p-6 rounded-lg shadow-md mb-6">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700">Item ID</label>
            <input
              type="text"
              name="item_id"
              value={formData.item_id}
              onChange={handleChange}
              className="mt-1 block w-full p-2 border border-gray-300 rounded-md"
              placeholder="Ví dụ: FOODS_1_218"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700">Store ID</label>
            <input
              type="text"
              name="store_id"
              value={formData.store_id}
              onChange={handleChange}
              className="mt-1 block w-full p-2 border border-gray-300 rounded-md"
              placeholder="Ví dụ: CA_1"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700">Start Date</label>
            <input
              type="date"
              name="start_date"
              value={formData.start_date}
              onChange={handleChange}
              className="mt-1 block w-full p-2 border border-gray-300 rounded-md"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700">End Date</label>
            <input
              type="date"
              name="end_date"
              value={formData.end_date}
              onChange={handleChange}
              className="mt-1 block w-full p-2 border border-gray-300 rounded-md"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700">Limit</label>
            <input
              type="number"
              name="limit"
              value={formData.limit}
              onChange={handleChange}
              className="mt-1 block w-full p-2 border border-gray-300 rounded-md"
              min="1"
              placeholder="Số lần dự báo tối đa"
            />
          </div>
        </div>
        <div className="mt-4 flex justify-between">
          <button
            type="submit"
            disabled={loading}
            className="bg-blue-500 text-white p-2 rounded-md hover:bg-blue-600 disabled:bg-blue-300"
          >
            {loading ? 'Đang xử lý...' : 'Tìm kiếm'}
          </button>
          <button
            type="button"
            onClick={exportReport}
            disabled={loading || forecastHistory.length === 0}
            className="bg-green-500 text-white p-2 rounded-md hover:bg-green-600 disabled:bg-green-300"
          >
            Xuất Báo Cáo
          </button>
        </div>
        {error && <p className="text-red-500 mt-2">{error}</p>}
      </form>

      {forecastHistory.length > 0 ? (
        <div className="space-y-6">
          {forecastHistory.map((forecast) => (
            <div key={forecast.stt} className="bg-white p-6 rounded-lg shadow-md">
              <h2 className="text-xl font-semibold mb-2">
                Lần dự báo {forecast.stt} - Thực hiện lúc: {forecast.timestamp}
              </h2>
              <table className="w-full text-left border-collapse">
                <thead>
                  <tr className="bg-gray-200">
                    <th className="p-2 border">Item ID</th>
                    <th className="p-2 border">Store ID</th>
                    <th className="p-2 border">Ngày</th>
                    <th className="p-2 border">Dự báo</th>
                  </tr>
                </thead>
                <tbody>
                  {forecast.forecasts.map((pred, index) => (
                    <tr key={index} className={index % 2 === 0 ? 'bg-gray-100' : ''}>
                      <td className="p-2 border">{pred.item_id}</td>
                      <td className="p-2 border">{pred.store_id}</td>
                      <td className="p-2 border">{pred.date}</td>
                      <td className="p-2 border">{pred.prediction.toFixed(2)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ))}
        </div>
      ) : (
        <p className="text-gray-500">Không có dữ liệu lịch sử để hiển thị.</p>
      )}
    </div>
  );
};

export default History;