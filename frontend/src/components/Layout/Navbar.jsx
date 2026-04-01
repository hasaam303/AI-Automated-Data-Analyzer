import { Link, useLocation } from "react-router-dom";
import { BarChart3, Clock, Zap } from "lucide-react";
import clsx from "clsx";

const links = [
  { to: "/", label: "Analyze", icon: Zap },
  { to: "/history", label: "History", icon: Clock },
];

export default function Navbar() {
  const { pathname } = useLocation();

  return (
    <nav className="border-b border-surface-border bg-surface-card/50 backdrop-blur-sm sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-6 flex items-center h-14 gap-8">
        {/* Logo */}
        <Link to="/" className="flex items-center gap-2 font-semibold text-slate-100">
          <BarChart3 className="w-5 h-5 text-brand" />
          <span>AI Data Analyst</span>
        </Link>

        {/* Nav links */}
        <div className="flex items-center gap-1 ml-2">
          {links.map(({ to, label, icon: Icon }) => (
            <Link
              key={to}
              to={to}
              className={clsx(
                "flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-sm font-medium",
                pathname === to
                  ? "bg-brand/10 text-brand-light"
                  : "text-slate-400 hover:text-slate-200 hover:bg-surface-hover"
              )}
            >
              <Icon className="w-4 h-4" />
              {label}
            </Link>
          ))}
        </div>

        <div className="ml-auto">
          <span className="badge bg-brand/10 text-brand-light border border-brand/20">
            Powered by GPT-4o
          </span>
        </div>
      </div>
    </nav>
  );
}
