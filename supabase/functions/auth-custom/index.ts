import { serve } from "https://deno.land/std@0.168.0/http/server.ts"
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2'
import * as jose from 'https://deno.land/x/jose@v4.14.4/index.ts'

const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
  'Access-Control-Allow-Methods': 'POST, OPTIONS',
};

serve(async (req) => {
  if (req.method === 'OPTIONS') {
    return new Response('ok', { headers: corsHeaders });
  }

  try {
    const JWT_SECRET = Deno.env.get('JWT_SECRET');
    if (!JWT_SECRET) throw new Error("Нет JWT_SECRET в переменных окружения");

    const body = await req.json();
    const { stableId, name, publicKeysPayload, isRegister } = body;

    const supabaseAdmin = createClient(
      Deno.env.get('SUPABASE_URL') ?? '',
      Deno.env.get('SUPABASE_SERVICE_ROLE_KEY') ?? ''
    );

    let { data: dbUser } = await supabaseAdmin
      .from('users')
      .select('*')
      .eq('tg_id', stableId)
      .maybeSingle();

    if (isRegister) {
      if (dbUser) {
        throw new Error('Узел с таким идентификатором уже существует');
      }
      const tempToken = crypto.randomUUID().replace(/-/g, '') + crypto.randomUUID().replace(/-/g, '');
      const { data: newUser, error: upsertErr } = await supabaseAdmin
        .from('users')
        .insert({ 
          tg_id: stableId, 
          first_name: name || 'User', 
          auth_token: tempToken,
          public_key: publicKeysPayload ? publicKeysPayload : null,
          status: JSON.stringify({ invites: [] })
        })
        .select('*')
        .single();
        
      if (upsertErr) throw upsertErr;
      dbUser = newUser;
    } else {
      if (!dbUser) {
        throw new Error('Пользователь не найден');
      }
    }

    const secretBytes = new TextEncoder().encode(JWT_SECRET);
    const currentTime = Math.floor(Date.now() / 1000);

    const jwt = await new jose.SignJWT({
        aud: 'authenticated',
        role: 'authenticated',
        iss: 'supabase',
        tg_id: stableId,
        sub: dbUser.id
    })
    .setProtectedHeader({ alg: 'HS256', typ: 'JWT' })
    .setIssuedAt(currentTime - 60)
    .setExpirationTime(currentTime + 60 * 60 * 24 * 30)
    .sign(secretBytes);

    return new Response(JSON.stringify({ token: jwt, user: dbUser }), { headers: { ...corsHeaders, 'Content-Type': 'application/json' } });

  } catch (err: any) {
    return new Response(JSON.stringify({ error: err.message }), { status: 400, headers: corsHeaders });
  }
})
