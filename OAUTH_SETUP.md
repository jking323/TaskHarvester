# OAuth Setup Guide for TaskHarvester

## Azure AD App Registration Setup

### 1. Create App Registration
1. Go to [Azure Portal](https://portal.azure.com)
2. Navigate to **Azure Active Directory** > **App registrations** > **New registration**
3. Configure:
   - **Name**: `TaskHarvester`
   - **Supported account types**: **Accounts in any organizational directory and personal Microsoft accounts (Multitenant and personal accounts)**
   - **Redirect URI**: Web → `http://localhost:8000/api/auth/microsoft/callback`

### 2. Configure Authentication
1. In your app registration, go to **Authentication**
2. Under **Platform configurations**, click **Add a platform** > **Web**
3. Add redirect URI: `http://localhost:8000/api/auth/microsoft/callback`
4. Under **Advanced settings**:
   - ✅ Enable **Access tokens**
   - ✅ Enable **ID tokens**
   - ✅ Enable **Allow public client flows**

### 3. Set API Permissions
1. Go to **API permissions** > **Add a permission** > **Microsoft Graph** > **Delegated permissions**
2. Add these permissions:
   - `User.Read` - Read user profile
   - `Mail.Read` - Read user mail
   - `Mail.ReadWrite` - Read and write access to user mail
   - `Calendars.Read` - Read user calendars
   - `offline_access` - Maintain access to data
3. Click **Grant admin consent for [Your Tenant]**

### 4. Create Client Secret
1. Go to **Certificates & secrets** > **Client secrets** > **New client secret**
2. Add description: "TaskHarvester Backend Secret"
3. Set expiration: 24 months (or your preference)
4. **Copy the secret value immediately** - you won't be able to see it again!

### 5. Configure Doppler Secrets
Set these environment variables in Doppler:

```bash
# Required OAuth Configuration
MICROSOFT_CLIENT_ID=your-application-client-id-here
MICROSOFT_CLIENT_SECRET=your-client-secret-here
MICROSOFT_TENANT_ID=common  # Use 'common' for multi-tenant support
MICROSOFT_REDIRECT_URI=http://localhost:8000/api/auth/microsoft/callback

# Database Configuration
DATABASE_URL=sqlite:///./action_items.db

# AI Configuration
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=gpt-oss:20b
AI_CONFIDENCE_THRESHOLD=0.7

# Security Configuration
SECRET_KEY=your-secret-key-for-jwt-here-make-it-long-and-random
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Application Configuration
DEBUG=true
LOG_LEVEL=INFO
```

### 6. Test Multi-tenant Access
The app should now work with:
- Personal Microsoft accounts (@outlook.com, @hotmail.com, @live.com)
- Work or school accounts from any organization
- Azure AD B2C accounts

### 7. Common Issues & Solutions

#### "User account does not exist in tenant"
- **Problem**: App is configured for single-tenant only
- **Solution**: Change **Supported account types** to "Multitenant and personal accounts"

#### "AADSTS50011: Redirect URI mismatch"
- **Problem**: Redirect URI doesn't match exactly
- **Solution**: Ensure URI in Azure AD exactly matches: `http://localhost:8000/api/auth/microsoft/callback`

#### "AADSTS65001: User or administrator has not consented"
- **Problem**: Permissions not granted
- **Solution**: Grant admin consent for permissions in Azure AD

#### "Invalid client secret"
- **Problem**: Client secret expired or incorrect
- **Solution**: Generate new client secret and update Doppler

### 8. Production Considerations
For production deployment:
- Use HTTPS redirect URIs
- Store secrets securely (Azure Key Vault, AWS Secrets Manager)
- Implement proper session management
- Add rate limiting
- Use Redis for OAuth state storage
- Enable logging and monitoring