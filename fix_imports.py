with open('src/components/LoginScreen.tsx', 'r') as f:
    content = f.read()

import_str = "import { auth, googleProvider } from '../lib/firebase';\nimport { signInWithPopup } from 'firebase/auth';\n"
if "import { auth, googleProvider }" not in content:
    content = content.replace("import { supabaseClient } from '../lib/supabase';", import_str + "import { supabaseClient } from '../lib/supabase';")

with open('src/components/LoginScreen.tsx', 'w') as f:
    f.write(content)
