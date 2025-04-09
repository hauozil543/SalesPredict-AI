import React from 'react';
import { Link } from 'react-router-dom';
import logo from '../assets/logo.png';

const Header = () => {
  return (
    <header className="bg-white shadow-md sticky top-0 z-50">
      <div className="max-w-7xl mx-auto flex items-center justify-between px-6 py-4">
        {/* Logo + Tên */}
        <div className="flex items-center gap-3">
            <img src={logo} alt="Logo" className="w-[40px] h-[40px] object-contain" />

            <h1 className="text-2xl font-semibold text-[#2563eb] tracking-wide">RetailForecast</h1>
        </div>

        {/* Menu */}
        <nav className="flex gap-10">
          <Link
            to="/"
            className="text-slate-700 font-medium hover:text-[#2563eb] transition-all hover:underline underline-offset-4"
          >
            Home
          </Link>
          <Link
            to="/history"
            className="text-slate-700 font-medium hover:text-[#2563eb] transition-all hover:underline underline-offset-4"
          >
            History
          </Link>
          <Link
            to="/forecast"
            className="text-slate-700 font-medium hover:text-[#2563eb] transition-all hover:underline underline-offset-4"
          >
            Forecast
          </Link>
        </nav>
      </div>
    </header>
  );
};

export default Header;
