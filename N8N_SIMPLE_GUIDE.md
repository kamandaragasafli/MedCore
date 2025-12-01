# n8n Simple Guide for MedAdmin

## What is n8n?

**n8n** is a workflow automation tool (like Zapier, but open-source). It connects different services together and can process data.

## How n8n Works with MedAdmin

### Simple Explanation:

1. **User asks a question** in the chatbot (e.g., "How much debt does Dr. Ali have?")
2. **MedAdmin sends the question** to n8n webhook
3. **n8n processes it** (can use AI like OpenAI, Claude, etc.)
4. **n8n calls back to MedAdmin** to get database information
5. **n8n formats the answer** and sends it back
6. **User sees the answer** in the chatbot

### Visual Flow:

```
User → MedAdmin → n8n → AI Processing → MedAdmin Database API → n8n → MedAdmin → User
```

## Do You Need n8n?

**Short Answer**: Yes, if you want the AI chatbot to work.

**Why?**
- n8n acts as the "brain" that understands user questions
- It can use AI services (OpenAI, Anthropic, etc.) to understand natural language
- It processes the question and calls your database API to get real data

## Setting Up n8n

### Option 1: Use n8n Cloud (Easiest)
1. Go to https://n8n.io
2. Sign up for free account
3. Create a new workflow
4. Add a "Webhook" node
5. Copy the webhook URL
6. Paste it in MedAdmin settings: `N8N_WEBHOOK_URL`

### Option 2: Self-Host n8n (Advanced)
1. Install n8n on your server
2. Set up webhook
3. Configure it

## What You Need to Configure

### In MedAdmin (`config/settings.py`):
```python
N8N_WEBHOOK_URL = "https://your-n8n-instance.com/webhook/your-id"
N8N_API_KEY = ""  # Optional, if n8n requires authentication
```

### In n8n Workflow:
1. **Webhook Node**: Receives messages from MedAdmin
2. **AI Node** (OpenAI/Anthropic): Understands the question
3. **HTTP Request Node**: Calls MedAdmin API to get data
4. **Response Node**: Sends answer back to MedAdmin

## Example n8n Workflow

### Step 1: Webhook (Receive)
- Receives: `{"message": "Dr. Ali borcu?", "company_id": 1}`

### Step 2: AI Processing (Understand)
- Uses OpenAI/Claude to understand: "User wants doctor debt info"
- Extracts: `doctor_name: "Ali"`, `query_type: "doctor_debt"`

### Step 3: HTTP Request (Get Data)
- Calls: `POST /chatbot/api/query/`
- Sends: `{"query_type": "doctor_debt", "parameters": {"doctor_name": "Ali"}, "company_id": 1}`
- Gets: `{"data": {"message": "Dr. Ali borcu: 1500₼"}}`

### Step 4: Format Response
- Formats: "Dr. Ali həkiminin cari borcu 1500 manatdır."
- Sends back to MedAdmin

## If You Don't Want to Use n8n

You have two options:

### Option 1: Disable Chatbot Feature
- Remove chatbot from menu
- Users won't see it

### Option 2: Use Direct AI Integration
- Integrate OpenAI/Anthropic directly in Django
- More complex, but no n8n needed

## Current Setup

Your current n8n webhook URL is:
```
https://agsfli.app.n8n.cloud/webhook/c37e42bd-56c6-47a1-9f75-47b78923c2a6
```

This appears to be already configured. If it's working, you don't need to change anything!

## Testing n8n Connection

1. Go to chatbot page
2. Type a message
3. If you get a response, n8n is working!
4. If you get an error, check:
   - Is n8n webhook URL correct?
   - Is n8n workflow active?
   - Is n8n workflow configured correctly?

## Need Help?

- Check `N8N_INTEGRATION_GUIDE.md` for detailed technical setup
- n8n documentation: https://docs.n8n.io
- Test your webhook: Use Postman or curl to send test requests

