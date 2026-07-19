import re

with open('src/components/LoginScreen.tsx', 'r') as f:
    content = f.read()

# Let's remove the simulated google picker overlay
content = re.sub(r'\{/\* --- SIMULATED GOOGLE ACCOUNT PICKER OVERLAY ---\s*\*/\}.*?(?=</div>\n  \);\n})', '', content, flags=re.DOTALL)

with open('src/components/LoginScreen.tsx', 'w') as f:
    f.write(content)
