import { Navigation } from "@/components/Navigation";
import { UploadZone } from "@/components/UploadZone";
import { DocumentList } from "@/components/DocumentList";
import { FileStack } from "lucide-react";

export default function Documents() {
  return (
    <div className="flex min-h-screen bg-background text-foreground selection:bg-primary/20">
      <Navigation />
      
      <main className="flex-1 ml-20 md:ml-64 transition-all duration-300">
        <div className="max-w-4xl mx-auto px-6 py-12 md:py-20 space-y-12">
          
          <div className="space-y-4">
            <h1 className="text-4xl md:text-5xl font-bold font-display tracking-tight text-glow">
              Knowledge Base
            </h1>
            <p className="text-lg text-muted-foreground max-w-2xl leading-relaxed">
              Manage the documents your AI assistant learns from. Upload PDFs to expand its knowledge base instantly.
            </p>
          </div>

          <section className="space-y-6">
            <div className="flex items-center gap-3 text-lg font-semibold font-display">
              <div className="w-1 h-6 bg-primary rounded-full shadow-[0_0_10px_var(--primary)]" />
              Upload New
            </div>
            <UploadZone />
          </section>

          <div className="w-full h-px bg-gradient-to-r from-transparent via-white/10 to-transparent" />

          <section className="space-y-6">
            <div className="flex items-center gap-3 text-lg font-semibold font-display">
              <div className="w-8 h-8 rounded-lg bg-white/5 flex items-center justify-center text-primary">
                <FileStack className="w-4 h-4" />
              </div>
              Active Documents
            </div>
            <DocumentList />
          </section>

        </div>
      </main>
    </div>
  );
}
