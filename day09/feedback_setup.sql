CREATE TABLE IF NOT EXISTS public.rag_feedback (
    id BIGSERIAL PRIMARY KEY,
    city TEXT NOT NULL,
    question TEXT NOT NULL,
    answer TEXT NOT NULL,
    citations TEXT NOT NULL,
    model TEXT NOT NULL,
    rating TEXT NOT NULL CHECK (rating IN ('up', 'down')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

GRANT USAGE, SELECT
ON SEQUENCE public.rag_feedback_id_seq
TO weather_app;

GRANT INSERT, SELECT
ON TABLE public.rag_feedback
TO weather_app;
