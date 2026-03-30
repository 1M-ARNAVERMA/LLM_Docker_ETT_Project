import { Link, useLocation } from "wouter";
import { MessageSquare, FileText, Database, Terminal } from "lucide-react";
import { cn } from "@/lib/utils";

export function Navigation() {
  const [location] = useLocation();

  const links = [
    { href: "/", label: "Chat", icon: MessageSquare },
    { href: "/documents", label: "Documents", icon: FileText },
  ];

  return (
    <nav className="fixed left-0 top-0 bottom-0 w-20 md:w-64 border-r border-white/5 bg-card/30 backdrop-blur-md flex flex-col py-6 z-50">
      <div className="px-6 mb-10 flex items-center gap-3">
        <div className="w-10 h-10 rounded-xl bg-primary/20 flex items-center justify-center text-primary shadow-[0_0_15px_rgba(var(--primary),0.3)]">
          <Database className="w-6 h-6" />
        </div>
        <span className="hidden md:block font-display font-bold text-xl tracking-tight">
          DocMind
          <span className="text-primary">.ai</span>
        </span>
      </div>

      <div className="flex-1 px-3 space-y-2">
        {links.map((link) => {
          const Icon = link.icon;
          const isActive = location === link.href;
          return (
            <Link
              key={link.href}
              href={link.href}
              className={cn(
                "flex items-center gap-3 px-3 md:px-4 py-3 rounded-xl transition-all duration-300 group relative overflow-hidden",
                isActive 
                  ? "bg-primary/10 text-primary shadow-[0_0_20px_rgba(var(--primary),0.15)] border border-primary/20" 
                  : "text-muted-foreground hover:text-foreground hover:bg-white/5"
              )}
            >
              <Icon className={cn("w-5 h-5 transition-transform group-hover:scale-110", isActive && "animate-pulse")} />
              <span className="hidden md:block font-medium">{link.label}</span>
              
              {isActive && (
                <div className="absolute left-0 top-1/2 -translate-y-1/2 w-1 h-8 bg-primary rounded-r-full shadow-[0_0_10px_var(--primary)]" />
              )}
            </Link>
          );
        })}
      </div>

      <div className="px-6 mt-auto">
        <div className="hidden md:flex items-center gap-3 p-4 rounded-xl bg-white/5 border border-white/5">
          <Terminal className="w-5 h-5 text-muted-foreground" />
          <div className="flex flex-col">
            <span className="text-xs font-mono text-muted-foreground">Status</span>
            <span className="text-xs font-semibold text-green-400 flex items-center gap-1.5">
              <span className="w-1.5 h-1.5 rounded-full bg-green-400 animate-pulse" />
              Online
            </span>
          </div>
        </div>
      </div>
    </nav>
  );
}
