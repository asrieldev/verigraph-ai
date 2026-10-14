CREATE EXTENSION IF NOT EXISTS vector;
CREATE TABLE IF NOT EXISTS analysis_runs (id UUID PRIMARY KEY, repository_url TEXT NOT NULL, status TEXT NOT NULL, demo_mode BOOLEAN NOT NULL, payload JSONB NOT NULL, created_at TIMESTAMPTZ NOT NULL DEFAULT now(), updated_at TIMESTAMPTZ NOT NULL DEFAULT now());
CREATE TABLE IF NOT EXISTS code_chunks (id BIGSERIAL PRIMARY KEY, run_id UUID NOT NULL REFERENCES analysis_runs(id) ON DELETE CASCADE, path TEXT NOT NULL, content TEXT NOT NULL, embedding vector(1536));
CREATE INDEX IF NOT EXISTS code_chunks_run_idx ON code_chunks(run_id);

