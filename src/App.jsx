import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Navbar from "./components/Navbar";
import Footer from "./components/Footer";

import Beranda from "./pages/Beranda";
import All from "./pages/All";
import Berita from "./pages/Berita";
import Makanan from "./pages/Makanan";
import Minuman from "./pages/Minuman";
import ResepSehat from "./pages/ResepSehat";

export default function App() {
  return (
    <Router>
      <div className="bg-[#E4DBCA] min-h-screen flex flex-col">
        <Navbar />

        <div className="flex-grow">
          <Routes>
            <Route path="/" element={<Beranda />} />
            <Route path="/beranda" element={<Beranda />} />
            <Route path="/all" element={<All />} />
            <Route path="/berita" element={<Berita />} />
            <Route path="/makanan" element={<Makanan />} />
            <Route path="/minuman" element={<Minuman />} />

            {/* Tambahan: path baru biar /resep-sehat tidak error */}
            <Route path="/resep-sehat" element={<ResepSehat />} />
          </Routes>
        </div>

        <Footer />
      </div>
    </Router>
  );
}
