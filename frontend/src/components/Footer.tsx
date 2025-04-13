import React from "react";

const Footer = () => {
  return (
    <footer className="bg-gray-100 border-t mt-10">
      <div className="max-w-7xl mx-auto px-4 py-4 flex justify-between items-center text-sm text-gray-500">
        <span>© 2025 RetailForecast. All rights reserved.</span>
        <div className="space-x-4">
          <a href="#" className="hover:text-blue-500">Privacy</a>
          <a href="#" className="hover:text-blue-500">Terms</a>
          <a href="#" className="hover:text-blue-500">Contact</a>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
