import { NavLink } from "react-router-dom";

function Navbar() {
  return (
    <nav className="bg-[#6E4A3E] text-white px-6 py-4 flex items-center justify-between relative">

      {/* LOGO + TEXT */}
      <div className="flex items-center gap-3">
        <img
          src="/images/logo.png"
          alt="logo"
          className="w-10 h-10 object-contain select-none"
        />
        <h1 className="text-2xl font-semibold font-serif">
          <NavLink to="/">TasteFind</NavLink>
        </h1>
      </div>

      {/* NAV LINKS — TENGAH */}
      <ul className="flex gap-6 text-base md:text-lg font-sans absolute left-1/2 transform -translate-x-1/2">
        <li>
          <NavLink
            to="/"
            className={({ isActive }) =>
              isActive
                ? "border-b-2 border-white pb-1"
                : "pb-1 hover:border-b-2 hover:border-white transition-all"
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
                ? "border-b-2 border-white pb-1"
                : "pb-1 hover:border-b-2 hover:border-white transition-all"
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
                ? "border-b-2 border-white pb-1"
                : "pb-1 hover:border-b-2 hover:border-white transition-all"
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
                ? "border-b-2 border-white pb-1"
                : "pb-1 hover:border-b-2 hover:border-white transition-all"
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
                ? "border-b-2 border-white pb-1"
                : "pb-1 hover:border-b-2 hover:border-white transition-all"
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
                ? "border-b-2 border-white pb-1"
                : "pb-1 hover:border-b-2 hover:border-white transition-all"
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