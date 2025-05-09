import React, { useState } from 'react';

const Forecast = () => {
  const [formData, setFormData] = useState({
    item_id: 'FOODS_1_218',
    store_id: 'CA_1',
    start_date: '2016-04-25',
    end_date: '2016-05-03',
  });
  const [predictions, setPredictions] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const response = await fetch('http://localhost:5000/predict', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData),
      });

      if (!response.ok) throw new Error('Lỗi khi gọi API');
      const data = await response.json();
      if (data.status === 'success') {
        setPredictions(data.predictions);
      } else {
        setError(data.error || 'Lỗi không xác định');
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto">
      <h1 className="text-2xl font-bold mb-4">Dự báo Doanh Số</h1>
      <form onSubmit={handleSubmit} className="bg-white p-6 rounded-lg shadow-md">
        <div className="mb-4">
          <label className="block text-sm font-medium text-gray-700">Item ID</label>
          <input
            type="text"
            name="item_id"
            value={formData.item_id}
            onChange={handleChange}
            className="mt-1 block w-full p-2 border border-gray-300 rounded-md"
            required
          />
        </div>
        <div className="mb-4">
          <label className="block text-sm font-medium text-gray-700">Store ID</label>
          <input
            type="text"
            name="store_id"
            value={formData.store_id}
            onChange={handleChange}
            className="mt-1 block w-full p-2 border border-gray-300 rounded-md"
            required
          />
        </div>
        <div className="mb-4">
          <label className="block text-sm font-medium text-gray-700">Start Date</label>
          <input
            type="date"
            name="start_date"
            value={formData.start_date}
            onChange={handleChange}
            className="mt-1 block w-full p-2 border border-gray-300 rounded-md"
            required
          />
        </div>
        <div className="mb-4">
          <label className="block text-sm font-medium text-gray-700">End Date</label>
          <input
            type="date"
            name="end_date"
            value={formData.end_date}
            onChange={handleChange}
            className="mt-1 block w-full p-2 border border-gray-300 rounded-md"
            required
          />
        </div>
        <button
          type="submit"
          disabled={loading}
          className="w-full bg-blue-500 text-white p-2 rounded-md hover:bg-blue-600 disabled:bg-blue-300"
        >
          {loading ? 'Đang xử lý...' : 'Dự báo'}
        </button>
        {error && <p className="text-red-500 mt-2">{error}</p>}
      </form>

      {predictions.length > 0 && (
        <div className="mt-6 bg-white p-6 rounded-lg shadow-md">
          <h2 className="text-xl font-semibold mb-4">Kết quả Dự báo</h2>
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="bg-gray-200">
                <th className="p-2 border">Ngày</th>
                <th className="p-2 border">Dự báo</th>
              </tr>
            </thead>
            <tbody>
              {predictions.map((pred, index) => (
                <tr key={index} className={index % 2 === 0 ? 'bg-gray-100' : ''}>
                  <td className="p-2 border">{pred.date}</td>
                  <td className="p-2 border">{pred.prediction.toFixed(2)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};

export default Forecast;