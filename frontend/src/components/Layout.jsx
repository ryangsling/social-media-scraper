import React, { useState } from "react";
import { Outlet, NavLink, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import {
  LayoutDashboard, Search, History, LogOut, Menu, X,
  Zap, ChevronRight
} from "lucide-react";

const navItems = [
  { to: "/", icon: LayoutDashboard, label: "Dashboard" },
  { to: "/scrape", icon: Search, label: "New Scrape" },
  { to: "/history", icon: History, label: "History" },
];

export default function Layout() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [open, setOpen] = useState(false);

  const handleLogout = () => { logout(); navigate("/login"); };

  const Sidebar = ({ mobile = false }) => (
    <aside className={`${mobile ? "w-full" : "w-64"} bg-white border-r border-gray-200 flex flex-col h-full`}>
      {/* Logo */}
      <div className="p-6 border-b border-gray-200">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 bg-blue-600 rounded-xl flex items-center justify-center">
            <Zap size={18} className="text-white" />
          </div>
          <div>
            <h1 className="text-blue-900 font-bold text-sm leading-tight">Social Scraper</h1>
            <p className="text-gray-500 text-xs">Intelligence Platform</p>
          </div>
        </div>
      </div>

      {/* Nav */}
      <nav className="flex-1 p-4 space-y-1">
        {navItems.map(({ to, icon: Icon, label }) => (
          <NavLink
            key={to}
            to={to}
            end={to === "/"}
            onClick={() => setOpen(false)}
            className={({ isActive }) =>
              `flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all duration-150 group
              ${isActive
                ? "bg-blue-100 text-blue-700 border border-blue-200"
                : "text-gray-600 hover:text-gray-900 hover:bg-gray-100"
              }`
            }
          >
            <Icon size={17} />
            <span className="flex-1">{label}</span>
            <ChevronRight size={14} className="opacity-0 group-hover:opacity-100 transition-opacity" />
          </NavLink>
        ))}
      </nav>

      {/* User */}
      <div className="p-4 border-t border-gray-200">
        <div className="flex items-center gap-3 px-3 py-2 rounded-lg bg-gray-100 mb-2">
          <div className="w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center text-xs font-bold text-white">
            {user?.username?.[0]?.toUpperCase()}
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-sm font-medium text-gray-800 truncate">{user?.username}</p>
            <p className="text-xs text-gray-500 truncate">{user?.email}</p>
          </div>
        </div>
        <button onClick={handleLogout}
          className="flex items-center gap-2 w-full px-3 py-2 text-sm text-gray-500 hover:text-red-600 hover:bg-red-100 rounded-lg transition-all">
          <LogOut size={15} />
          Logout
        </button>
      </div>
    </aside>
  );

  return (
    <div className="flex h-screen bg-gray-50 overflow-hidden" style={{ fontFamily: "'Plus Jakarta Sans', sans-serif" }}>
      {/* Desktop sidebar */}
      <div className="hidden lg:flex flex-col"><Sidebar /></div>

      {/* Mobile overlay */}
      {open && (
        <div className="lg:hidden fixed inset-0 z-50 flex">
          <div className="w-72"><Sidebar mobile /></div>
          <div className="flex-1 bg-black/60" onClick={() => setOpen(false)} />
        </div>
      )}

      {/* Main */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Mobile header */}
        <header className="lg:hidden flex items-center gap-3 px-4 py-3 bg-white border-b border-gray-200">
          <button onClick={() => setOpen(true)} className="text-gray-500">
            <Menu size={22} />
          </button>
          <span className="text-gray-800 font-semibold text-sm">Social Scraper</span>
        </header>

        <main className="flex-1 overflow-y-auto p-4 lg:p-8">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
