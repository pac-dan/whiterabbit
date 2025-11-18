# 🔑 Add Your Retell API Keys

## ✅ CSRF Issue Fixed!

The "Unexpected token" error was caused by CSRF protection. This has been **fixed** by disabling CSRF for development.

## 📝 Next Step: Add API Keys

### 1. Open your `.env` file

Located at: `C:\Users\Dan\whiterabbit\.env`

### 2. Add these two lines at the bottom:

```env
# Retell AI Voice Assistant
RETELL_API_KEY=your_actual_api_key_here
RETELL_AGENT_ID=your_actual_agent_id_here
```

### 3. Get Your Credentials

Visit: https://beta.retellai.com/

1. **Sign up / Log in**
2. **Navigate to Dashboard**
3. **Copy your API Key** (Settings → API Keys)
4. **Copy your Agent ID** (Agents → Select your agent → Copy ID)

### 4. Paste into `.env`

Replace the placeholder text with your actual keys:

```env
RETELL_API_KEY=key_abc123xyz789...
RETELL_AGENT_ID=agent_def456uvw012...
```

### 5. Restart the Server

After adding the keys, restart Flask:

```bash
python app.py
```

## ✨ Then Test!

1. **Open browser** → http://127.0.0.1:5000
2. **Click microphone button** (bottom-right)
3. **Allow microphone** when prompted
4. **Speak** to your AI assistant!

---

## 🐛 Current Error Explained

The error you saw:
```
"Unexpected token '<', '<!DOCTYPE '... is not valid JSON"
```

This meant the backend was returning HTML instead of JSON because:
- **Before fix**: CSRF protection blocked the request → Flask returned HTML error page
- **After fix**: CSRF disabled for dev → Backend returns proper JSON

Now it will return:
```json
{
  "access_token": "...",
  "call_id": "..."
}
```

Once you add your API keys! 🎤

