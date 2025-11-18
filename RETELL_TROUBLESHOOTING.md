# Retell Widget - Troubleshooting 422 Error

## Current Errors

You're seeing:
```
422 error on api.retellai.com/create-chat
404 error on api.retellai.com/get-chat/undefined
```

## What These Mean

**422 Error** = Validation failed - Your credentials or agent configuration has an issue

**404 with "undefined"** = Widget can't find the chat session (caused by the 422 error)

## What I Fixed

✅ **Removed quotes from your `.env` keys**

**Before:**
```env
RETELL_PUBLIC_KEY="key_..."
RETELL_AGENT_ID="agent_..."
```

**After:**
```env
RETELL_PUBLIC_KEY=key_05be0a578ff6edc1d5577b879510
RETELL_AGENT_ID=agent_69ed3ebbd0f049ddf8198c043f
```

## What YOU Need To Verify

The 422 error suggests one of these issues:

### 1. Is Your Agent a CHAT Agent?

Go to [Retell Dashboard](https://dashboard.retellai.com/agents):

- Click on agent: `agent_69ed3ebbd0f049ddf8198c043f`
- **Check the type**: Must be **"Chat Agent"** NOT "Voice Agent"
- If it's a voice agent, you need to create a NEW chat agent

**How to create a Chat Agent:**
1. Go to https://dashboard.retellai.com/agents
2. Click "Create Agent"
3. Select **"Chat Agent"** (NOT voice agent)
4. Configure and save
5. Copy the new agent ID
6. Update `.env` with new agent ID

### 2. Is Your Public Key Valid?

Go to [Retell Public Keys](https://dashboard.retellai.com/settings/public-keys):

- Find key: `key_05be0a578ff6edc1d5577b879510`
- **Check status**: Must be "Active" or "Enabled"
- **Check permissions**: Must allow "Create Chat"
- If it doesn't exist or is disabled, create a new one

### 3. Is Your Agent Published/Active?

- Go to your agent settings
- Make sure it's **published** and **active**
- Check that it has a valid LLM configuration

## Common Causes of 422 Error

1. ❌ **Using Voice Agent ID instead of Chat Agent ID**
   - Voice agents are for phone calls
   - Chat agents are for text chat
   - They are NOT interchangeable!

2. ❌ **Public key is disabled or doesn't have permissions**
   - Check in dashboard settings
   - Enable "Create Chat" permission

3. ❌ **Agent is not published or configured**
   - Agent needs to be fully set up
   - LLM model must be selected
   - Agent must be in "Active" state

4. ❌ **Invalid agent version**
   - If you specified a version, make sure it exists
   - Or remove `data-agent-version` to use latest

## Testing Steps

After fixing any issues above:

1. **Update `.env`** with correct IDs
2. **Restart server**: `python app.py`
3. **Clear browser cache**: `Ctrl + Shift + Delete`
4. **Hard refresh**: `Ctrl + Shift + R`
5. **Check console** (F12) for new errors

## How to Verify Your Setup

In Retell Dashboard:

### Check Agent Type:
```
Dashboard → Agents → Click your agent
Look for: "Type: Chat Agent" (not Voice Agent)
```

### Check Public Key:
```
Dashboard → Settings → Public Keys
Find your key → Status should be "Active"
Permissions should include "Create Chat"
```

### Check Agent Status:
```
Your agent page should show:
- Status: Active
- LLM Model: (selected)
- Published: Yes
```

## If Still Not Working

Provide me with:
1. Screenshot of your agent page showing "Type"
2. Screenshot of your public key settings
3. Any new error messages from browser console

Then I can help debug further!

