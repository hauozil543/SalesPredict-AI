import React from "react";
import { Outlet } from "react-router-dom";
import Header from "../components/Header";
import Footer from "../components/Footer";

const Adminlayout = () => {
  return (
    <div className="flex flex-col min-h-screen bg-white text-gray-800">
      <Header />
      <main className="flex-grow max-w-7xl mx-auto w-full px-4 py-6">
        <Outlet />
      </main>
      <Footer />
    </div>
  );
};

export default Adminlayout;
