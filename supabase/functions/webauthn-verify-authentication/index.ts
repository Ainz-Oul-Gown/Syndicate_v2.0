import { serve } from "https://deno.land/std@0.168.0/http/server.ts"
import { verifyAuthenticationResponse } from 'npm:@simplewebauthn/server'
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2'
import * as jose from 'https://deno.land/x/jose@v4.14.4/index.ts'
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
    const { stableId, response } = await req.json();
    const origin = req.headers.get("origin") || 'http://localhost:3000';
    const rpID = new URL(origin).hostname;

    const supabaseAdmin = createClient(
      Deno.env.get('SUPABASE_URL') ?? '',
      Deno.env.get('SUPABASE_SERVICE_ROLE_KEY') ?? ''
    );

    const { data: challengeData } = await supabaseAdmin.from('auth_challenges').select('challenge').eq('id', `auth_${stableId}`).single();
    if (!challengeData) throw new Error("Challenge expired or not found");

    const { data: dbUser } = await supabaseAdmin.from('users').select('*').eq('tg_id', stableId).maybeSingle();
    if (!dbUser) throw new Error("User not found");

    const payload = JSON.parse(dbUser.public_key || '{}');
    const passkeys = payload.passkeys || [];
    
    const credential = passkeys.find((c: any) => c.id === response.id);
    if (!credential) throw new Error('Passkey not found for this user');

    const verification = await verifyAuthenticationResponse({
      response,
      expectedChallenge: challengeData.challenge,
      expectedOrigin: origin,
      expectedRPID: rpID,
      authenticator: {
        credentialID: decodeBase64Url(credential.id),
        credentialPublicKey: decodeBase64Url(credential.publicKey),
        counter: credential.counter,
        transports: credential.transports,
      },
    });

    if (verification.verified && verification.authenticationInfo) {
      credential.counter = verification.authenticationInfo.newCounter;
      await supabaseAdmin.from('users').update({ public_key: JSON.stringify(payload) }).eq('id', dbUser.id);
      await supabaseAdmin.from('auth_challenges').delete().eq('id', `auth_${stableId}`);

      const JWT_SECRET = Deno.env.get('JWT_SECRET');
      const secretBytes = new TextEncoder().encode(JWT_SECRET);
      const currentTime = Math.floor(Date.now() / 1000);
      const jwt = await new jose.SignJWT({
          aud: 'authenticated', role: 'authenticated', iss: 'supabase', tg_id: stableId, sub: dbUser.id
      }).setProtectedHeader({ alg: 'HS256', typ: 'JWT' }).setIssuedAt(currentTime - 60).setExpirationTime(currentTime + 60 * 60 * 24 * 30).sign(secretBytes);

      return new Response(JSON.stringify({ verified: true, token: jwt, user: dbUser }), { headers: { ...corsHeaders, 'Content-Type': 'application/json' } });
    } else {
      throw new Error('Verification failed');
    }
  } catch (error: any) {
    return new Response(JSON.stringify({ error: error.message }), { status: 400, headers: corsHeaders });
  }
})
