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

          {/* GAMBAR KANAN */}
          <div className="flex-1 flex justify-center relative">

            <div className="absolute inset-0 flex justify-center items-center pointer-events-none">
              <img
                src="/images/bg.png"
                style={{
                  width: "1200px",
                  opacity: 0.99,
                  zIndex: 0
                }}
              />
            </div>

            <img
              src="/images/beranda.png"
              alt="beranda"
              className="relative z-10 w-[70%] md:w-[60%] max-w-md md:max-w-lg animate-slow-spin select-none pointer-events-none"
              style={{
                background: "transparent",
                border: "none",
                boxShadow: "none",
              }}
            />
          </div>
        </div>
      </div>

      {/* TENTANG KAMI */}
      <div
        id="tentang-kami"
        className="w-full bg-[#EDE4D1] py-20"
      >
        <div className="max-w-7xl mx-auto flex flex-col md:flex-row items-center px-6 md:px-10 gap-6">

          <div className="flex-1 flex justify-center relative">
            {/* BG belakang piring */}
            <div className="absolute inset-0 flex justify-center items-center pointer-events-none">
              <img
                src="/images/bg.png"
                style={{ width: "1200px", opacity: 0.99, zIndex: 0 }}
              />
            </div>

            <img
              src="/images/beranda.png"
              alt="tentang-kami"
              className="relative z-10 w-[70%] md:w-[60%] max-w-md md:max-w-lg animate-slow-spin select-none pointer-events-none"
              style={{
                background: "transparent",
                border: "none",
                boxShadow: "none",
              }}
            />
          </div>

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

        {/* BUTTON SEE MORE */}
        <div className="w-full flex justify-center mt-10">
          <button
            onClick={() =>
              document.getElementById("anggota-kelompok").scrollIntoView({
                behavior: "smooth",
              })
            }
            className="flex items-center gap-2 bg-[#6E4A3E] text-white px-6 py-3 rounded-lg shadow hover:bg-[#5a3d32] transition"
          >
            See More
            <span className="text-xl">↓</span>
          </button>
        </div>
      </div>

      {/* ANGGOTA KELOMPOK */}
      <section
        id="anggota-kelompok"
        className="min-h-screen w-full bg-[#DCCDBA] py-20 px-6 flex flex-col items-center"
      >
        <h2 className="text-4xl font-bold mb-12 text-[#6E4A3E] tracking-wide">
          Anggota Kelompok
        </h2>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-10 w-full max-w-6xl">

          <div className="bg-[#F6ECE0] p-6 rounded-2xl shadow-lg flex flex-col items-center hover:scale-105 transition">
            <img
              src="/images/nasya.jpeg"
              className="w-56 h-56 object-cover rounded-2xl mb-4 shadow"
              alt="anggota1"
            />
            <h3 className="text-xl font-semibold text-[#6E4A3E] mb-2">
              Cut Renatha Fadhilah
            </h3>
          </div>

          <div className="bg-[#F6ECE0] p-6 rounded-2xl shadow-lg flex flex-col items-center hover:scale-105 transition">
            <img
              src="/images/nasya.jpeg"
              className="w-56 h-56 object-cover rounded-2xl mb-4 shadow"
              alt="anggota2"
            />
            <h3 className="text-xl font-semibold text-[#6E4A3E] mb-2">
              Zalvia Inasya Zulna
            </h3>
          </div>

          <div className="bg-[#F6ECE0] p-6 rounded-2xl shadow-lg flex flex-col items-center hover:scale-105 transition">
            <img
              src="/images/nasya.jpeg"
              className="w-56 h-56 object-cover rounded-2xl mb-4 shadow"
              alt="anggota3"
            />
            <h3 className="text-xl font-semibold text-[#6E4A3E] mb-2">
              Nadia Maghdalena
            </h3>
          </div>
        </div>
      </section>

      {/* ANIMASI */}
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