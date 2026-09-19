-- ==============================================================================
-- Supabase Realtime Setup Script for OCG Agent
-- Run this in the Supabase SQL Editor: https://supabase.com/dashboard/project/_/sql
-- ==============================================================================

-- 1. Ensure tables are added to the Supabase Realtime publication
DO $$
BEGIN
    -- Add public.sessions
    IF NOT EXISTS (
        SELECT 1 FROM pg_publication_tables 
        WHERE pubname = 'supabase_realtime' AND schemaname = 'public' AND tablename = 'sessions'
    ) THEN
        ALTER PUBLICATION supabase_realtime ADD TABLE public.sessions;
    END IF;

    -- Add public.messages
    IF NOT EXISTS (
        SELECT 1 FROM pg_publication_tables 
        WHERE pubname = 'supabase_realtime' AND schemaname = 'public' AND tablename = 'messages'
    ) THEN
        ALTER PUBLICATION supabase_realtime ADD TABLE public.messages;
    END IF;

    -- Add public.agent_memories
    IF NOT EXISTS (
        SELECT 1 FROM pg_publication_tables 
        WHERE pubname = 'supabase_realtime' AND schemaname = 'public' AND tablename = 'agent_memories'
    ) THEN
        ALTER PUBLICATION supabase_realtime ADD TABLE public.agent_memories;
    END IF;
END $$;

-- 2. Enable REPLICA IDENTITY FULL
-- Required so that UPDATE and DELETE events include complete row data in Realtime payloads
ALTER TABLE public.sessions REPLICA IDENTITY FULL;
ALTER TABLE public.messages REPLICA IDENTITY FULL;
ALTER TABLE public.agent_memories REPLICA IDENTITY FULL;

-- 3. RLS Guest & Authenticated Realtime Policies
-- Sessions and messages user_id is UUID (NULL for guest, auth.uid() for logged in)
-- agent_memories user_id is TEXT (supports 'global', 'guest_user', or auth.uid())
DROP POLICY IF EXISTS "Allow guest access to sessions" ON public.sessions;
CREATE POLICY "Allow guest access to sessions"
    ON public.sessions FOR ALL
    USING (user_id IS NULL OR auth.uid() = user_id)
    WITH CHECK (user_id IS NULL OR auth.uid() = user_id);

DROP POLICY IF EXISTS "Allow guest access to messages" ON public.messages;
CREATE POLICY "Allow guest access to messages"
    ON public.messages FOR ALL
    USING (user_id IS NULL OR auth.uid() = user_id)
    WITH CHECK (user_id IS NULL OR auth.uid() = user_id);

DROP POLICY IF EXISTS "Allow guest access to agent_memories" ON public.agent_memories;
CREATE POLICY "Allow guest access to agent_memories"
    ON public.agent_memories FOR ALL
    USING (user_id IS NULL OR user_id LIKE 'guest%' OR user_id = 'global' OR auth.uid()::text = user_id)
    WITH CHECK (user_id IS NULL OR user_id LIKE 'guest%' OR user_id = 'global' OR auth.uid()::text = user_id);

-- Confirmation query: check that realtime is enabled
SELECT 
    schemaname, 
    tablename 
FROM 
    pg_publication_tables 
WHERE 
    pubname = 'supabase_realtime';
