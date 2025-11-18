import React from "react";
import { Link } from "react-router-dom";

export default function Navbar() {
  return (
    <nav className="w-full bg-[#6E4A3E] text-white py-4 shadow-md">
      <div className="max-w-7xl mx-auto flex items-center justify-between px-6">
        <h1 className="text-2xl font-extrabold tracking-wide">TasteFind</h1>

        <ul className="flex gap-8 text-sm font-medium">
          <li><Link to="/berita" className="hover:text-[#DEB3A3]">News</Link></li>
          <li><Link to="/resepsehat" className="hover:text-[#DEB3A3]">Healthy Recipes</Link></li>
          <li><Link to="/makanan" className="hover:text-[#DEB3A3]">Food</Link></li>
          <li><Link to="/minuman" className="hover:text-[#DEB3A3]">Drink</Link></li>
          <li><Link to="/all" className="hover:text-[#DEB3A3]">All</Link></li>
        </ul>

        <button className="px-4 py-2 bg-[#DEB3A3] text-[#6E4A3E] rounded-lg hover:bg-[#cfa293]">
          Search
        </button>
      </div>
    </nav>
  );
}
