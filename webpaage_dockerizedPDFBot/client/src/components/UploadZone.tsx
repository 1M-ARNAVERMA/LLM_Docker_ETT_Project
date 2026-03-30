import { useCallback, useState } from "react";
import { Upload, FileType, Loader2, CheckCircle2 } from "lucide-react";
import { cn } from "@/lib/utils";
import { useUploadDocument } from "@/hooks/use-documents";
import { useToast } from "@/hooks/use-toast";

export function UploadZone() {
  const [isDragging, setIsDragging] = useState(false);
  const { mutate: uploadFile, isPending } = useUploadDocument();
  const { toast } = useToast();

  const handleDrag = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setIsDragging(true);
    } else if (e.type === "dragleave") {
      setIsDragging(false);
    }
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);

    const files = Array.from(e.dataTransfer.files);
    if (files.length > 0) {
      handleUpload(files[0]);
    }
  }, []);

  const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      handleUpload(e.target.files[0]);
    }
  };

  const handleUpload = (file: File) => {
    if (file.type !== "application/pdf") {
      toast({
        title: "Invalid file type",
        description: "Please upload PDF files only.",
        variant: "destructive",
      });
      return;
    }

    uploadFile(file, {
      onSuccess: () => {
        toast({
          title: "Upload complete",
          description: `${file.name} has been indexed successfully.`,
        });
      },
      onError: (error) => {
        toast({
          title: "Upload failed",
          description: error.message,
          variant: "destructive",
        });
      },
    });
  };

  return (
    <div
      className={cn(
        "relative group cursor-pointer overflow-hidden rounded-2xl border-2 border-dashed transition-all duration-300",
        isDragging
          ? "border-primary bg-primary/5 shadow-[0_0_30px_rgba(var(--primary),0.1)] scale-[1.01]"
          : "border-border hover:border-primary/50 hover:bg-white/5",
        isPending && "pointer-events-none opacity-80"
      )}
      onDragEnter={handleDrag}
      onDragLeave={handleDrag}
      onDragOver={handleDrag}
      onDrop={handleDrop}
    >
      <input
        type="file"
        accept=".pdf"
        className="absolute inset-0 z-50 cursor-pointer opacity-0"
        onChange={handleFileInput}
        disabled={isPending}
      />
      
      <div className="flex flex-col items-center justify-center py-16 px-6 text-center">
        <div className={cn(
          "w-16 h-16 rounded-2xl flex items-center justify-center mb-6 transition-all duration-500",
          isDragging ? "bg-primary text-primary-foreground rotate-6 scale-110" : "bg-card border border-white/10 text-muted-foreground group-hover:text-primary group-hover:border-primary/30"
        )}>
          {isPending ? (
            <Loader2 className="w-8 h-8 animate-spin" />
          ) : (
            <Upload className="w-8 h-8" />
          )}
        </div>
        
        <h3 className="text-xl font-display font-bold mb-2 text-foreground group-hover:text-glow transition-all">
          {isPending ? "Indexing Document..." : "Drop PDF Here"}
        </h3>
        
        <p className="text-sm text-muted-foreground max-w-xs mx-auto leading-relaxed">
          Drag and drop your knowledge base PDF here, or click to browse.
          <br />
          <span className="text-xs opacity-60 mt-2 block">Maximum file size: 10MB</span>
        </p>
      </div>

      {/* Decorative corner accents */}
      <div className="absolute top-0 left-0 w-4 h-4 border-t-2 border-l-2 border-primary/30 rounded-tl-lg transition-all group-hover:w-6 group-hover:h-6 group-hover:border-primary" />
      <div className="absolute bottom-0 right-0 w-4 h-4 border-b-2 border-r-2 border-primary/30 rounded-br-lg transition-all group-hover:w-6 group-hover:h-6 group-hover:border-primary" />
    </div>
  );
}
