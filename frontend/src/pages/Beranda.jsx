import React, { useState, useEffect, useRef } from "react";

export default function Beranda() {
  const [visibleSections, setVisibleSections] = useState({});
  const sectionsRef = useRef({});

  useEffect(() => {
    const observerOptions = {
      threshold: 0.2,
      rootMargin: "0px 0px -100px 0px"
    };

    const observer = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          setVisibleSections(prev => ({
            ...prev,
            [entry.target.id]: true
          }));
        }
      });
    }, observerOptions);

    Object.values(sectionsRef.current).forEach(ref => {
      if (ref) observer.observe(ref);
    });

    return () => observer.disconnect();
  }, []);

  const scrollToSection = (id) => {
    const element = document.getElementById(id);
    if (element) {
      element.scrollIntoView({ behavior: "smooth" });
    }
  };

  return (
    <div className="w-full font-serif">
      {/* HERO SECTION */}
      <div
        id="hero"
        ref={el => sectionsRef.current.hero = el}
        className={`
          w-full py-20 px-6 md:px-12 relative overflow-hidden bg-cover bg-center
          transition-all duration-1000 ease-out
          ${visibleSections.hero ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-10'}
        `}
        style={{
          backgroundImage: "url('/images/Background.jpg')",
        }}
      >
        {/* OVERLAY TIPIS BIAR TEKS TETAP TERBACA */}
        <div className="absolute inset-0 bg-[#F6ECE0]/85 z-0"></div>

        {/* BLUR DEKORASI */}
        <div className="absolute -top-20 -left-20 w-72 h-72 bg-[#6E4A3E]/20 rounded-full blur-3xl z-10 animate-pulse-slow" />
        <div className="absolute bottom-0 right-0 w-96 h-96 bg-[#8B5E4B]/20 rounded-full blur-3xl z-10 animate-pulse-slow" style={{ animationDelay: '1s' }} />

        <div className="max-w-7xl mx-auto flex flex-col md:flex-row items-center gap-10 relative z-20">
          {/* TEXT KIRI */}
          <div className={`
            flex-1 transition-all duration-1000 ease-out delay-300
            ${visibleSections.hero ? 'opacity-100 translate-x-0' : 'opacity-0 -translate-x-10'}
          `}>
            <h1 className="text-4xl md:text-5xl font-bold leading-tight text-[#2D2A26]">
              Dari <span className="text-[#6E4A3E]">Resep</span> Hingga <span className="text-[#6E4A3E]">Berita</span> Semua Tentang Kuliner Untukmu
            </h1>

            <p className="text-[#6E4A3E] text-lg mt-5 max-w-2xl">
              Temukan berbagai resep sehat, menu organik, dan inspirasi makanan bergizi
              yang disusun untuk mendukung gaya hidup lebih baik dan seimbang.
            </p>

            {/* BADGE FITUR */}
            <div className="flex flex-wrap gap-3 mt-6">
              {["Berita Kuliner","Resep Sehat", "Resep Makanan", "Resep Minuman"].map((item, i) => (
                <span
                  key={i}
                  className={`
                    px-4 py-1 rounded-full bg-[#6E4A3E]/10 text-[#6E4A3E] text-sm font-semibold 
                    hover:bg-[#6E4A3E] hover:text-white transition-all duration-300 cursor-pointer
                    hover:scale-110 hover:shadow-lg
                    ${visibleSections.hero ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-5'}
                  `}
                  style={{ transitionDelay: `${500 + i * 100}ms` }}
                >
                  {item}
                </span>
              ))}
            </div>

            {/* BUTTON */}
            <button
              onClick={() => scrollToSection("tentang-kami")}
              className="
                mt-8 px-8 py-3 rounded-full font-semibold tracking-wide
                bg-gradient-to-r from-[#6E4A3E] via-[#8B5E4B] to-[#6E4A3E]
                text-white shadow-lg shadow-[#6E4A3E]/40
                hover:scale-110 hover:shadow-[#6E4A3E]/70
                active:scale-95
                transition-all duration-300
                relative overflow-hidden
              "
            >
              Tentang Kami
              <span className="absolute inset-0 bg-white/20 translate-x-[-100%] hover:translate-x-[100%] transition duration-500" />
            </button>

            {/* STATISTIK */}
            <div className="flex gap-8 mt-8 text-[#6E4A3E]">
              {[
                { value: "120+", label: "Resep" },
                { value: "50+", label: "Artikel" },
                { value: "100+", label: "BeritaKuliner" }
              ].map((stat, i) => (
                <div 
                  key={i}
                  className={`
                    transition-all duration-700 ease-out
                    ${visibleSections.hero ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-10'}
                  `}
                  style={{ transitionDelay: `${900 + i * 150}ms` }}
                >
                  <p className="text-2xl font-bold">{stat.value}</p>
                  <p className="text-sm">{stat.label}</p>
                </div>
              ))}
            </div>
          </div>

          {/* GAMBAR KANAN */}
          <div className={`
            flex-1 flex justify-center relative
            transition-all duration-1000 ease-out delay-500
            ${visibleSections.hero ? 'opacity-100 translate-x-0 scale-100' : 'opacity-0 translate-x-10 scale-90'}
          `}>
            <div className="absolute inset-0 flex justify-center items-center pointer-events-none"></div>
            <img
              src="/images/beranda.png"
              alt="beranda"
              className="
                relative z-10
                w-[95%] md:w-[90%]
                max-w-none
                animate-slow-spin
                select-none
                pointer-events-none
                left-8 md:left-16
              "
            />
          </div>
        </div>
      </div>

      {/* TENTANG KAMI */}
      <div 
        id="tentang-kami" 
        ref={el => sectionsRef.current['tentang-kami'] = el}
        className="w-full bg-[#3B241A] py-20"
      >
        <div className="max-w-7xl mx-auto flex flex-col md:flex-row items-center px-6 md:px-10 gap-6">
          <div className={`
            flex-1 flex justify-start relative
            transition-all duration-1000 ease-out
            ${visibleSections['tentang-kami'] ? 'opacity-100 translate-x-0 scale-100' : 'opacity-0 -translate-x-20 scale-90'}
          `}>
            {/* SINAR PUTIH DI KIRI PIRING */}
            <div className="absolute left-0 top-1/2 -translate-y-1/2 w-[300px] h-[300px] bg-white/40 blur-[120px] rounded-full z-0 animate-pulse-slow"></div>
            <div className="absolute inset-0 flex justify-start items-center pointer-events-none"></div>
            <img
              src="/images/beranda.png"
              alt="tentang-kami"
              className="
                relative z-10 
                w-[95%] md:w-[90%] 
                max-w-2xl md:max-w-3xl
                -ml-16 md:-ml-24
                animate-slow-spin 
                select-none pointer-events-none
              "
            />
          </div>

          <div className="flex-1 text-center md:text-left">
            <h2 className={`
              text-[#F3D9B1] text-4xl md:text-5xl font-bold mb-5
              transition-all duration-1000 ease-out delay-200
              ${visibleSections['tentang-kami'] ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-10'}
            `}>
              Tentang Kami
            </h2>

            <p className={`
              text-[#E6C9A8] text-lg md:text-xl leading-relaxed mb-4
              transition-all duration-1000 ease-out delay-400
              ${visibleSections['tentang-kami'] ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-10'}
            `}>
              TasteFind adalah platform mesin pencari kuliner yang menghadirkan berbagai informasi seputar resep makanan, 
              minuman, resep sehat, serta berita kuliner terkini.
            </p>
            <p className={`
              text-[#E6C9A8] text-lg md:text-xl leading-relaxed
              transition-all duration-1000 ease-out delay-600
              ${visibleSections['tentang-kami'] ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-10'}
            `}>
              Melalui Tastefind, pengguna dapat dengan mudah menemukan 
              inspirasi memasak, referensi gaya hidup sehat, hingga mengikuti perkembangan dunia kuliner dalam satu tempat 
              yang praktis dan terpercaya.
            </p>

            {/* BUTTON SELANJUTNYA */}
            <button
              onClick={() => scrollToSection("anggota-kelompok")}
              className={`
                group relative inline-flex items-center gap-3 mt-8
                px-8 py-4 rounded-full font-semibold tracking-wide
                bg-gradient-to-r from-[#F3D9B1] via-[#E6C9A8] to-[#F3D9B1]
                text-[#3B241A] shadow-xl shadow-[#F3D9B1]/30
                hover:shadow-2xl hover:shadow-[#F3D9B1]/50
                hover:scale-105 active:scale-95
                transition-all duration-300
                overflow-hidden
                ${visibleSections['tentang-kami'] ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-10'}
              `}
              style={{ transitionDelay: '800ms' }}
            >
              <span className="relative z-10 text-lg">Selanjutnya</span>
              <svg 
                className="relative z-10 w-6 h-6 group-hover:translate-x-2 transition-transform duration-300" 
                fill="none" 
                stroke="currentColor" 
                viewBox="0 0 24 24"
              >
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M13 7l5 5m0 0l-5 5m5-5H6" />
              </svg>
              <span className="absolute inset-0 bg-white/30 translate-x-[-100%] group-hover:translate-x-[100%] transition-transform duration-700" />
              
              {/* RING EFFECT */}
              <span className="absolute inset-0 rounded-full border-2 border-[#F3D9B1] opacity-0 group-hover:opacity-100 group-hover:scale-110 transition-all duration-500"></span>
            </button>
          </div>
        </div>
      </div>

      {/* ANGGOTA KELOMPOK */}
      <section
        id="anggota-kelompok"
        ref={el => sectionsRef.current['anggota-kelompok'] = el}
        className="
          w-full py-20 px-4 flex flex-col items-center
          bg-[url('/images/anggota.png')]
          bg-cover bg-center bg-no-repeat relative
        "
      >
        {/* OVERLAY AGAR TEKS JELAS */}
        <div className="absolute inset-0 bg-[#DCCDBA]/70 backdrop-blur-sm"></div>

        <div className="relative flex flex-col items-center w-full">
          {/* TITLE */}
          <h2 className={`
            text-4xl font-bold mb-4 text-[#6E4A3E] tracking-wide text-center
            transition-all duration-1000 ease-out
            ${visibleSections['anggota-kelompok'] ? 'opacity-100 translate-y-0 scale-100' : 'opacity-0 -translate-y-10 scale-95'}
          `}>
            Anggota Kelompok
          </h2>

          {/* SUBTITLE */}
          <p className={`
            text-[#6E4A3E]/80 text-center max-w-2xl mb-12 text-lg
            transition-all duration-1000 ease-out delay-200
            ${visibleSections['anggota-kelompok'] ? 'opacity-100 translate-y-0' : 'opacity-0 -translate-y-10'}
          `}>
            Berikut adalah anggota kelompok yang berkontribusi dalam pengembangan
            dan perancangan proyek <span className="font-semibold">TasteFind</span>.
          </p>

          {/* CARD GRID */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-10 w-full max-w-5xl">
            {[
              { nama: "Cut Renatha Fadhilah", foto: "/images/renatha.jpeg" },
              { nama: "Zalvia Inasya Zulna", foto: "/images/nasya.jpeg" },
              { nama: "Nadia Maghdalena", foto: "/images/nadia.jpeg" },
            ].map((anggota, i) => (
              <div
                key={i}
                className={`
                  relative p-6 rounded-2xl shadow-lg flex flex-col items-center 
                  bg-[#E4D3C4]/90 backdrop-blur-sm
                  hover:scale-[1.08] hover:shadow-2xl hover:-translate-y-2
                  transition-all duration-500
                  border border-[#BFA895]
                  animate-[float_4s_ease-in-out_infinite]
                  ${visibleSections['anggota-kelompok'] ? 'opacity-100 translate-y-0 scale-100' : 'opacity-0 translate-y-20 scale-90'}
                `}
                style={{ 
                  transitionDelay: `${400 + i * 200}ms`,
                  animationDelay: `${i * 0.3}s`
                }}
              >
                {/* GLOW BACKGROUND */}
                <div className="
                  absolute inset-0 rounded-2xl
                  bg-gradient-to-b from-[#C8B4A3] to-[#E6D5C8]
                  blur-2xl opacity-60
                  -z-10 group-hover:opacity-80 transition-opacity duration-500
                "></div>

                {/* IMAGE */}
                <div className="relative overflow-hidden rounded-2xl mb-4">
                  <img
                    src={anggota.foto}
                    className="w-48 h-48 object-cover rounded-2xl shadow-lg transition-transform duration-500 hover:scale-110"
                    alt={anggota.nama}
                  />
                  <div className="absolute inset-0 bg-gradient-to-t from-[#5A3D33]/50 to-transparent opacity-0 hover:opacity-100 transition-opacity duration-300 rounded-2xl"></div>
                </div>

                {/* NAME */}
                <h3 className="text-xl font-semibold text-[#5A3D33] text-center">
                  {anggota.nama}
                </h3>
              </div>
            ))}
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
        
        @keyframes pulse-slow {
          0%, 100% { opacity: 0.6; }
          50% { opacity: 0.9; }
        }
        .animate-pulse-slow {
          animation: pulse-slow 4s ease-in-out infinite;
        }
        
        @keyframes float {
          0%, 100% { transform: translateY(0px); }
          50% { transform: translateY(-10px); }
        }
      `}</style>
    </div>
  );
}