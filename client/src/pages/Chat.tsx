import { useRef, useEffect } from "react";
import { Navigation } from "@/components/Navigation";
import { ChatMessage } from "@/components/ChatMessage";
import { useChatHistory, useSendMessage, useClearChat } from "@/hooks/use-chat";
import { Send, Loader2, Sparkles, Trash2 } from "lucide-react";
import { cn } from "@/lib/utils";
import { useForm } from "react-hook-form";
import { z } from "zod";
import { zodResolver } from "@hookform/resolvers/zod";
import { useToast } from "@/hooks/use-toast";

const messageSchema = z.object({
  message: z.string().min(1),
});

type MessageForm = z.infer<typeof messageSchema>;

export default function Chat() {
  const scrollRef = useRef<HTMLDivElement>(null);
  const { data: messages, isLoading } = useChatHistory();
  const { mutate: sendMessage, isPending } = useSendMessage();
  const { mutate: clearChat, isPending: isClearing } = useClearChat();
  const { toast } = useToast();

  const { register, handleSubmit, reset } = useForm<MessageForm>({
    resolver: zodResolver(messageSchema),
  });

  // Auto-scroll to bottom
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollIntoView({ behavior: "smooth" });
    }
  }, [messages, isPending]);

  const onSubmit = (data: MessageForm) => {
    sendMessage(data.message, {
      onSuccess: () => reset(),
      onError: (error) => {
        toast({
          title: "Error sending message",
          description: error.message,
          variant: "destructive",
        });
      },
    });
  };

  const handleClear = () => {
    if (confirm("Are you sure you want to clear the chat history?")) {
      clearChat();
    }
  };

  return (
    <div className="flex h-screen bg-background text-foreground overflow-hidden">
      <Navigation />
      
      <main className="flex-1 flex flex-col ml-20 md:ml-64 relative">
        {/* Header */}
        <header className="flex-none h-16 md:h-20 border-b border-white/5 bg-background/50 backdrop-blur-md flex items-center justify-between px-6 z-10 sticky top-0">
          <div className="flex items-center gap-3">
            <Sparkles className="w-5 h-5 text-primary" />
            <h2 className="font-display font-bold text-lg tracking-tight">AI Assistant</h2>
          </div>
          <button
            onClick={handleClear}
            disabled={isClearing || !messages?.length}
            className="p-2 text-muted-foreground hover:text-destructive hover:bg-destructive/10 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            title="Clear History"
          >
            <Trash2 className="w-5 h-5" />
          </button>
        </header>

        {/* Messages Area */}
        <div className="flex-1 overflow-y-auto custom-scrollbar scroll-smooth">
          <div className="max-w-4xl mx-auto w-full pb-32 pt-8">
            {isLoading ? (
              <div className="flex flex-col items-center justify-center py-20 opacity-50">
                <Loader2 className="w-10 h-10 animate-spin mb-4" />
                <p>Loading conversation...</p>
              </div>
            ) : messages?.length === 0 ? (
              <div className="flex flex-col items-center justify-center py-20 px-6 text-center space-y-6">
                <div className="w-20 h-20 rounded-2xl bg-gradient-to-br from-primary/20 to-purple-500/20 flex items-center justify-center shadow-[0_0_40px_rgba(var(--primary),0.1)] mb-4">
                  <Sparkles className="w-10 h-10 text-primary" />
                </div>
                <div className="space-y-2 max-w-md">
                  <h3 className="text-2xl font-bold font-display">How can I help you?</h3>
                  <p className="text-muted-foreground leading-relaxed">
                    I can answer questions based on the documents you've uploaded. Try asking about specific details in your PDFs.
                  </p>
                </div>
              </div>
            ) : (
              <div className="flex flex-col">
                {messages?.map((msg) => (
                  <ChatMessage key={msg.id} message={msg} />
                ))}
                
                {isPending && (
                  <div className="p-6">
                    <div className="flex gap-4 md:gap-6 animate-pulse">
                      <div className="w-8 h-8 md:w-10 md:h-10 rounded-xl bg-primary/20 border border-primary/20 flex items-center justify-center">
                        <Loader2 className="w-5 h-5 text-primary animate-spin" />
                      </div>
                      <div className="space-y-3 pt-2">
                        <div className="h-2 w-24 bg-white/10 rounded-full" />
                        <div className="h-2 w-64 bg-white/10 rounded-full" />
                      </div>
                    </div>
                  </div>
                )}
                
                <div ref={scrollRef} />
              </div>
            )}
          </div>
        </div>

        {/* Input Area */}
        <div className="flex-none p-6 bg-gradient-to-t from-background via-background to-transparent absolute bottom-0 left-0 right-0 z-20">
          <div className="max-w-4xl mx-auto">
            <form 
              onSubmit={handleSubmit(onSubmit)}
              className="relative group"
            >
              <div className="absolute inset-0 bg-gradient-to-r from-primary/20 to-purple-500/20 rounded-2xl blur-xl opacity-0 group-focus-within:opacity-100 transition-opacity duration-500" />
              
              <div className="relative flex items-center bg-card/80 backdrop-blur-xl border border-white/10 rounded-2xl shadow-2xl focus-within:border-primary/50 focus-within:ring-1 focus-within:ring-primary/20 transition-all duration-300">
                <input
                  {...register("message")}
                  placeholder="Ask a question about your documents..."
                  className="flex-1 bg-transparent px-6 py-4 text-base focus:outline-none placeholder:text-muted-foreground/50"
                  disabled={isPending}
                  autoComplete="off"
                />
                <div className="pr-2">
                  <button
                    type="submit"
                    disabled={isPending}
                    className={cn(
                      "p-3 rounded-xl transition-all duration-200 flex items-center justify-center",
                      "bg-primary text-primary-foreground font-medium shadow-lg hover:shadow-primary/25 hover:-translate-y-0.5 active:translate-y-0",
                      "disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none disabled:shadow-none"
                    )}
                  >
                    {isPending ? (
                      <Loader2 className="w-5 h-5 animate-spin" />
                    ) : (
                      <Send className="w-5 h-5" />
                    )}
                  </button>
                </div>
              </div>
              
              <p className="text-center text-xs text-muted-foreground mt-3 opacity-60">
                AI can make mistakes. Please verify important information.
              </p>
            </form>
          </div>
        </div>
      </main>
    </div>
  );
}
