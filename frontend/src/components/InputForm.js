import React, { useState } from "react";
import { getForecast } from "../services/api";

const InputForm = () => {
    const [inputData, setInputData] = useState("");
    const [result, setResult] = useState(null);

    const handleSubmit = async (event) => {
        event.preventDefault();
        const features = inputData.split(",").map(Number);
        const response = await getForecast(features);
        setResult(response.prediction);
    };

    return (
        <div>
            <h2>Nhập dữ liệu dự báo</h2>
            <form onSubmit={handleSubmit}>
                <input
                    type="text"
                    value={inputData}
                    onChange={(e) => setInputData(e.target.value)}
                    placeholder="Nhập 10 giá trị, cách nhau bởi dấu phẩy"
                />
                <button type="submit">Dự báo</button>
            </form>
            {result && <h3>Kết quả dự báo: {JSON.stringify(result)}</h3>}
        </div>
    );
};

export default InputForm;
