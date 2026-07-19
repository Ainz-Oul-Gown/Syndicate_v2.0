import re

with open('src/components/LoginScreen.tsx', 'r') as f:
    content = f.read()

content = re.sub(r'\{/\* --- SIMULATED GOOGLE ACCOUNT PICKER OVERLAY ---\s*\*/\}[\s\S]*?\{/\* Overlay Clickaway Handler \*/\}', '{/* Overlay Clickaway Handler */}', content)

with open('src/components/LoginScreen.tsx', 'w') as f:
    f.write(content)
