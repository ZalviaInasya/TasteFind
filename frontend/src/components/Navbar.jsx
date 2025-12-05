import { NavLink } from "react-router-dom";

function Navbar() {
  return (
    <nav className="bg-[#6E4A3E] text-white px-6 py-4 flex items-center justify-between relative">

      {/* LOGO + TEXT */}
      <div className="flex items-center gap-3 pl-4">
        <img
          src="/images/logo.png"
          alt="logo"
          className="w-12 h-12 object-contain select-none ml-1"
        />
        <h1 className="text-2xl font-bold font-serif tracking-wide drop-shadow-md">
          <NavLink to="/">TasteFind</NavLink>
        </h1>
      </div>

      {/* NAV LINKS — TENGAH */}
      <ul className="flex gap-6 text-lg font-semibold tracking-wide font-sans absolute left-1/2 transform -translate-x-1/2">
        <li>
          <NavLink
            to="/"
            className={({ isActive }) =>
              isActive
                ? "border-b-2 border-white pb-1 drop-shadow-[0_0_6px_rgba(255,255,255,0.7)]"
                : "pb-1 hover:border-b-2 hover:border-white transition-all hover:drop-shadow-[0_0_5px_rgba(255,255,255,0.6)]"
            }
          >
            Beranda
          </NavLink>
        </li>
        <li>
          <NavLink
            to="/berita"
            className={({ isActive }) =>
              isActive
                ? "border-b-2 border-white pb-1 drop-shadow-[0_0_6px_rgba(255,255,255,0.7)]"
                : "pb-1 hover:border-b-2 hover:border-white transition-all hover:drop-shadow-[0_0_5px_rgba(255,255,255,0.6)]"
            }
          >
            Berita
          </NavLink>
        </li>
        <li>
          <NavLink
            to="/resep-sehat"
            className={({ isActive }) =>
              isActive
                ? "border-b-2 border-white pb-1 drop-shadow-[0_0_6px_rgba(255,255,255,0.7)]"
                : "pb-1 hover:border-b-2 hover:border-white transition-all hover:drop-shadow-[0_0_5px_rgba(255,255,255,0.6)]"
            }
          >
            Resep Sehat
          </NavLink>
        </li>
        <li>
          <NavLink
            to="/makanan"
            className={({ isActive }) =>
              isActive
                ? "border-b-2 border-white pb-1 drop-shadow-[0_0_6px_rgba(255,255,255,0.7)]"
                : "pb-1 hover:border-b-2 hover:border-white transition-all hover:drop-shadow-[0_0_5px_rgba(255,255,255,0.6)]"
            }
          >
            Makanan
          </NavLink>
        </li>
        <li>
          <NavLink
            to="/minuman"
            className={({ isActive }) =>
              isActive
                ? "border-b-2 border-white pb-1 drop-shadow-[0_0_6px_rgba(255,255,255,0.7)]"
                : "pb-1 hover:border-b-2 hover:border-white transition-all hover:drop-shadow-[0_0_5px_rgba(255,255,255,0.6)]"
            }
          >
            Minuman
          </NavLink>
        </li>
        <li>
          <NavLink
            to="/all"
            className={({ isActive }) =>
              isActive
                ? "border-b-2 border-white pb-1 drop-shadow-[0_0_6px_rgba(255,255,255,0.7)]"
                : "pb-1 hover:border-b-2 hover:border-white transition-all hover:drop-shadow-[0_0_5px_rgba(255,255,255,0.6)]"
            }
          >
            Semua
          </NavLink>
        </li>
      </ul>
    </nav>
  );
}

export default Navbar;