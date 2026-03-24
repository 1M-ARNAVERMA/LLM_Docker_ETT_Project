import type { Express } from "express";
import type { Server } from "http";
import { storage } from "./storage";
import { api } from "@shared/routes";
import { z } from "zod";
import multer from "multer";
import { createRequire } from "module";
const require = createRequire(import.meta.url);
const pdfParse = require("pdf-parse");
import OpenAI from "openai";

const upload = multer({ 
  storage: multer.memoryStorage(),
  limits: { fileSize: 5 * 1024 * 1024 } // 5MB limit
});

export async function registerRoutes(
  httpServer: Server,
  app: Express
): Promise<Server> {
  
  // Initialize OpenAI (API Key should be in env vars)
  // We check for key on request to avoid crashing if not set yet
  
  app.get(api.documents.list.path, async (req, res) => {
    const docs = await storage.getDocuments();
    res.json(docs);
  });

  app.post(api.documents.create.path, upload.single('file'), async (req, res) => {
    try {
      if (!req.file) {
        return res.status(400).json({ message: "No file uploaded" });
      }

      let content = "";

      if (req.file.mimetype === 'application/pdf') {
        const data = await pdfParse(req.file.buffer);
        content = data.text;
      } else if (req.file.mimetype === 'text/plain') {
        content = req.file.buffer.toString('utf-8');
      } else {
        return res.status(400).json({ message: "Unsupported file type. Upload PDF or Text." });
      }

      if (!content.trim()) {
        return res.status(400).json({ message: "Could not extract text from file" });
      }

      const doc = await storage.createDocument({
        title: req.file.originalname,
        content: content.trim()
      });

      res.status(201).json(doc);
    } catch (err) {
      console.error("Upload error:", err);
      res.status(500).json({ message: "Failed to process file" });
    }
  });

  app.delete(api.documents.delete.path, async (req, res) => {
    await storage.deleteDocument(Number(req.params.id));
    res.status(204).send();
  });

  app.get(api.chat.history.path, async (req, res) => {
    const msgs = await storage.getMessages();
    res.json(msgs);
  });

  app.delete(api.chat.clear.path, async (req, res) => {
    await storage.clearMessages();
    res.status(204).send();
  });

  app.post(api.chat.send.path, async (req, res) => {
    try {
      const input = api.chat.send.input.parse(req.body);
      
      // Save user message
      await storage.createMessage({
        role: 'user',
        content: input.message
      });

      // Prepare context from documents
      const docs = await storage.getDocuments();
      const context = docs.map(d => `--- Document: ${d.title} ---\n${d.content}\n`).join("\n");
      
      const apiKey = process.env.OPENAI_API_KEY;
      
      let aiResponseContent = "";

      if (!apiKey) {
        aiResponseContent = "I am a demo bot. I cannot answer intelligently because the OPENAI_API_KEY environment variable is not set. Please set it in your Replit Secrets or environment variables to enable the AI functionality. \n\nFound context from " + docs.length + " documents.";
      } else {
        const openai = new OpenAI({ apiKey });
        
        const systemPrompt = `You are a helpful assistant. 
        You have access to the following documents provided by the user. 
        Answer the user's question based primarily on these documents. 
        If the answer is not in the documents, you can use your general knowledge but mention that it's not in the documents.
        
        Context:
        ${context.substring(0, 100000)} // Truncate to avoid token limits roughly
        `;

        const response = await openai.chat.completions.create({
          model: "gpt-4o",
          messages: [
            { role: "system", content: systemPrompt },
            { role: "user", content: input.message }
          ],
        });

        aiResponseContent = response.choices[0].message.content || "No response generated.";
      }

      // Save and return AI response
      const aiMsg = await storage.createMessage({
        role: 'assistant',
        content: aiResponseContent
      });

      res.json(aiMsg);

    } catch (err) {
      console.error("Chat error:", err);
      if (err instanceof z.ZodError) {
        res.status(400).json({ message: "Invalid input" });
      } else {
        res.status(500).json({ message: "Failed to generate response" });
      }
    }
  });

  return httpServer;
}
