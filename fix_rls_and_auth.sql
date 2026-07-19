-- Fix RLS Policies for Syndicate App

-- 1. Secure users table
ALTER TABLE public.users ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "Public profiles are viewable by everyone." ON public.users;
CREATE POLICY "Public profiles are viewable by everyone." ON public.users 
  FOR SELECT USING (true);

DROP POLICY IF EXISTS "Users can insert themselves." ON public.users;
-- Only the edge function / backend can insert users now (Service Role bypasses RLS)

DROP POLICY IF EXISTS "Users can update their own status." ON public.users;
CREATE POLICY "Users can update their own status." ON public.users 
  FOR UPDATE USING (auth.uid() = id);

-- 2. Secure friendships
ALTER TABLE public.friendships ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS "delete_own_friendships" ON public.friendships;
DROP POLICY IF EXISTS "friendships_delete_secure" ON public.friendships;
DROP POLICY IF EXISTS "friendships_insert_secure" ON public.friendships;
DROP POLICY IF EXISTS "friendships_select" ON public.friendships;
DROP POLICY IF EXISTS "insert_own_friendships" ON public.friendships;
DROP POLICY IF EXISTS "select_own_friendships" ON public.friendships;
DROP POLICY IF EXISTS "update_own_friendships" ON public.friendships;

CREATE POLICY "Users can select their friendships" ON public.friendships
  FOR SELECT USING (
    (auth.uid() IN (SELECT id FROM public.users WHERE tg_id = requester_id)) OR 
    (auth.uid() IN (SELECT id FROM public.users WHERE tg_id = addressee_id))
  );

CREATE POLICY "Users can insert their friendships" ON public.friendships
  FOR INSERT WITH CHECK (
    auth.uid() IN (SELECT id FROM public.users WHERE tg_id = requester_id)
  );

CREATE POLICY "Users can update their friendships" ON public.friendships
  FOR UPDATE USING (
    (auth.uid() IN (SELECT id FROM public.users WHERE tg_id = requester_id)) OR 
    (auth.uid() IN (SELECT id FROM public.users WHERE tg_id = addressee_id))
  );

-- 3. Secure user_devices
ALTER TABLE public.user_devices ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS "Allow full access" ON public.user_devices;

CREATE POLICY "Users can manage their own devices" ON public.user_devices
  FOR ALL USING (
    auth.uid() IN (SELECT id FROM public.users WHERE tg_id = user_id)
  );

-- 4. Secure device_requests
ALTER TABLE public.device_requests ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS "Users can view their own device requests" ON public.device_requests;
DROP POLICY IF EXISTS "Users can insert their own device requests" ON public.device_requests;
DROP POLICY IF EXISTS "Users can update their own device requests" ON public.device_requests;
DROP POLICY IF EXISTS "Users can delete their own device requests" ON public.device_requests;

CREATE POLICY "Users can view their own device requests" ON public.device_requests
  FOR SELECT USING (
    auth.uid() IN (SELECT id FROM public.users WHERE tg_id = user_id)
  );
CREATE POLICY "Users can insert their own device requests" ON public.device_requests
  FOR INSERT WITH CHECK (
    auth.uid() IN (SELECT id FROM public.users WHERE tg_id = user_id)
  );
CREATE POLICY "Users can update their own device requests" ON public.device_requests
  FOR UPDATE USING (
    auth.uid() IN (SELECT id FROM public.users WHERE tg_id = user_id)
  );
CREATE POLICY "Users can delete their own device requests" ON public.device_requests
  FOR DELETE USING (
    auth.uid() IN (SELECT id FROM public.users WHERE tg_id = user_id)
  );

-- 5. WebAuthn Challenges table
CREATE TABLE IF NOT EXISTS public.auth_challenges (
    id text NOT NULL PRIMARY KEY,
    challenge text NOT NULL,
    updated_at timestamp with time zone DEFAULT now()
);

-- Enable RLS but let only the service role access it (so client can't query it)
ALTER TABLE public.auth_challenges ENABLE ROW LEVEL SECURITY;
