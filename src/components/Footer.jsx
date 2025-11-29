import React from "react";
import { NavLink } from "react-router-dom";
import { FaInstagram, FaYoutube, FaFacebook } from "react-icons/fa";

export default function Footer() {
  return (
    <footer className="w-full bg-[#6E4A3E] text-white py-10 px-6 font-serif">
      
      <div className="max-w-7xl mx-auto grid grid-cols-1 md:grid-cols-3 gap-10">

        {/* QUICK LINKS */}
        <div>
          <h2 className="text-xl font-semibold mb-3">Navigasi</h2>
          <ul className="space-y-2 text-sm opacity-90">
            <li><NavLink to="/" className="hover:underline">Beranda</NavLink></li>
            <li><NavLink to="/berita" className="hover:underline">Berita</NavLink></li>
            <li><NavLink to="/resep-sehat" className="hover:underline">Resep Sehat</NavLink></li>
            <li><NavLink to="/makanan" className="hover:underline">Makanan</NavLink></li>
            <li><NavLink to="/minuman" className="hover:underline">Minuman</NavLink></li>
            <li><NavLink to="/all" className="hover:underline">Semua</NavLink></li>
          </ul>
        </div>

        {/* CONTACT */}
        <div>
          <h2 className="text-xl font-semibold mb-3">Kontak</h2>
          <p className="text-sm opacity-90 leading-6">
            Email: tastefind.team@gmail.com <br />
            Telp: +62 812-3456-7890 <br />
            Lokasi: Banda Aceh, Indonesia
          </p>
        </div>

        {/* SOCIAL MEDIA */}
        <div>
          <h2 className="text-xl font-semibold mb-3">Ikuti Kami</h2>
          <div className="flex items-center gap-5 text-2xl">
            <a href="#" className="hover:opacity-80"><FaInstagram /></a>
            <a href="#" className="hover:opacity-80"><FaYoutube /></a>
            <a href="#" className="hover:opacity-80"><FaFacebook /></a>
          </div>
        </div>
      </div>

      {/* LINE */}
      <div className="border-t border-white/30 mt-10 pt-5 text-center text-sm opacity-90">
        © {new Date().getFullYear()} TasteFind. All rights reserved.
      </div>

    </footer>
  );
}
