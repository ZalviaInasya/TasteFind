import React from "react";

export default function Beranda() {
  return (
    <div className="w-full font-serif">

      {/* BAGIAN ATAS — BERANDA */}
      <div className="w-full bg-[#F6ECE0] pt-6 pb-8">
        <div className="max-w-7xl mx-auto flex flex-col md:flex-row items-center px-6 md:px-10 gap-8">

          {/* TEKS KIRI */}
          <div className="flex-1">
            <h1 className="text-[#6E4A3E] text-[30px] md:text-[40px] font-semibold leading-tight">
              Temukan artikel berbagai resep dan berita tentang kuliner
            </h1>

            <button
              onClick={() => {
                const about = document.getElementById("tentang-kami");
                if (about) about.scrollIntoView({ behavior: "smooth" });
              }}
              className="mt-4 px-7 py-3 bg-[#6E4A3E] text-white font-medium rounded-md shadow-md hover:bg-[#5c3f35] transition-all"
            >
              Tentang Kami
            </button>
          </div>

          {/* GAMBAR KANAN — BERANDA */}
          <div className="flex-1 flex justify-center">
            <img
              src="/images/beranda.png"
              alt="beranda"
              className="w-[70%] md:w-[60%] max-w-md md:max-w-lg animate-slow-spin select-none pointer-events-none"
              style={{
                background: "transparent",
                border: "none",
                boxShadow: "none",
              }}
            />
          </div>
        </div>
      </div>

      {/* TENTANG KAMI — MIRIP BERANDA, POSISI DIBALIK */}
      <div
        id="tentang-kami"
        className="max-w-7xl mx-auto flex flex-col md:flex-row items-center px-6 md:px-10 gap-6 mt-6"
      >
        {/* GAMBAR KIRI */}
        <div className="flex-1 flex justify-center">
          <img
            src="/images/beranda.png"
            alt="tentang-kami"
            className="w-[70%] md:w-[60%] max-w-md md:max-w-lg animate-slow-spin select-none pointer-events-none"
            style={{
              background: "transparent",
              border: "none",
              boxShadow: "none",
            }}
          />
        </div>

        {/* TEKS KANAN */}
        <div className="flex-1 text-center md:text-left">
          <h2 className="text-[#6E4A3E] text-3xl md:text-4xl font-semibold mb-4">
            Tentang Kami
          </h2>
          <p className="text-[#6E4A3E] text-lg leading-relaxed font-sans">
            TasteFind adalah platform yang menyediakan berbagai artikel seputar
            resep makanan, minuman, dan berita kuliner terbaru. Kami membantu
            pengguna menemukan inspirasi hidangan yang sehat, lezat, dan mudah
            dibuat.
          </p>
        </div>
      </div>

      {/* ANIMASI PUTAR */}
      <style>{`
        @keyframes slow-spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(10deg); }
        }

        .animate-slow-spin {
          animation: slow-spin 4s ease-in-out infinite alternate;
        }
      `}</style>
    </div>
  );
}
