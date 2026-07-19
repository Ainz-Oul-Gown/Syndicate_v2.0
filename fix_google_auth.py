import re

with open('src/components/LoginScreen.tsx', 'r') as f:
    content = f.read()

# Add imports for firebase
import_str = "import { auth, googleProvider } from '../lib/firebase';\nimport { signInWithPopup } from 'firebase/auth';\n"
if "import { auth" not in content:
    content = content.replace("import { createClient }", import_str + "import { createClient }")

# Add state variables for google_auth
state_vars = """
  // Google Auth State
  const [googleName, setGoogleName] = useState('');
  const [googleInvite, setGoogleInvite] = useState('');
"""
content = content.replace("const [googleAction, setGoogleAction] = useState<'login' | 'register'>('login');", "const [googleAction, setGoogleAction] = useState<'login' | 'register'>('login');\n" + state_vars)

# Replace handleGoogleAccountSelect with handleRealGoogleSignIn
handle_google_code = """
  const handleRealGoogleSignIn = async () => {
    setErrorMessage(null);
    setIsSubmitting(true);
    hapticImpact("medium");

    if (googleAction === 'register' && !googleInvite.trim()) {
      hapticImpact("error");
      setErrorMessage('Пожалуйста, введите код приглашения (Invite Code) для прохождения белого списка.');
      setIsSubmitting(false);
      return;
    }

    try {
      const result = await signInWithPopup(auth, googleProvider);
      const user = result.user;
      const accountEmail = user.email || 'unknown@gmail.com';
      const accountName = googleAction === 'register' ? (googleName.trim() || user.displayName || 'Google User') : (user.displayName || 'Google User');
      
      const stableId = getStableNumericId(user.uid); // use robust Google UID

      if (googleAction === 'login') {
        const { data: userProfile } = await supabaseClient
          .from('users')
          .select('*')
          .eq('tg_id', stableId)
          .maybeSingle();

        if (!userProfile) {
          hapticImpact("error");
          setErrorMessage(`Google-аккаунт ${accountEmail} не зарегистрирован в Синдикате.`);
          setIsSubmitting(false);
          return;
        }

        const keysPayload = JSON.parse(userProfile.public_key || '{}');
        if (keysPayload.vault) {
          const googleDerivedAes = await deriveAesKeyFromSeed(`google-auth-key-derivation-salt-${user.uid}`);
          const decryptedKeys = await decryptVault(googleDerivedAes, keysPayload.vault);

          if (decryptedKeys) {
            const impRsa = await window.crypto.subtle.importKey(
              'jwk', 
              decryptedKeys.rsaPrivJwk, 
              { name: 'RSA-OAEP', hash: 'SHA-256' }, 
              true, 
              ['decrypt']
            );
            const impEcdsa = await window.crypto.subtle.importKey(
              'jwk', 
              decryptedKeys.ecdsaPrivJwk, 
              { name: 'ECDSA', namedCurve: decryptedKeys.ecdsaPrivJwk.crv || 'P-256' }, 
              true, 
              ['sign']
            );
            await idbKeyval.set(`my_private_key_${stableId}`, impRsa);
            await idbKeyval.set(`my_sign_key_${stableId}`, impEcdsa);
            localStorage.setItem('synd_my_pubkey_cache', JSON.stringify(keysPayload.legacy?.rsa || {}));
            localStorage.setItem('synd_my_pubsign_cache', JSON.stringify(keysPayload.legacy?.ecdsa || {}));
          }
        }
        localStorage.setItem('synd_alt_user', JSON.stringify({ id: stableId, first_name: userProfile.first_name, method: 'google' }));
        hapticImpact("success");
        const token = await customAuthCall(stableId, userProfile.first_name, null, false);
        onLoginSuccess(token, null, { id: stableId, first_name: userProfile.first_name });
      } else {
        const isInviteValid = await verifyAndConsumeInvite(googleInvite);
        if (!isInviteValid) {
          hapticImpact("error");
          setErrorMessage('Неверный или уже использованный код приглашения.');
          setIsSubmitting(false);
          return;
        }

        const { data: existingUser } = await supabaseClient
          .from('users')
          .select('tg_id')
          .eq('tg_id', stableId)
          .maybeSingle();

        if (existingUser) {
          hapticImpact("error");
          setErrorMessage('Этот Google-аккаунт уже привязан к профилю.');
          setIsSubmitting(false);
          return;
        }

        const rsaKeyPair = await window.crypto.subtle.generateKey(
          { name: 'RSA-OAEP', modulusLength: 2048, publicExponent: new Uint8Array([1, 0, 1]), hash: 'SHA-256' },
          true,
          ['encrypt', 'decrypt']
        ) as CryptoKeyPair;
        
        const ecdsaKeyPair = await window.crypto.subtle.generateKey(
          { name: 'ECDSA', namedCurve: 'P-256' },
          true,
          ['sign', 'verify']
        ) as CryptoKeyPair;

        const rsaPubJwk = await window.crypto.subtle.exportKey('jwk', rsaKeyPair.publicKey);
        const rsaPrivJwk = await window.crypto.subtle.exportKey('jwk', rsaKeyPair.privateKey);
        const ecdsaPubJwk = await window.crypto.subtle.exportKey('jwk', ecdsaKeyPair.publicKey);
        const ecdsaPrivJwk = await window.crypto.subtle.exportKey('jwk', ecdsaKeyPair.privateKey);

        const googleDerivedAes = await deriveAesKeyFromSeed(`google-auth-key-derivation-salt-${user.uid}`);
        const encryptedVaultJson = await encryptVault(googleDerivedAes, rsaPrivJwk, ecdsaPrivJwk);

        const publicKeysPayload = {
          legacy: { rsa: rsaPubJwk, ecdsa: ecdsaPubJwk },
          vault: encryptedVaultJson
        };

        const token = await customAuthCall(stableId, accountName, publicKeysPayload, true);
        await idbKeyval.set(`my_private_key_${stableId}`, rsaKeyPair.privateKey);
        await idbKeyval.set(`my_sign_key_${stableId}`, ecdsaKeyPair.privateKey);
        localStorage.setItem('synd_my_pubkey_cache', JSON.stringify(rsaPubJwk));
        localStorage.setItem('synd_my_pubsign_cache', JSON.stringify(ecdsaPubJwk));
        localStorage.setItem('synd_alt_user', JSON.stringify({ id: stableId, first_name: accountName, method: 'google' }));
        
        hapticImpact("success");
        onLoginSuccess(token, null, { id: stableId, first_name: accountName });
      }
    } catch (err: any) {
      hapticImpact("error");
      setErrorMessage(`Ошибка Google OAuth: ${err.message}`);
    } finally {
      setIsSubmitting(false);
    }
  };
"""

content = re.sub(r'const handleGoogleAccountSelect = async \([^)]*\) => \{.*?(?=const handleCopyText =)', handle_google_code, content, flags=re.DOTALL)

with open('src/components/LoginScreen.tsx', 'w') as f:
    f.write(content)
