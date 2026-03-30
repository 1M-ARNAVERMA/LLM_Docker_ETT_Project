import { db } from "./db";
import {
  documents,
  messages,
  type InsertDocument,
  type InsertMessage,
  type Document,
  type Message
} from "@shared/schema";
import { eq, desc } from "drizzle-orm";

export interface IStorage {
  getDocuments(): Promise<Document[]>;
  createDocument(doc: InsertDocument): Promise<Document>;
  deleteDocument(id: number): Promise<void>;
  
  getMessages(): Promise<Message[]>;
  createMessage(msg: InsertMessage): Promise<Message>;
  clearMessages(): Promise<void>;
}

export class DatabaseStorage implements IStorage {
  async getDocuments(): Promise<Document[]> {
    return await db.select().from(documents).orderBy(desc(documents.createdAt));
  }

  async createDocument(doc: InsertDocument): Promise<Document> {
    const [document] = await db.insert(documents).values(doc).returning();
    return document;
  }

  async deleteDocument(id: number): Promise<void> {
    await db.delete(documents).where(eq(documents.id, id));
  }

  async getMessages(): Promise<Message[]> {
    return await db.select().from(messages).orderBy(messages.createdAt);
  }

  async createMessage(msg: InsertMessage): Promise<Message> {
    const [message] = await db.insert(messages).values(msg).returning();
    return message;
  }

  async clearMessages(): Promise<void> {
    await db.delete(messages);
  }
}

export const storage = new DatabaseStorage();
