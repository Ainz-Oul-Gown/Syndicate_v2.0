import { serve } from "https://deno.land/std@0.168.0/http/server.ts"
import { verifyRegistrationResponse } from 'npm:@simplewebauthn/server'
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2'
import * as jose from 'https://deno.land/x/jose@v4.14.4/index.ts'
import { encodeBase64Url } from "https://deno.land/std@0.224.0/encoding/base64url.ts";

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
    const { stableId, name, response, publicKeysPayload } = await req.json();
    const origin = req.headers.get("origin") || 'http://localhost:3000';
    const rpID = new URL(origin).hostname;

    const supabaseAdmin = createClient(
      Deno.env.get('SUPABASE_URL') ?? '',
      Deno.env.get('SUPABASE_SERVICE_ROLE_KEY') ?? ''
    );

    const { data: challengeData } = await supabaseAdmin.from('auth_challenges').select('challenge').eq('id', `reg_${stableId}`).single();
    if (!challengeData) throw new Error("Challenge expired or not found");

    const expectedChallenge = challengeData.challenge;

    const verification = await verifyRegistrationResponse({
      response,
      expectedChallenge,
      expectedOrigin: origin,
      expectedRPID: rpID,
    });

    if (verification.verified && verification.registrationInfo) {
      const { credentialPublicKey, credentialID, counter } = verification.registrationInfo;
      
      const newCredential = {
        id: encodeBase64Url(credentialID),
        publicKey: encodeBase64Url(credentialPublicKey),
        counter,
        transports: response.response.transports || [],
      };

      const payloadWithCreds = JSON.parse(publicKeysPayload || '{}');
      if (!payloadWithCreds.passkeys) payloadWithCreds.passkeys = [];
      payloadWithCreds.passkeys.push(newCredential);

      // Check if user exists (to append or create)
      const { data: existingUser } = await supabaseAdmin.from('users').select('id, public_key').eq('tg_id', stableId).maybeSingle();
      
      let finalUser;
      if (existingUser) {
        // Appending passkey to existing user
        const existingPayload = JSON.parse(existingUser.public_key || '{}');
        existingPayload.passkeys = payloadWithCreds.passkeys;
        
        const { data: updatedUser, error: updateErr } = await supabaseAdmin
          .from('users')
          .update({ public_key: JSON.stringify(existingPayload) })
          .eq('tg_id', stableId)
          .select('*')
          .single();
        if (updateErr) throw updateErr;
        finalUser = updatedUser;
      } else {
        const tempToken = crypto.randomUUID().replace(/-/g, '') + crypto.randomUUID().replace(/-/g, '');
        const { data: newUser, error: upsertErr } = await supabaseAdmin
          .from('users')
          .insert({ 
            tg_id: stableId, 
            first_name: name || 'User', 
            auth_token: tempToken,
            public_key: JSON.stringify(payloadWithCreds),
            status: JSON.stringify({ invites: [] })
          })
          .select('*')
          .single();
        if (upsertErr) throw upsertErr;
        finalUser = newUser;
      }

      await supabaseAdmin.from('auth_challenges').delete().eq('id', `reg_${stableId}`);

      const JWT_SECRET = Deno.env.get('JWT_SECRET');
      const secretBytes = new TextEncoder().encode(JWT_SECRET);
      const currentTime = Math.floor(Date.now() / 1000);
      const jwt = await new jose.SignJWT({
          aud: 'authenticated', role: 'authenticated', iss: 'supabase', tg_id: stableId, sub: finalUser.id
      }).setProtectedHeader({ alg: 'HS256', typ: 'JWT' }).setIssuedAt(currentTime - 60).setExpirationTime(currentTime + 60 * 60 * 24 * 30).sign(secretBytes);

      return new Response(JSON.stringify({ verified: true, token: jwt, user: finalUser }), { headers: { ...corsHeaders, 'Content-Type': 'application/json' } });
    } else {
      throw new Error('Verification failed');
    }
  } catch (error: any) {
    return new Response(JSON.stringify({ error: error.message }), { status: 400, headers: corsHeaders });
  }
})
