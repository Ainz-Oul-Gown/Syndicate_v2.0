import { serve } from "https://deno.land/std@0.168.0/http/server.ts"
import { generateAuthenticationOptions } from 'npm:@simplewebauthn/server'
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2'
import { decodeBase64Url } from "https://deno.land/std@0.224.0/encoding/base64url.ts";

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
    const { stableId } = await req.json();
    const rpID = req.headers.get("origin") ? new URL(req.headers.get("origin")!).hostname : 'localhost';

    const supabaseAdmin = createClient(
      Deno.env.get('SUPABASE_URL') ?? '',
      Deno.env.get('SUPABASE_SERVICE_ROLE_KEY') ?? ''
    );

    const { data: dbUser } = await supabaseAdmin.from('users').select('public_key').eq('tg_id', stableId).maybeSingle();
    if (!dbUser) throw new Error("User not found");

    const payload = JSON.parse(dbUser.public_key || '{}');
    const passkeys = payload.passkeys || [];

    const options = await generateAuthenticationOptions({
      rpID,
      allowCredentials: passkeys.map((cred: any) => ({
        id: decodeBase64Url(cred.id),
        type: 'public-key',
        transports: cred.transports,
      })),
      userVerification: 'preferred',
    });

    await supabaseAdmin.from('auth_challenges').upsert({
      id: `auth_${stableId}`,
      challenge: options.challenge,
      updated_at: new Date().toISOString()
    });

    return new Response(JSON.stringify(options), { headers: { ...corsHeaders, 'Content-Type': 'application/json' } });
  } catch (error: any) {
    return new Response(JSON.stringify({ error: error.message }), { status: 400, headers: corsHeaders });
  }
})
