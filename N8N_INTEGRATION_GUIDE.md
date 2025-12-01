# n8n Integration Guide for MedAdmin AI Chatbot

## Overview

This guide explains how to integrate n8n with MedAdmin's AI Chatbot to enable database queries. The AI can answer questions like "How much debt did Abdullayev Huseyn have last month?" by querying the company's database.

## Architecture

```
User Message → Django Backend → n8n Webhook → AI Processing → Database Query API → Response → User
```

## Setup Steps

### 1. Configure n8n Webhook

In your n8n workflow:
1. Add a **Webhook** node to receive messages from MedAdmin
2. Set the webhook URL in MedAdmin settings: `N8N_WEBHOOK_URL`
3. Configure the webhook to accept POST requests with JSON

### 2. MedAdmin Sends to n8n

When a user sends a message, MedAdmin sends this JSON to your n8n webhook:

```json
{
  "message": "Abdullayev Huseyn həkiminin keçən ay borcu nə qədərdir?",
  "user_id": 1,
  "username": "user123",
  "company_id": 1,
  "company_name": "Company Name",
  "session_id": "session_key",
  "api_endpoint": "http://your-domain.com/chatbot/api/query/",
  "api_available": true
}
```

### 3. n8n Workflow Structure

Your n8n workflow should:

1. **Receive Webhook** - Get message from MedAdmin
2. **AI Processing** - Use OpenAI/Anthropic/etc. to understand the query
3. **Extract Intent** - Determine what data is needed
4. **Query Database API** - Call MedAdmin's query API
5. **Format Response** - Use AI to format the response
6. **Return to MedAdmin** - Send formatted response back

### 4. Database Query API

MedAdmin provides a query API endpoint that n8n can call:

**Endpoint**: `POST /chatbot/api/query/`

**Headers**:
```
Content-Type: application/json
```

**Request Body**:
```json
{
  "query_type": "doctor_debt",
  "parameters": {
    "doctor_name": "Abdullayev Huseyn",
    "month": 10,
    "year": 2025
  },
  "company_id": 1,
  "session_id": "session_key"
}
```

**Response**:
```json
{
  "success": true,
  "data": {
    "found": true,
    "doctor": {
      "name": "Abdullayev Huseyn",
      "code": "DOC001",
      "current_debt": 1500.50,
      "previous_debt": 1200.00
    },
    "archived_month": {
      "month": 10,
      "year": 2025,
      "final_debt": 1500.50
    },
    "message": "Abdullayev Huseyn həkiminin 2025 ilinin 10 ayındakı yekun borcu: 1500.50 ₼"
  }
}
```

## Available Query Types

### 1. `doctor_debt` - Get Doctor's Debt

**Parameters**:
- `doctor_name` (required): Doctor's name or code
- `month` (optional): Month number (1-12)
- `year` (optional): Year (e.g., 2025)

**Example Request**:
```json
{
  "query_type": "doctor_debt",
  "parameters": {
    "doctor_name": "Abdullayev Huseyn",
    "month": 10,
    "year": 2025
  },
  "company_id": 1
}
```

**Use Case**: "Abdullayev Huseyn həkiminin keçən ay borcu nə qədərdir?"

### 2. `doctor_info` - Get Doctor Information

**Parameters**:
- `doctor_name` (required): Doctor's name or code

**Example Request**:
```json
{
  "query_type": "doctor_info",
  "parameters": {
    "doctor_name": "Abdullayev Huseyn"
  },
  "company_id": 1
}
```

**Use Case**: "Abdullayev Huseyn həkiminin məlumatlarını göstər"

### 3. `prescription_count` - Get Prescription Count

**Parameters**:
- `doctor_name` (optional): Filter by doctor
- `month` (optional): Filter by month
- `year` (optional): Filter by year

**Example Request**:
```json
{
  "query_type": "prescription_count",
  "parameters": {
    "doctor_name": "Abdullayev Huseyn",
    "month": 11,
    "year": 2025
  },
  "company_id": 1
}
```

**Use Case**: "Bu ay neçə qeydiyyat var?"

### 4. `monthly_report` - Get Monthly Report Summary

**Parameters**:
- `month` (optional): Month number (defaults to current)
- `year` (optional): Year (defaults to current)

**Example Request**:
```json
{
  "query_type": "monthly_report",
  "parameters": {
    "month": 11,
    "year": 2025
  },
  "company_id": 1
}
```

**Use Case**: "Bu ayın hesabatını göstər"

### 5. `doctor_list` - Get List of Doctors

**Parameters**:
- `search` (optional): Search term
- `limit` (optional): Max results (default: 10)

**Example Request**:
```json
{
  "query_type": "doctor_list",
  "parameters": {
    "search": "Abdul",
    "limit": 5
  },
  "company_id": 1
}
```

**Use Case**: "Abdul adlı həkimləri göstər"

### 6. `recent_prescriptions` - Get Recent Prescriptions

**Parameters**:
- `limit` (optional): Number of results (default: 5)
- `doctor_name` (optional): Filter by doctor

**Example Request**:
```json
{
  "query_type": "recent_prescriptions",
  "parameters": {
    "limit": 5,
    "doctor_name": "Abdullayev Huseyn"
  },
  "company_id": 1
}
```

**Use Case**: "Son qeydiyyatları göstər"

### 7. `sales_summary` - Get Sales Summary

**Parameters**:
- `month` (optional): Filter by month
- `year` (optional): Filter by year

**Example Request**:
```json
{
  "query_type": "sales_summary",
  "parameters": {
    "month": 11,
    "year": 2025
  },
  "company_id": 1
}
```

**Use Case**: "Bu ayın satış gəlirini göstər"

## n8n Workflow Example

### Step 1: Webhook Node
- **Method**: POST
- **Path**: `/webhook/chatbot` (or your custom path)
- **Response Mode**: Respond to Webhook

### Step 2: AI Processing Node (OpenAI/Anthropic)
- **Prompt**: 
```
You are an AI assistant for MedAdmin, a medical management system.

User message: {{ $json.message }}

Determine what information the user is asking for and extract:
1. Query type (doctor_debt, doctor_info, prescription_count, monthly_report, doctor_list, recent_prescriptions, sales_summary)
2. Parameters needed (doctor_name, month, year, etc.)

Respond with JSON:
{
  "query_type": "...",
  "parameters": {
    "doctor_name": "...",
    "month": 11,
    "year": 2025
  },
  "needs_database_query": true/false
}
```

### Step 3: IF Node
- **Condition**: `{{ $json.needs_database_query }} === true`
- **If true**: Go to Database Query
- **If false**: Go to Direct Response

### Step 4: HTTP Request Node (Database Query)
- **Method**: POST
- **URL**: `{{ $json.api_endpoint }}` (from webhook data)
- **Body**:
```json
{
  "query_type": "{{ $json.query_type }}",
  "parameters": {{ $json.parameters }},
  "company_id": {{ $('Webhook').item.json.company_id }},
  "session_id": "{{ $('Webhook').item.json.session_id }}"
}
```

### Step 5: AI Format Response Node
- **Prompt**:
```
User asked: {{ $('Webhook').item.json.message }}

Database query result: {{ $json.data.message }}

Format a friendly, natural response in Azerbaijani language that answers the user's question using the database data.
```

### Step 6: Respond to Webhook
- **Response Body**:
```json
{
  "response": "{{ $json.formatted_response }}"
}
```

## Example Queries & Responses

### Query 1: "Abdullayev Huseyn həkiminin keçən ay borcu nə qədərdir?"

**n8n Processing**:
1. AI extracts: `query_type: "doctor_debt"`, `doctor_name: "Abdullayev Huseyn"`, `month: 10`, `year: 2025`
2. Calls API: `/chatbot/api/query/` with extracted parameters
3. Gets response: `{"message": "Abdullayev Huseyn həkiminin 2025 ilinin 10 ayındakı yekun borcu: 1500.50 ₼"}`
4. Formats response: "Abdullayev Huseyn həkiminin oktyabr ayındakı borcu 1500.50 manatdır."

### Query 2: "Bu ay neçə qeydiyyat var?"

**n8n Processing**:
1. AI extracts: `query_type: "prescription_count"`, `month: 11`, `year: 2025`
2. Calls API with parameters
3. Gets response: `{"count": 45, "message": "2025 ilinin 11 ayındakı ümumi qeydiyyat sayı: 45"}`
4. Formats: "Bu ay (noyabr) ümumilikdə 45 qeydiyyat qeydə alınıb."

### Query 3: "Ümumi həkim sayını göstər"

**n8n Processing**:
1. AI extracts: `query_type: "doctor_list"`, `limit: 1000`
2. Calls API
3. Gets response: `{"count": 25, "message": "25 həkim tapıldı."}`
4. Formats: "Sistemdə cəmi 25 həkim qeydiyyatdadır."

## Security Considerations

1. **Company Isolation**: The API automatically filters data by `company_id` - each company only sees its own data
2. **No Authentication Required**: The API uses `company_id` from the request (called by n8n, not directly by users)
3. **Session Validation**: Optional session validation can be added
4. **Rate Limiting**: Consider adding rate limiting for production

## Error Handling

The API returns errors in this format:
```json
{
  "success": false,
  "error": "Error message here"
}
```

Common errors:
- `company_id is required` - Missing company ID
- `Company not found` - Invalid company ID
- `doctor_name parameter is required` - Missing required parameter
- `Unknown query_type` - Invalid query type

## Testing

### Test with curl:

```bash
curl -X POST http://localhost:8000/chatbot/api/query/ \
  -H "Content-Type: application/json" \
  -d '{
    "query_type": "doctor_debt",
    "parameters": {
      "doctor_name": "Abdullayev Huseyn",
      "month": 10,
      "year": 2025
    },
    "company_id": 1
  }'
```

## Best Practices

1. **Cache Responses**: Cache frequently asked queries in n8n
2. **Error Messages**: Provide user-friendly error messages
3. **Timeout Handling**: Set appropriate timeouts for API calls
4. **Logging**: Log all queries for debugging
5. **Rate Limiting**: Implement rate limiting to prevent abuse

## Next Steps

1. Set up your n8n workflow following this guide
2. Test with sample queries
3. Fine-tune AI prompts for better understanding
4. Add more query types as needed
5. Monitor and optimize performance

---

**Note**: Make sure your n8n instance can reach your MedAdmin server's API endpoint. If MedAdmin is behind a firewall, you may need to configure network access.

