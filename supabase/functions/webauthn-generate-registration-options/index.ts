import { serve } from "https://deno.land/std@0.168.0/http/server.ts"
import { generateRegistrationOptions } from 'npm:@simplewebauthn/server'
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2'

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
    const { name, stableId } = await req.json();
    
    // In production, the RP ID should match your GitHub Pages domain (e.g. username.github.io)
    const rpName = 'Syndicate';
    const rpID = req.headers.get("origin") ? new URL(req.headers.get("origin")!).hostname : 'localhost';

    const options = await generateRegistrationOptions({
      rpName,
      rpID,
      userID: new TextEncoder().encode(stableId.toString()),
      userName: name,
      attestationType: 'none',
      authenticatorSelection: {
        residentKey: 'preferred',
        userVerification: 'preferred',
      },
    });

    const supabaseAdmin = createClient(
      Deno.env.get('SUPABASE_URL') ?? '',
      Deno.env.get('SUPABASE_SERVICE_ROLE_KEY') ?? ''
    );

    // Save challenge
    await supabaseAdmin.from('auth_challenges').upsert({
      id: `reg_${stableId}`,
      challenge: options.challenge,
      updated_at: new Date().toISOString()
    });

    return new Response(JSON.stringify(options), { headers: { ...corsHeaders, 'Content-Type': 'application/json' } });
  } catch (error: any) {
    return new Response(JSON.stringify({ error: error.message }), { status: 400, headers: corsHeaders });
  }
})
