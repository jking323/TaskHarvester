# Azure AD App Registration Setup for TaskHarvester

This guide walks you through setting up Microsoft Azure Active Directory (Azure AD) app registration to enable TaskHarvester's Microsoft Graph OAuth integration.

## Prerequisites

- Azure AD tenant (Microsoft 365 or Azure subscription)
- Admin permissions to register applications in Azure AD
- Basic understanding of OAuth 2.0 and Microsoft Graph API

## Step 1: Create Azure AD App Registration

### 1.1 Navigate to Azure Portal
1. Go to [Azure Portal](https://portal.azure.com)
2. Sign in with your organizational account
3. Navigate to **Azure Active Directory** > **App registrations**
4. Click **"New registration"**

### 1.2 Configure Basic App Settings
Fill in the registration form:

**Name**: `TaskHarvester - Action Item Extractor`

**Supported account types**: Choose based on your needs:
- **Single tenant**: Only users in your organization
- **Multi-tenant**: Users in any organization (recommended for broader usage)
- **Personal + Work accounts**: Include personal Microsoft accounts

**Redirect URI**: 
- Platform: `Web`
- URI: `http://localhost:8000/api/auth/microsoft/callback`

> **Note**: For production, replace `localhost` with your actual domain

## Step 2: Configure Application Settings

### 2.1 Get Application Credentials
After creation, note these values from the **Overview** page:
- **Application (client) ID** → `MICROSOFT_CLIENT_ID`
- **Directory (tenant) ID** → `MICROSOFT_TENANT_ID`

### 2.2 Create Client Secret
1. Go to **Certificates & secrets** > **Client secrets**
2. Click **"New client secret"**
3. Add description: `TaskHarvester Production Secret`
4. Set expiration: `24 months` (recommended)
5. Copy the **Value** → `MICROSOFT_CLIENT_SECRET`

⚠️ **Important**: Copy the secret value immediately - it won't be shown again!

### 2.3 Configure Redirect URIs
1. Go to **Authentication**
2. Under **Web** platform, ensure you have:
   - Development: `http://localhost:8000/api/auth/microsoft/callback`
   - Production: `https://yourdomain.com/api/auth/microsoft/callback`
3. Enable **ID tokens** and **Access tokens** under **Implicit grant and hybrid flows**
4. **Advanced settings**:
   - ✅ Allow public client flows: `No`
   - ✅ Live SDK support: `No`

## Step 3: Configure API Permissions

### 3.1 Add Microsoft Graph Permissions
1. Go to **API permissions**
2. Click **"Add a permission"** > **Microsoft Graph** > **Delegated permissions**

**Required Permissions for TaskHarvester**:

#### Core Permissions (Required)
- `User.Read` - Read user profile
- `Mail.Read` - Read user mail
- `Mail.ReadWrite` - Read and update user mail
- `Calendars.Read` - Read user calendars
- `offline_access` - Maintain access to data

#### Teams Integration (Optional but Recommended)
- `ChannelMessage.Read.All` - Read all channel messages
- `Chat.Read` - Read user chat messages  
- `Team.ReadBasic.All` - Read basic team information
- `CallRecords.Read.All` - Read call records (for meeting transcripts)
- `OnlineMeetings.Read` - Read online meeting details

### 3.2 Grant Admin Consent
For organization-wide deployment:
1. Click **"Grant admin consent for [Your Organization]"**
2. Confirm the consent

> **Note**: This step may require Global Administrator privileges

## Step 4: Advanced Configuration

### 4.1 Enable Multi-Tenant Support (Optional)
If supporting multiple organizations:

1. **Authentication** > **Supported account types**:
   - Select "Accounts in any organizational directory"
2. **Manifest** > Edit the following:
   ```json
   {
     "signInAudience": "AzureADMultipleOrgs",
     "accessTokenAcceptedVersion": 2
   }
   ```

### 4.2 Configure Token Configuration (Recommended)
1. Go to **Token configuration**
2. Add **Optional claims** for ID tokens:
   - `email`
   - `family_name`
   - `given_name`
   - `preferred_username`

### 4.3 Set Up Conditional Access (Enterprise)
For enhanced security in enterprise environments:
1. Configure **Conditional Access** policies
2. Set up **Multi-Factor Authentication** requirements
3. Configure **Device compliance** policies

## Step 5: Environment Configuration

### 5.1 Update TaskHarvester Configuration
Add the following to your `.env` file:

```bash
# Microsoft Graph API Configuration
MICROSOFT_CLIENT_ID=your_application_client_id
MICROSOFT_CLIENT_SECRET=your_client_secret_value
MICROSOFT_TENANT_ID=your_tenant_id_or_common
MICROSOFT_REDIRECT_URI=http://localhost:8000/api/auth/microsoft/callback
```

### 5.2 Multi-Tenant Configuration
For multi-tenant apps, use:
```bash
MICROSOFT_TENANT_ID=common
```

For single-tenant apps, use your specific tenant ID:
```bash
MICROSOFT_TENANT_ID=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
```

## Step 6: Security Best Practices

### 6.1 Secret Management
- **Development**: Use environment variables or .env files
- **Production**: Use Azure Key Vault, AWS Secrets Manager, or similar
- **Rotation**: Rotate client secrets every 12-24 months

### 6.2 Redirect URI Security
- Use HTTPS in production
- Validate redirect URIs strictly
- Implement CSRF protection with state parameter

### 6.3 Scope Principle of Least Privilege
Only request permissions your application actually needs:

**Minimal Setup** (Email only):
- `User.Read`
- `Mail.Read`
- `offline_access`

**Full Featured** (Email + Teams):
- All permissions listed in Step 3.1

## Step 7: Testing Your Setup

### 7.1 Test Authentication Flow
1. Start TaskHarvester backend
2. Navigate to: `http://localhost:8000/api/auth/microsoft/login`
3. Complete OAuth flow
4. Verify token storage and API access

### 7.2 Validate Permissions
Test API endpoints:
```bash
# Check authentication status
curl http://localhost:8000/api/auth/status

# Test Microsoft Graph connection
curl -X POST http://localhost:8000/api/auth/test-connection \
  -H "Content-Type: application/json" \
  -d '{"provider": "microsoft"}'
```

## Troubleshooting

### Common Issues

**1. "AADSTS700054: response_type 'code' is not enabled"**
- Solution: Enable "ID tokens" in Authentication settings

**2. "AADSTS50011: The reply URL specified in the request does not match"**
- Solution: Verify redirect URI matches exactly (including trailing slashes)

**3. "AADSTS65001: The user or administrator has not consented"**
- Solution: Grant admin consent or implement user consent flow

**4. "Invalid client secret"**
- Solution: Regenerate client secret and update configuration

### Debug Mode
Enable debug logging in TaskHarvester:
```bash
DEBUG=true
LOG_LEVEL=DEBUG
```

## Production Deployment

### 1. Update Redirect URIs
Replace localhost with your production domain:
```
https://yourdomain.com/api/auth/microsoft/callback
```

### 2. SSL Certificate
Ensure HTTPS is properly configured with valid SSL certificate

### 3. Monitoring
Set up monitoring for:
- Authentication failures
- Token refresh failures
- API rate limits
- Permission changes

## Security Considerations

### Data Privacy
- **Local Processing**: TaskHarvester processes emails locally
- **Token Storage**: Tokens are encrypted in local database
- **No Data Transmission**: Email content stays on your infrastructure

### Compliance
This setup supports:
- **GDPR**: Data processing transparency
- **SOC 2**: Security controls and monitoring
- **HIPAA**: When properly configured with BAA

### Rate Limiting
Microsoft Graph API limits:
- **Per-app**: 10,000 requests per 10 minutes
- **Per-tenant**: 150,000 requests per 10 minutes
- **Throttling**: Implement exponential backoff

## Support

### Microsoft Resources
- [Microsoft Graph Documentation](https://docs.microsoft.com/en-us/graph/)
- [Azure AD App Registration Guide](https://docs.microsoft.com/en-us/azure/active-directory/develop/)
- [Microsoft Graph Explorer](https://developer.microsoft.com/en-us/graph/graph-explorer)

### TaskHarvester Support
- Check logs in `backend/logs/`
- Review authentication endpoints in `backend/src/api/auth.py`
- Test connection with `/api/auth/test-connection`

---

*Last updated: [Current Date]*
*Compatible with: TaskHarvester v0.1.0+*