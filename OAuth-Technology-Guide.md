# OAuth Technology Guide

## Table of Contents
- [What is OAuth](#what-is-oauth)
- [OAuth 2.0 Core Concepts](#oauth-20-core-concepts)
- [OAuth 2.0 Authorization Flow](#oauth-20-authorization-flow)
- [Grant Types](#grant-types)
- [OAuth Token Types](#oauth-token-types)
- [Security Best Practices](#security-best-practices)
- [Common Use Cases](#common-use-cases)
- [Code Examples](#code-examples)

## What is OAuth

OAuth (Open Authorization) is an open standard protocol that allows users to authorize third-party applications to access their information stored on another service provider without providing their username and password to the third-party application.

### Key Features

1. **Security**: Users don't need to provide passwords to third-party applications
2. **Authorization Control**: Users can control the scope and duration of authorization
3. **Standardization**: Widely adopted industry standard
4. **Flexibility**: Supports multiple authorization scenarios

### OAuth 1.0 vs OAuth 2.0

- **OAuth 1.0**: Released in 2007, more complex, requires signature mechanism
- **OAuth 2.0**: Released in 2012, simplified process, easier to implement, current mainstream version

## OAuth 2.0 Core Concepts

### Four Roles

1. **Resource Owner**
   - Usually the user
   - Owns the accessed resources

2. **Client**
   - Third-party application
   - Requests access to the resource owner's protected resources

3. **Authorization Server**
   - Verifies the resource owner's identity
   - Issues access tokens

4. **Resource Server**
   - Server hosting protected resources
   - Validates access tokens and provides resources

### Core Terms

- **Access Token**: Credential used to access protected resources
- **Refresh Token**: Used to obtain new access tokens
- **Scope**: Defines the range of access permissions
- **Redirect URI**: Address to redirect to after authorization

## OAuth 2.0 Authorization Flow

### Basic Flow

```
+--------+                               +---------------+
|        |--(A)- Authorization Request ->|   Resource    |
|        |                               |     Owner     |
|        |<-(B)-- Authorization Grant ---|               |
|        |                               +---------------+
|        |
|        |                               +---------------+
|        |--(C)-- Authorization Grant -->| Authorization |
| Client |                               |     Server    |
|        |<-(D)----- Access Token -------|               |
|        |                               +---------------+
|        |
|        |                               +---------------+
|        |--(E)----- Access Token ------>|    Resource   |
|        |                               |     Server    |
|        |<-(F)--- Protected Resource ---|               |
+--------+                               +---------------+
```

### Detailed Steps

1. **Authorization Request**: Client requests authorization from resource owner
2. **Authorization Grant**: Resource owner approves authorization
3. **Token Request**: Client requests access token from authorization server
4. **Token Issued**: Authorization server issues access token after verification
5. **Resource Access**: Client uses access token to access resource server
6. **Resource Return**: Resource server validates token and returns protected resource

## Grant Types

### 1. Authorization Code Grant

**Most secure and commonly used**, suitable for applications with backend servers.

**Flow:**
1. Client redirects user to authorization server
2. User logs in and authorizes
3. Authorization server returns authorization code
4. Client exchanges authorization code for access token

**Use Cases:** Web applications, mobile apps

**Example Request:**
```
GET /authorize?
    response_type=code&
    client_id=CLIENT_ID&
    redirect_uri=REDIRECT_URI&
    scope=read_user&
    state=RANDOM_STRING
```

### 2. Implicit Grant

**Simplified flow**, returns access token directly without authorization code.

**Flow:**
1. Client redirects user to authorization server
2. User logs in and authorizes
3. Authorization server returns access token directly (in URL fragment)

**Use Cases:** Pure frontend applications (Single Page Applications)

**Note:** Lower security, no longer recommended in OAuth 2.1

### 3. Resource Owner Password Credentials Grant

**Directly uses username and password** to exchange for access token.

**Flow:**
1. User provides username and password to client
2. Client uses these credentials to request token from authorization server

**Use Cases:** Highly trusted applications (e.g., official apps)

**Note:** Violates OAuth principles, deprecated in OAuth 2.1

### 4. Client Credentials Grant

**Application-to-application** authorization, doesn't involve users.

**Flow:**
1. Client uses its own credentials to request token from authorization server
2. Authorization server validates and issues token

**Use Cases:** Backend services, API calls, microservice communication

**Example Request:**
```
POST /token
Content-Type: application/x-www-form-urlencoded

grant_type=client_credentials&
client_id=CLIENT_ID&
client_secret=CLIENT_SECRET
```

### 5. Device Authorization Flow

**Designed for input-constrained devices**.

**Use Cases:** Smart TVs, game consoles, IoT devices

## OAuth Token Types

### Access Token

- **Purpose**: Access protected resources
- **Characteristics**:
  - Short validity period (typically minutes to hours)
  - Can be opaque token or JWT
  - Should be transmitted via HTTPS

### Refresh Token

- **Purpose**: Obtain new access tokens
- **Characteristics**:
  - Longer validity period (days, weeks, months)
  - Must be stored securely
  - Can be revoked

### ID Token

- **Purpose**: Provides user identity information
- **Characteristics**:
  - OpenID Connect standard
  - Must be JWT format
  - Contains user identity claims

## Security Best Practices

### 1. Use HTTPS

All OAuth communications must be over HTTPS to prevent token theft.

### 2. Validate Redirect URI

Strictly validate redirect URIs to prevent authorization code hijacking.

```python
# Insecure redirect URI validation
if redirect_uri.startswith(registered_uri):
    # Not strict enough

# Secure redirect URI validation
if redirect_uri == registered_uri:
    # Exact match
```

### 3. Use State Parameter

Prevent CSRF attacks.

```javascript
// Generate random state
const state = generateRandomString();
sessionStorage.setItem('oauth_state', state);

// Authorization request
window.location = `${authUrl}?client_id=${clientId}&state=${state}`;

// Callback validation
const returnedState = new URLSearchParams(window.location.search).get('state');
if (returnedState !== sessionStorage.getItem('oauth_state')) {
    throw new Error('Invalid state parameter');
}
```

### 4. Use PKCE

**Proof Key for Code Exchange**, enhances security of authorization code flow.

```python
import hashlib
import base64
import secrets

# Generate code_verifier
code_verifier = base64.urlsafe_b64encode(secrets.token_bytes(32)).decode('utf-8').rstrip('=')

# Generate code_challenge
code_challenge = base64.urlsafe_b64encode(
    hashlib.sha256(code_verifier.encode('utf-8')).digest()
).decode('utf-8').rstrip('=')
```

### 5. Limit Token Scope

Only request necessary permission ranges.

```
# Bad practice
scope=read write delete admin

# Good practice
scope=read_user read_email
```

### 6. Token Storage

- **Access Token**: Can be stored in memory
- **Refresh Token**: Must be stored securely (e.g., HttpOnly Cookie, encrypted storage)
- **Don't**: Store in localStorage (vulnerable to XSS attacks)

### 7. Token Revocation

Implement token revocation mechanism, allowing users to revoke authorization anytime.

```
POST /revoke
Content-Type: application/x-www-form-urlencoded

token=ACCESS_TOKEN&
token_type_hint=access_token
```

## Common Use Cases

### 1. Third-Party Login

Allow users to log in using accounts from GitHub, Google, WeChat, etc.

**Example: Login with GitHub**
```
# Step 1: Redirect to GitHub authorization page
https://github.com/login/oauth/authorize?
    client_id=YOUR_CLIENT_ID&
    redirect_uri=YOUR_CALLBACK_URL&
    scope=user:email

# Step 2: GitHub returns authorization code
YOUR_CALLBACK_URL?code=AUTHORIZATION_CODE

# Step 3: Exchange authorization code for access token
POST https://github.com/login/oauth/access_token
Content-Type: application/json

{
    "client_id": "YOUR_CLIENT_ID",
    "client_secret": "YOUR_CLIENT_SECRET",
    "code": "AUTHORIZATION_CODE"
}
```

### 2. API Access Authorization

Authorize third-party applications to access user's API resources.

**Example: Access user's Google Drive**
```
scope=https://www.googleapis.com/auth/drive.readonly
```

### 3. Microservice Authentication

Use client credentials grant for secure inter-service communication.

### 4. Mobile App Authorization

Use authorization code flow + PKCE to protect mobile applications.

## Code Examples

### Python Example (using requests-oauthlib)

```python
from requests_oauthlib import OAuth2Session

# Configuration
client_id = 'YOUR_CLIENT_ID'
client_secret = 'YOUR_CLIENT_SECRET'
authorization_base_url = 'https://provider.com/oauth/authorize'
token_url = 'https://provider.com/oauth/token'
redirect_uri = 'https://yourapp.com/callback'

# Step 1: Get authorization URL
oauth = OAuth2Session(client_id, redirect_uri=redirect_uri, scope=['read', 'write'])
authorization_url, state = oauth.authorization_url(authorization_base_url)
print(f'Please visit this URL to authorize: {authorization_url}')

# Step 2: After user authorization, get authorization response from callback URL
authorization_response = 'https://yourapp.com/callback?code=...'

# Step 3: Get access token
token = oauth.fetch_token(
    token_url,
    authorization_response=authorization_response,
    client_secret=client_secret
)

# Step 4: Use access token to access protected resources
response = oauth.get('https://api.provider.com/user')
user_data = response.json()
print(f'User data: {user_data}')
```

### JavaScript Example (Node.js + Express)

```javascript
const express = require('express');
const axios = require('axios');
const crypto = require('crypto');

const app = express();
const port = 3000;

// OAuth configuration
const config = {
    clientId: 'YOUR_CLIENT_ID',
    clientSecret: 'YOUR_CLIENT_SECRET',
    authorizationUrl: 'https://provider.com/oauth/authorize',
    tokenUrl: 'https://provider.com/oauth/token',
    redirectUri: 'http://localhost:3000/callback',
    scope: 'read write'
};

// Store state (production should use database or Redis for distributed systems)
// In-memory storage is only suitable for single-server development environments
// For production with multiple server instances, use Redis or a distributed cache
// Note: Implement state expiration/cleanup to prevent memory leaks
const stateStore = new Map();

// Step 1: Redirect to authorization page
app.get('/login', (req, res) => {
    const state = crypto.randomBytes(16).toString('hex');
    stateStore.set(state, Date.now());
    
    const authUrl = `${config.authorizationUrl}?` +
        `response_type=code&` +
        `client_id=${config.clientId}&` +
        `redirect_uri=${encodeURIComponent(config.redirectUri)}&` +
        `scope=${encodeURIComponent(config.scope)}&` +
        `state=${state}`;
    
    res.redirect(authUrl);
});

// Step 2: Handle callback
app.get('/callback', async (req, res) => {
    const { code, state } = req.query;
    
    // Validate state
    if (!stateStore.has(state)) {
        return res.status(400).send('Invalid state parameter');
    }
    stateStore.delete(state);
    
    try {
        // Step 3: Exchange access token
        const tokenResponse = await axios.post(config.tokenUrl, {
            grant_type: 'authorization_code',
            code: code,
            redirect_uri: config.redirectUri,
            client_id: config.clientId,
            client_secret: config.clientSecret
        });
        
        const { access_token, refresh_token } = tokenResponse.data;
        
        // Step 4: Use access token to get user info
        const userResponse = await axios.get('https://api.provider.com/user', {
            headers: {
                'Authorization': `Bearer ${access_token}`
            }
        });
        
        res.json({
            message: 'Authorization successful',
            user: userResponse.data
        });
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

app.listen(port, () => {
    console.log(`Server running at http://localhost:${port}`);
});
```

### Go Example

```go
package main

import (
    "context"
    "crypto/rand"
    "encoding/base64"
    "fmt"
    "golang.org/x/oauth2"
    "log"
    "net/http"
    "time"
)

var (
    oauthConfig = &oauth2.Config{
        ClientID:     "YOUR_CLIENT_ID",
        ClientSecret: "YOUR_CLIENT_SECRET",
        RedirectURL:  "http://localhost:8080/callback",
        Scopes:       []string{"read", "write"},
        Endpoint: oauth2.Endpoint{
            AuthURL:  "https://provider.com/oauth/authorize",
            TokenURL: "https://provider.com/oauth/token",
        },
    }
    // In production, store state in secure storage like Redis or database
    // Implement expiration to prevent memory leaks
    stateStore = make(map[string]int64)
)

func main() {
    http.HandleFunc("/login", handleLogin)
    http.HandleFunc("/callback", handleCallback)
    
    log.Println("Server started on :8080")
    log.Fatal(http.ListenAndServe(":8080", nil))
}

func handleLogin(w http.ResponseWriter, r *http.Request) {
    // Generate cryptographically secure random state
    b := make([]byte, 16)
    rand.Read(b)
    state := base64.URLEncoding.EncodeToString(b)
    
    // Store state (use Redis/database in production for distributed systems)
    stateStore[state] = time.Now().Unix()
    
    url := oauthConfig.AuthCodeURL(state)
    http.Redirect(w, r, url, http.StatusTemporaryRedirect)
}

func handleCallback(w http.ResponseWriter, r *http.Request) {
    state := r.FormValue("state")
    
    // Validate state
    if _, exists := stateStore[state]; !exists {
        http.Error(w, "Invalid state parameter", http.StatusBadRequest)
        return
    }
    delete(stateStore, state)
    
    code := r.FormValue("code")
    token, err := oauthConfig.Exchange(context.Background(), code)
    if err != nil {
        http.Error(w, "Failed to exchange token: "+err.Error(), http.StatusInternalServerError)
        return
    }
    
    client := oauthConfig.Client(context.Background(), token)
    resp, err := client.Get("https://api.provider.com/user")
    if err != nil {
        http.Error(w, "Failed to get user info: "+err.Error(), http.StatusInternalServerError)
        return
    }
    defer resp.Body.Close()
    
    fmt.Fprintf(w, "Authorization successful! Access token: %s", token.AccessToken)
}
```

## Summary

OAuth 2.0 is an essential authorization framework for modern applications, providing:

✅ **Security**: No need to share passwords  
✅ **Flexibility**: Supports multiple authorization scenarios  
✅ **Standardization**: Wide industry support  
✅ **User Control**: Fine-grained permission management  

### Key Takeaways

1. Always use HTTPS
2. Choose appropriate grant type
3. Implement security best practices (PKCE, State validation, etc.)
4. Limit token scope
5. Securely store and transmit tokens
6. Implement token refresh and revocation mechanisms

### Reference Resources

- [RFC 6749: OAuth 2.0 Framework](https://tools.ietf.org/html/rfc6749)
- [RFC 6750: OAuth 2.0 Bearer Token](https://tools.ietf.org/html/rfc6750)
- [RFC 7636: PKCE](https://tools.ietf.org/html/rfc7636)
- [OAuth 2.0 Security Best Practices](https://tools.ietf.org/html/draft-ietf-oauth-security-topics)
- [OpenID Connect](https://openid.net/connect/)

---

**Last Updated:** 2026-02-01
