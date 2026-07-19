import re

with open('src/components/LoginScreen.tsx', 'r') as f:
    content = f.read()

content = re.sub(r"const \[showGoogleOverlay, setShowGoogleOverlay\] = useState\(false\);\n?", "", content)
content = re.sub(r"const \[googleAction, setGoogleAction\] = useState<'login' \| 'register'>\('login'\);\n?", "", content)
content = re.sub(r"const \[customGoogleEmail, setCustomGoogleEmail\] = useState\(''\);\n?", "", content)
content = re.sub(r"const \[customGoogleName, setCustomGoogleName\] = useState\(''\);\n?", "", content)
content = re.sub(r"const \[isGoogleCustomOpen, setIsGoogleCustomOpen\] = useState\(false\);\n?", "", content)

# Remove handleGoogleAccountSelect block completely
content = re.sub(r"// Google Account - Handle simulated account select[\s\S]*?(?=// Telegram Auth State & Logic)", "", content)

with open('src/components/LoginScreen.tsx', 'w') as f:
    f.write(content)
