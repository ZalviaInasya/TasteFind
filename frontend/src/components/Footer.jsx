import React from "react";
import { NavLink } from "react-router-dom";
import { FaInstagram, FaYoutube, FaFacebook } from "react-icons/fa";

export default function Footer() {
  const scrollTop = () => {
    window.scrollTo({ top: 0, behavior: "smooth" });
  };

  return (
    <footer className="w-full bg-[#6E4A3E] text-white py-6 px-6 font-serif">

      <div className="max-w-6xl mx-auto flex flex-col md:flex-row justify-between items-start md:items-center gap-10">

        {/* LOGO + TITLE */}
        <div className="flex items-center gap-4">
          <img
            src="/images/logo.png"
            alt="Logo"
            className="w-12 h-12 scale-150 object-contain rounded-md"
          />
          <h1 className="text-2xl font-semibold tracking-wide">
            TasteFind
          </h1>
        </div>
        
        {/* QUICK LINKS */}
        <div>
          <h2 className="text-lg font-semibold mb-2">Navigasi</h2>
          <ul className="space-y-1 text-sm opacity-90">
            <li><NavLink to="/" onClick={scrollTop} className="hover:underline">Beranda</NavLink></li>
            <li><NavLink to="/berita" onClick={scrollTop} className="hover:underline">Berita</NavLink></li>
            <li><NavLink to="/resep-sehat" onClick={scrollTop} className="hover:underline">Resep Sehat</NavLink></li>
            <li><NavLink to="/makanan" onClick={scrollTop} className="hover:underline">Makanan</NavLink></li>
            <li><NavLink to="/minuman" onClick={scrollTop} className="hover:underline">Minuman</NavLink></li>
            <li><NavLink to="/all" onClick={scrollTop} className="hover:underline">Semua</NavLink></li>
          </ul>
        </div>

        {/* CONTACT */}
        <div>
          <h2 className="text-lg font-semibold mb-2">Kontak</h2>
          <p className="text-sm opacity-90 leading-6">
            Email: tastefind.team@gmail.com <br />
            Telp: +62 812-3456-7890 <br />
            Lokasi: Banda Aceh, Indonesia
          </p>
        </div>

        {/* SOCIAL MEDIA */}
        <div>
          <h2 className="text-lg font-semibold mb-2">Ikuti Kami</h2>
          <div className="flex items-center gap-4 text-xl">
            <a href="#" className="hover:opacity-80"><FaInstagram /></a>
            <a href="#" className="hover:opacity-80"><FaYoutube /></a>
            <a href="#" className="hover:opacity-80"><FaFacebook /></a>
          </div>
        </div>
      </div>

      {/* LINE */}
      <div className="border-t border-white/30 mt-6 pt-4 text-center text-sm opacity-80">
        © {new Date().getFullYear()} TasteFind. All rights reserved.
      </div>

    </footer>
  );
}
