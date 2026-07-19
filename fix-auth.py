import re

with open('src/components/LoginScreen.tsx', 'r') as f:
    content = f.read()

# Replace insert blocks with customAuthCall
content = re.sub(
    r"const \{ error: insertError \} = await supabaseClient\s*\.from\('users'\)\s*\.insert\(\{\s*tg_id: ([a-zA-Z]+),\s*first_name: ([^,]+),\s*public_key: JSON.stringify\(publicKeysPayload\),\s*status: JSON.stringify\(\{ invites: \[\] \}\)\s*\}\);\s*(if \(insertError\) \{?\s*throw insertError;\s*\}?)",
    r"const token = await customAuthCall(\1, \2, publicKeysPayload, true);",
    content
)

# Replace all onLoginSuccess('SUPABASE_ANON' with token (for register) or customAuthCall for login
# Seed Register (has token from above)
content = content.replace(
    "onLoginSuccess('SUPABASE_ANON', null, { id: numericId, first_name: regName.trim() });",
    "onLoginSuccess(token, null, { id: numericId, first_name: regName.trim() });"
)
# Seed Login
content = content.replace(
    "onLoginSuccess('SUPABASE_ANON', null, { id: numericId, first_name: userProfile.first_name });",
    "const token = await customAuthCall(numericId, userProfile.first_name, null, false);\n      onLoginSuccess(token, null, { id: numericId, first_name: userProfile.first_name });"
)

# Telegram Register
content = content.replace(
    "onLoginSuccess('SUPABASE_ANON', null, { id: stableId, first_name: telegramName.trim() });",
    "onLoginSuccess(token, null, { id: stableId, first_name: telegramName.trim() });"
)
# Telegram Login
content = content.replace(
    "onLoginSuccess('SUPABASE_ANON', null, { id: stableId, first_name: userProfile.first_name });",
    "const token = await customAuthCall(stableId, userProfile.first_name, null, false);\n        onLoginSuccess(token, null, { id: stableId, first_name: userProfile.first_name });"
)

# Email Register
content = content.replace(
    "onLoginSuccess('SUPABASE_ANON', null, { id: stableId, first_name: emailName.trim() });",
    "onLoginSuccess(token, null, { id: stableId, first_name: emailName.trim() });"
)

# Google Register
content = content.replace(
    "onLoginSuccess('SUPABASE_ANON', null, { id: stableId, first_name: accountName });",
    "onLoginSuccess(token, null, { id: stableId, first_name: accountName });"
)

with open('src/components/LoginScreen.tsx', 'w') as f:
    f.write(content)
