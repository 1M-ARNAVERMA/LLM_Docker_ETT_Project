import { cn } from "@/lib/utils";
import { Message } from "@shared/schema";
import { Bot, User, Copy, Check } from "lucide-react";
import { useState } from "react";
import { format } from "date-fns";

interface ChatMessageProps {
  message: Message;
}

export function ChatMessage({ message }: ChatMessageProps) {
  const isBot = message.role === "assistant";
  const [copied, setCopied] = useState(false);

  const copyToClipboard = () => {
    navigator.clipboard.writeText(message.content);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div
      className={cn(
        "flex w-full gap-4 md:gap-6 p-4 md:p-6 transition-colors duration-300",
        isBot ? "bg-white/[0.02]" : "bg-transparent"
      )}
    >
      <div className={cn(
        "w-8 h-8 md:w-10 md:h-10 rounded-xl flex items-center justify-center shrink-0 shadow-lg",
        isBot 
          ? "bg-primary/20 text-primary border border-primary/20 shadow-[0_0_15px_rgba(var(--primary),0.2)]" 
          : "bg-secondary text-secondary-foreground border border-white/5"
      )}>
        {isBot ? <Bot className="w-5 h-5 md:w-6 md:h-6" /> : <User className="w-5 h-5 md:w-6 md:h-6" />}
      </div>

      <div className="flex-1 min-w-0 space-y-2">
        <div className="flex items-center justify-between">
          <span className="text-sm font-medium font-display tracking-wide opacity-80">
            {isBot ? "AI Assistant" : "You"}
          </span>
          <div className="flex items-center gap-3">
            <span className="text-xs font-mono text-muted-foreground opacity-50">
              {message.createdAt && format(new Date(message.createdAt), "HH:mm")}
            </span>
            {isBot && (
              <button
                onClick={copyToClipboard}
                className="text-muted-foreground hover:text-foreground transition-colors p-1"
                title="Copy response"
              >
                {copied ? <Check className="w-3.5 h-3.5" /> : <Copy className="w-3.5 h-3.5" />}
              </button>
            )}
          </div>
        </div>
        
        <div className={cn(
          "prose prose-invert max-w-none text-sm md:text-base leading-relaxed break-words",
          isBot ? "text-slate-300" : "text-white"
        )}>
          {message.content}
        </div>
      </div>
    </div>
  );
}
