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

ALTER TABLE public.rag_feedback ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS weather_app_insert_feedback
ON public.rag_feedback;

DROP POLICY IF EXISTS weather_app_select_feedback
ON public.rag_feedback;

CREATE POLICY weather_app_insert_feedback
ON public.rag_feedback
FOR INSERT
TO weather_app
WITH CHECK (true);

CREATE POLICY weather_app_select_feedback
ON public.rag_feedback
FOR SELECT
TO weather_app
USING (true);
