import re

with open('src/components/SettingsModal.tsx', 'r') as f:
    content = f.read()

# We need to replace handleTogglePasskey
old_block = """  const handleTogglePasskey = async () => {
    hapticImpact("selection");
    if (hasPasskey) {
      if (confirm("Вы действительно хотите отключить вход по Passkey (Биометрии) на этом устройстве?")) {
        try {
          await idbKeyval.del('syndicate_passkey_credential');
          localStorage.removeItem('synd_use_biometrics');
          setHasPasskey(false);
          hapticImpact("success");
        } catch (e) {
          console.error('Failed to disable passkey', e);
        }
      }
    } else {
      if (confirm("Включить быстрый вход по Passkey (Биометрии) на этом устройстве? Это позволит разблокировать приложение по отпечатку пальца или FaceID без ввода PIN-кода.")) {
        try {
          // Export active keys from IndexedDB
          const rsaKey = await idbKeyval.get<CryptoKey>(`my_private_key_${userId}`);
          const ecdsaKey = await idbKeyval.get<CryptoKey>(`my_sign_key_${userId}`);

          let localVault = null;
          const simulatedSeed = `passkey security credential anchor secret syndicate node ${userName.trim().toLowerCase()}`;
          const aesKey = await deriveAesKeyFromSeed(simulatedSeed);

          if (rsaKey && ecdsaKey) {
            try {
              const rsaPrivJwk = await window.crypto.subtle.exportKey('jwk', rsaKey);
              const ecdsaPrivJwk = await window.crypto.subtle.exportKey('jwk', ecdsaKey);
              localVault = await encryptVault(aesKey, rsaPrivJwk, ecdsaPrivJwk);
            } catch (err) {
              console.error('Failed to export keys for biometric vault', err);
            }
          }

          await idbKeyval.set('syndicate_passkey_credential', {
            id: userId,
            name: userName,
            seed: simulatedSeed,
            local_vault: localVault
          });
          localStorage.setItem('synd_use_biometrics', 'on');
          setHasPasskey(true);
          hapticImpact("success");
        } catch (e) {
          console.error('Failed to enable passkey', e);
        }
      }
    }
  };"""

new_block = """  const handleTogglePasskey = async () => {
    hapticImpact("selection");
    if (hasPasskey) {
      if (confirm("Вы действительно хотите отключить вход по Passkey (Биометрии) на этом устройстве?")) {
        try {
          await idbKeyval.del('syndicate_passkey_credential');
          localStorage.removeItem('synd_use_biometrics');
          setHasPasskey(false);
          hapticImpact("success");
        } catch (e) {
          console.error('Failed to disable passkey', e);
        }
      }
    } else {
      if (confirm("Включить быстрый вход по Passkey (Биометрии) на этом устройстве? Это позволит разблокировать приложение по отпечатку пальца или FaceID без ввода PIN-кода.")) {
        try {
          const { data: dbUser } = await supabaseClient.from('users').select('public_key').eq('tg_id', userId).maybeSingle();
          const publicKeysPayload = dbUser ? dbUser.public_key : '{}';

          const optsRes = await fetch('/api/auth/webauthn/generate-registration-options', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name: userName, stableId: userId })
          });
          const options = await optsRes.json();
          if (options.error) throw new Error(options.error);

          let attResp;
          try {
            attResp = await startRegistration(options);
          } catch (e: any) {
            throw new Error('Регистрация Passkey отменена: ' + e.message);
          }

          const verifyRes = await fetch('/api/auth/webauthn/verify-registration', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 
              stableId: userId, 
              name: userName, 
              response: attResp,
              publicKeysPayload: publicKeysPayload
            })
          });
          
          const verification = await verifyRes.json();
          if (verification.error) throw new Error(verification.error);

          // Export active keys from IndexedDB to store locally for passkey usage since
          // Passkeys only authenticate, they don't derive encryption keys directly
          const rsaKey = await idbKeyval.get<CryptoKey>(`my_private_key_${userId}`);
          const ecdsaKey = await idbKeyval.get<CryptoKey>(`my_sign_key_${userId}`);

          let localVault = null;
          const simulatedSeed = `passkey security node ${userName.trim().toLowerCase()} ${userId}`;
          const aesKey = await deriveAesKeyFromSeed(simulatedSeed);

          if (rsaKey && ecdsaKey) {
            try {
              const rsaPrivJwk = await window.crypto.subtle.exportKey('jwk', rsaKey);
              const ecdsaPrivJwk = await window.crypto.subtle.exportKey('jwk', ecdsaKey);
              localVault = await encryptVault(aesKey, rsaPrivJwk, ecdsaPrivJwk);
            } catch (err) {
              console.error('Failed to export keys for biometric vault', err);
            }
          }

          await idbKeyval.set('syndicate_passkey_credential', {
            id: userId,
            name: userName,
            seed: simulatedSeed,
            local_vault: localVault
          });
          localStorage.setItem('synd_use_biometrics', 'on');
          setHasPasskey(true);
          hapticImpact("success");
        } catch (e: any) {
          console.error('Failed to enable passkey', e);
          alert('Ошибка Passkey: ' + e.message);
        }
      }
    }
  };"""

content = content.replace(old_block, new_block)

with open('src/components/SettingsModal.tsx', 'w') as f:
    f.write(content)
