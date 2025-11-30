export default function All() {
  return (
    <div className="relative w-full h-screen overflow-hidden">

      {/* Background Image */}
      <img
        src="/images/all.jpg"
        className="w-full h-full object-cover opacity-70"
      />

      {/* DARK LUXURY OVERLAY */}
      <div className="absolute inset-0 bg-gradient-to-b from-black/75 via-black/60 to-black/85"></div>

      {/* CONTENT */}
      <div className="absolute inset-0 flex flex-col items-center justify-center text-center px-6">

        {/* TITLE */}
        <h1
          className="text-4xl md:text-5xl font-semibold text-white drop-shadow-2xl mb-4 opacity-0 animate-fade-in"
          style={{ fontFamily: 'Poppins, serif', animationDelay: "0.2s" }}
        >
          Semua <span className="text-[#E4C590]">Konten Kuliner</span> Dalam Satu Tempat
        </h1>

        {/* SUBTEXT */}
        <p
          className="text-lg md:text-xl text-white/85 max-w-2xl leading-relaxed mb-10 opacity-0 animate-fade-in"
          style={{ fontFamily: 'Georgia, serif', animationDelay: "0.5s" }}
        >
          Dari resep makanan, minuman, hidangan sehat, hingga berita kuliner terbaru.  
          <span className="text-[#F1D8AA] font-semibold"> Jelajahi semuanya dengan mudah.</span>
        </p>

        {/* SEARCH BOX */}
        <div
          className="flex bg-white/90 backdrop-blur-xl rounded-full overflow-hidden shadow-[0_4px_35px_rgba(0,0,0,0.3)] w-full max-w-2xl opacity-0 animate-fade-in-up"
          style={{ animationDelay: "0.8s" }}
        >
          <input
            type="text"
            placeholder="Cari semua konten kuliner..."
            className="px-6 py-3 w-full bg-transparent text-[#6E4A3E] outline-none text-lg"
            style={{ fontFamily: 'Georgia, serif' }}
          />
          <button
            className="px-8 bg-[#6E4A3E] text-white font-semibold hover:bg-[#5b3d33] transition-all text-lg"
            style={{ fontFamily: 'Poppins, serif' }}
          >
            Cari
          </button>
        </div>
      </div>

      {/* ANIMATION */}
      <style>
        {`
          @keyframes fade-in {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
          }
          @keyframes fade-in-up {
            from { opacity: 0; transform: translateY(25px); }
            to { opacity: 1; transform: translateY(0); }
          }
          .animate-fade-in {
            animation: fade-in 0.8s forwards ease-out;
          }
          .animate-fade-in-up {
            animation: fade-in-up 0.9s forwards ease-out;
          }
        `}
      </style>
    </div>
  );
}
