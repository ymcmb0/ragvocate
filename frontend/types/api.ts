export interface ChatRequest {
  query: string;
  conversation_id: string;
}

export interface ChatResponse {
  response: string;
  sources: Source[];
  conversation_id: string;
}

export interface Source {
  document: string;
  page: number;
  relevance: number;
  excerpt: string;
  metadata?: Record<string, any>;
}

export interface UploadResponse {
  files: {
    filename: string;
    status: 'success' | 'error';
    message?: string;
  }[];
}

export interface Document {
  id: string;
  name: string;
  size: number;
  uploadedAt: Date;
  status: 'processing' | 'ready' | 'error';
  type: 'precedent' | 'statute' | 'other';
  category: 'precedents' | 'statutes';
}

export interface Conversation {
  id: string;
  title: string;
  createdAt: Date;
  updatedAt: Date;
  messageCount: number;
  searchScope: 'precedents' | 'statutes' | 'both';
}