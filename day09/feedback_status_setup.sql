ALTER TABLE public.rag_feedback
ADD COLUMN IF NOT EXISTS status TEXT NOT NULL DEFAULT 'open',
ADD COLUMN IF NOT EXISTS note TEXT NOT NULL DEFAULT '',
ADD COLUMN IF NOT EXISTS updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW();

ALTER TABLE public.rag_feedback
DROP CONSTRAINT IF EXISTS rag_feedback_status_check;

ALTER TABLE public.rag_feedback
ADD CONSTRAINT rag_feedback_status_check
CHECK (status IN ('open', 'resolved', 'ignored'));

GRANT UPDATE
ON TABLE public.rag_feedback
TO weather_app;

DROP POLICY IF EXISTS weather_app_update_feedback
ON public.rag_feedback;

CREATE POLICY weather_app_update_feedback
ON public.rag_feedback
FOR UPDATE
TO weather_app
USING (true)
WITH CHECK (true);
