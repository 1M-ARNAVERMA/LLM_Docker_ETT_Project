import { useDocuments, useDeleteDocument } from "@/hooks/use-documents";
import { FileText, Trash2, Calendar, HardDrive } from "lucide-react";
import { format } from "date-fns";
import { Loader2 } from "lucide-react";

export function DocumentList() {
  const { data: documents, isLoading } = useDocuments();
  const { mutate: deleteDoc, isPending: isDeleting } = useDeleteDocument();

  if (isLoading) {
    return (
      <div className="flex items-center justify-center p-12">
        <Loader2 className="w-8 h-8 text-primary animate-spin" />
      </div>
    );
  }

  if (!documents?.length) {
    return (
      <div className="text-center py-12 px-6 rounded-2xl border border-dashed border-white/10 bg-white/[0.02]">
        <FileText className="w-12 h-12 text-muted-foreground/30 mx-auto mb-4" />
        <h3 className="text-lg font-medium text-foreground mb-1">No documents yet</h3>
        <p className="text-muted-foreground text-sm">Upload a PDF to start chatting with your data.</p>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 gap-4">
      {documents.map((doc) => (
        <div
          key={doc.id}
          className="group relative flex items-center gap-4 p-4 rounded-xl bg-card border border-white/5 hover:border-primary/30 hover:shadow-[0_0_20px_rgba(var(--primary),0.05)] transition-all duration-300"
        >
          <div className="w-12 h-12 rounded-lg bg-secondary/50 flex items-center justify-center text-primary shrink-0 group-hover:scale-105 transition-transform duration-300">
            <FileText className="w-6 h-6" />
          </div>

          <div className="flex-1 min-w-0">
            <h4 className="font-medium text-foreground truncate pr-4 group-hover:text-primary transition-colors">
              {doc.title}
            </h4>
            <div className="flex items-center gap-4 mt-1 text-xs text-muted-foreground font-mono">
              <span className="flex items-center gap-1.5">
                <Calendar className="w-3 h-3" />
                {doc.createdAt && format(new Date(doc.createdAt), "MMM d, yyyy")}
              </span>
              <span className="flex items-center gap-1.5">
                <HardDrive className="w-3 h-3" />
                PDF
              </span>
            </div>
          </div>

          <button
            onClick={() => deleteDoc(doc.id)}
            disabled={isDeleting}
            className="p-2 rounded-lg text-muted-foreground/50 hover:text-destructive hover:bg-destructive/10 transition-colors opacity-0 group-hover:opacity-100 disabled:opacity-50"
            title="Delete document"
          >
            {isDeleting ? (
              <Loader2 className="w-5 h-5 animate-spin" />
            ) : (
              <Trash2 className="w-5 h-5" />
            )}
          </button>
        </div>
      ))}
    </div>
  );
}
