# TaskHarvester Quick Start Demo Guide

## Prerequisites Checklist
- [ ] Python 3.9+ installed
- [ ] Ollama installed and running (http://localhost:11434)
- [ ] Llama 3.1 8B model pulled in Ollama: `ollama pull llama3.1:8b`
- [ ] Azure AD app registration completed
- [ ] .env file configured with Azure credentials

## Step 1: Azure AD Setup (5-10 minutes)

1. Go to [Azure Portal](https://portal.azure.com)
2. Navigate to **Azure Active Directory** > **App registrations** > **New registration**
3. Configure:
   - Name: `TaskHarvester Demo`
   - Account types: **Accounts in any organizational directory (Multi-tenant)**
   - Redirect URI: Web → `http://localhost:8000/api/auth/microsoft/callback`
4. After creation, copy:
   - **Application (client) ID** → Update `MICROSOFT_CLIENT_ID` in .env
   - **Directory (tenant) ID** → Update `MICROSOFT_TENANT_ID` in .env (or keep as 'common')
5. Go to **Certificates & secrets** > **New client secret**:
   - Copy the **Value** → Update `MICROSOFT_CLIENT_SECRET` in .env
6. Go to **API permissions** > **Add permission** > **Microsoft Graph** > **Delegated**:
   - Add: `User.Read`, `Mail.Read`, `Mail.ReadWrite`, `offline_access`
   - Click **Grant admin consent** (if you're an admin)

## Step 2: Install & Start Backend (2 minutes)

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start the server
python -m uvicorn src.main:app --reload --port 8000
```

## Step 3: Verify Ollama is Running

```bash
# In a new terminal, check Ollama status
curl http://localhost:11434/api/tags

# If not running, start Ollama:
ollama serve

# Pull the model if needed:
ollama pull llama3.1:8b
```

## Step 4: Test the Demo

### 4.1 Check API Health
Open browser: http://localhost:8000/docs
- Test the `/health` endpoint

### 4.2 Authenticate with Microsoft
1. Go to: http://localhost:8000/api/auth/microsoft/login
2. Copy the `auth_url` from the response
3. Open it in your browser
4. Sign in with your Microsoft account
5. After redirect, copy the `code` and `state` from the URL

### 4.3 Complete Authentication
Use the API docs to call POST `/api/auth/microsoft/callback` with:
```json
{
  "code": "YOUR_CODE_HERE",
  "state": "YOUR_STATE_HERE",
  "code_verifier": "YOUR_CODE_VERIFIER_HERE"
}
```

### 4.4 Test Email Processing
1. Check auth status: GET `/api/auth/status`
2. Fetch recent emails: GET `/api/emails/recent?days_back=7&max_emails=10`
3. Process for action items: POST `/api/emails/process-for-actions`
   ```json
   {
     "days_back": 7,
     "max_emails": 5,
     "filter_unread": false
   }
   ```

### 4.5 Test AI Extraction Directly
POST `/api/ai/test-extraction`
```json
{
  "content": "Hi team, Please review the Q4 report by Friday. John needs to update the budget spreadsheet. Sarah should schedule a meeting with the client next week.",
  "source_type": "email",
  "source_id": "test-123"
}
```

## Expected Demo Flow

1. **OAuth Authentication** ✓
   - User authenticates with Microsoft
   - Token stored securely

2. **Email Fetching** ✓
   - Fetch recent emails from Outlook
   - Display email metadata

3. **AI Processing** ✓
   - Extract action items from email content
   - Show confidence scores and assignees

4. **Action Items Display** ✓
   - List all extracted action items
   - Show source email and context

## Troubleshooting

### "Microsoft authentication failed"
- Check your Azure AD credentials in .env
- Ensure redirect URI matches exactly
- Verify API permissions are granted

### "Ollama not responding"
- Start Ollama: `ollama serve`
- Check it's running: `curl http://localhost:11434/api/tags`
- Pull model: `ollama pull llama3.1:8b`

### "No emails found"
- Ensure you have emails in your inbox from the last 7 days
- Check Microsoft Graph permissions
- Try with `filter_unread: false`

## Demo Script

1. "Let me show you TaskHarvester - it automatically extracts action items from emails"
2. "First, we authenticate with Microsoft" (show OAuth flow)
3. "Now let's fetch recent emails" (show email list)
4. "Watch as AI processes these emails for action items" (run processing)
5. "Here are all the action items found, with assignees and deadlines"
6. "Each item has a confidence score - we can filter by threshold"
7. "In production, these would auto-create tasks in Wrike"

## Next Steps After Demo

- [ ] Add Wrike integration for task creation
- [ ] Build Electron UI for better UX
- [ ] Add Teams message processing
- [ ] Implement background email monitoring
- [ ] Add user preferences and filtering rules