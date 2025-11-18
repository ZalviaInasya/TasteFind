export default function Beranda() {
  return (
    <div className="relative w-full h-screen">
      {/* Background gambar */}
      <img
        src="/images/hookberanda.jpg"
        className="w-full h-full object-cover opacity-80"
      />

      {/* Overlay gelap */}
      <div className="absolute inset-0 bg-black/40"></div>

      {/* Isi teks */}
      <div className="absolute inset-0 flex flex-col items-center justify-center text-center px-6">
        <h1 className="text-4xl md:text-5xl font-bold text-cream2 drop-shadow-lg mb-6">
          Temukan artikel berbagai resep dan berita tentang kuliner
        </h1>

        <div className="flex mt-4 bg-cream2 rounded-xl overflow-hidden shadow-xl">
          <input
            type="text"
            placeholder="Cari resep, berita, atau makanan..."
            className="px-4 py-3 w-64 md:w-96 bg-cream2 text-brown outline-none"
          />
          <button className="px-6 bg-brown text-cream1 font-semibold hover:bg-[#5b3d33]">
            Cari
          </button>
        </div>
      </div>
    </div>
  );
}
