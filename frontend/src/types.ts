export interface MedicalDocument {
  id: string;
  title: string;
  content: string;
  category: string;
  source?: string;
  file_type?: string;
  file_size?: number;
  status?: string;
  chunk_count?: number;
  metadata_json?: Record<string, string>;
  created_at: string;
  updated_at: string;
}

export interface VerificationResult {
  passed: boolean;
  reason: string;
}

export interface RAGSource {
  id: string;
  title: string;
  category: string;
  source?: string;
  content_preview?: string;
  relevance_score?: number;
  rrf_score?: number;
}

export interface RAGQuery {
  id: string;
  query: string;
  response: string;
  sources: RAGSource[];
  confidence?: number;
  processing_time?: number;
  retrieval_mode?: string;
  verification?: VerificationResult;
  created_at: string;
}

export interface SystemStats {
  total_documents: number;
  processed_documents: number;
  indexed_documents: number;
  total_queries: number;
  average_response_time: number;
  system_health: string;
  document_categories: Record<string, number>;
  recent_queries: RAGQuery[];
}
