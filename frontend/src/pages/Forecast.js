import React from "react";
import InputForm from "../components/InputForm";
import ForecastTable from "../components/ForecastTable";

const Forecast = () => {
    return (
        <div>
            <h1>Dự báo doanh số</h1>
            <InputForm />
            <ForecastTable />
        </div>
    );
};

export default Forecast;
