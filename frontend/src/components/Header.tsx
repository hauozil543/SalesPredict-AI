import React from "react";
import { Link } from "react-router-dom";

const Header = () => {
  return (
    <header className="font-sans bg-white shadow-md sticky top-0 z-50">
      <div className="max-w-7xl mx-auto flex items-center justify-between px-6 py-4">
        <div className="flex items-center gap-3">
          <img src="/src/assets/logo.png" alt="Logo" className="h-10 w-[40px] h-[40px] object-contain" />
          <h1 className="text-xl md:text-2xl font-bold text-[#007bff]">RetailForecast</h1>
        </div>
        <nav className="flex space-x-8">
          {/* Mỗi mục menu được bọc trong một ô với hiệu ứng hover */}
          <Link
            to="/"
            className="text-slate-700 font-medium text-[15px] hover:text-[#007bff] transition"
          >
            Home
          </Link>
          <Link
            to="/history"
            className="text-slate-700 font-medium text-[15px] hover:text-[#007bff] transition"
          >
            History
          </Link>
          <Link
            to="/forecast"
            className="text-slate-700 font-medium text-[15px] hover:text-[#007bff] transition"
          >
            Forecast
          </Link>
        </nav>

      </div>
    </header>
  );
};


export default Header;
