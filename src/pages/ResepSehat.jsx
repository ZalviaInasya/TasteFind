export default function ResepSehat() {
  return (
    <div className="relative w-full h-screen overflow-hidden">

      {/* Background Image */}
      <img
        src="/images/resepsehat.jpg"
        className="w-full h-full object-cover opacity-70"
      />

      {/* DARK LUXURY OVERLAY */}
      <div className="absolute inset-0 bg-gradient-to-b from-black/70 via-black/60 to-black/80"></div>

      {/* CONTENT */}
      <div className="absolute inset-0 flex flex-col items-center justify-center text-center px-6">

        {/* TITLE */}
        <h1
          className="text-4xl md:text-5xl font-semibold text-white drop-shadow-2xl mb-4 opacity-0 animate-fade-in"
          style={{ fontFamily: 'Poppins, serif', animationDelay: "0.2s" }}
        >
          Hidangan <span className="text-[#E9CBA7]">Sehat & Bergizi</span>
        </h1>

        {/* SUBTEXT */}
        <p
          className="text-lg md:text-xl text-white/85 max-w-2xl leading-relaxed mb-10 opacity-0 animate-fade-in"
          style={{ fontFamily: 'Georgia, serif', animationDelay: "0.5s" }}
        >
          Kumpulan resep sehat rendah kalori, penuh nutrisi, dan tetap lezat.  
          <span className="text-[#E9CBA7] font-semibold"> Jadikan hidupmu lebih seimbang.</span>
        </p>

        {/* SEARCH BOX */}
        <div
          className="flex bg-white/90 backdrop-blur-xl rounded-full overflow-hidden shadow-[0_4px_35px_rgba(0,0,0,0.3)] w-full max-w-2xl opacity-0 animate-fade-in-up"
          style={{ animationDelay: "0.8s" }}
        >
          <input
            type="text"
            placeholder="Cari resep sehat..."
            className="px-6 py-3 w-full bg-transparent text-[#2f5734] outline-none text-lg"
            style={{ fontFamily: 'Georgia, serif' }}
          />
          <button
            className="px-8 bg-[#6E4A3E] text-white font-semibold hover:bg-[#234428] transition-all text-lg"
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
