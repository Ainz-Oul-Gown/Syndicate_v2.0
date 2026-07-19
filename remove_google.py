import re

with open('src/components/LoginScreen.tsx', 'r') as f:
    content = f.read()

# Remove Google overlay rendering block
content = re.sub(
    r'\{/\* --- SIMULATED GOOGLE ACCOUNT PICKER OVERLAY ---\s*\*/\}[\s\S]*?\{/\* Overlay Clickaway Handler \*/\}',
    r'',
    content
)

# Remove Method 4: Google Account block
content = re.sub(
    r'\{/\* Method 4: Google Account \[B-Tier\] \*/\}[\s\S]*?\{/\* Method 5: Email & Password',
    r'{/* Method 5: Email & Password',
    content
)

# Remove Google Account Registration View
content = re.sub(
    r'\{/\* Google Account Registration \*/\}[\s\S]*?\{/\* WebAuthn / Passkeys Authentication Screen \*/\}',
    r'{/* WebAuthn / Passkeys Authentication Screen */}',
    content
)

with open('src/components/LoginScreen.tsx', 'w') as f:
    f.write(content)
