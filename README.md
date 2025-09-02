# 🚀 Custom Entity Extraction Agent

> **Extract meaningful business insights from your data using AI!**

## 🎯 What is This?

Imagine you have a smart assistant that can look at your business data and automatically find **new, valuable insights** that weren't obvious before. That's exactly what this Custom Entity Extraction Agent does!

### 🌟 In Simple Terms:
- **Input**: You give it some business data (like customer information, credit scores, account details)
- **AI Magic**: It analyzes this data and finds **new patterns, relationships, and insights**
- **Output**: You get **new business entities** that help you make better decisions

## 🏗️ How It Works (Simple Explanation)

### 1. **Data Selection** 📊
You pick which pieces of data you want the AI to analyze:
- **BC3 Fields**: Business rules and definitions (like "Credit Score", "Account Number")
- **Asset Columns**: Actual data from your databases (like customer credit scores, account balances)

### 2. **AI Analysis** 🤖
The AI looks at your selected data and thinks:
- "What new insights can I find here?"
- "What relationships exist between these data points?"
- "What business rules can I create?"

### 3. **Entity Extraction** ✨
The AI creates **new entities** like:
- **Credit Risk Score** (combining credit score + debt + limit)
- **Account Health Status** (based on multiple factors)
- **Risk Alerts** (when certain conditions are met)

## 🛠️ Tech Stack

- **Backend**: FastAPI (Python web framework)
- **AI Engine**: Google Vertex AI (Gemini 2.5 Flash Lite)
- **Workflow**: LangGraph (AI workflow management)
- **Session Storage**: In-memory (can be changed to Firestore, Redis, MongoDB)
- **Frontend Demo**: Streamlit (for testing)

## 🚀 Quick Start

### 1. **Install Dependencies**
```bash
# Create virtual environment
python -m venv .venv

# Activate it
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install packages
pip install -r requirements.txt
```

### 2. **Set Up Google Cloud**
```bash
# Set your Google Cloud project
export GOOGLE_CLOUD_PROJECT="your-project-id"
export GOOGLE_APPLICATION_CREDENTIALS="path/to/your/service-account-key.json"
```

### 3. **Start the Backend**
```bash
python main.py --port 8001
```

### 4. **Test the API**
```bash
curl http://localhost:8001/health
```

## 📡 API Endpoints

### 🔍 **Health Check**
```http
GET /health
```
**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-09-01T23:30:00.000000",
  "version": "2.0.0"
}
```

### 💬 **Chat with Agent**
```http
POST /chat
```

**Request Body:**
```json
{
  "message": "Extract meaningful entities from the selected context",
  "session_id": "user_session_123",
  "selected_bc3_fields": [
    {
      "field": {
        "description": "Credit Score",
        "definition": "A numerical representation of creditworthiness",
        "known_implementations": ["FICO", "VantageScore"],
        "valid_values": ["300-850"],
        "notes": "Higher scores indicate better credit"
      },
      "segment_context": {
        "segment_name": "Credit Accounts"
      }
    }
  ],
  "selected_asset_columns": [
    {
      "column": {
        "column_name": "credit_score",
        "data_type": "INTEGER",
        "description": "Customer credit score"
      },
      "asset_context": {
        "asset_name": "Credit Database",
        "workspace_name": "Financial Data",
        "big_query_table_name": "credit.credit_scores"
      }
    }
  ]
}
```

**Response:**
```json
{
  "response": "EXTRACTED ENTITIES:\n1. Derived Business Metric: Credit Risk Score...",
  "extracted_entities": [
    {
      "entity_type": "metadata",
      "entity_name": "Credit Risk Score",
      "entity_value": "[Calculated Value]",
      "confidence": 0.9,
      "source_field": "credit_score (Credit Database)",
      "description": "Combined risk assessment based on credit score and utilization",
      "context_provider": "credit_domain"
    }
  ],
  "chat_state": {...},
  "confidence_score": 0.9,
  "processing_time": 2.34,
  "metadata": {"session_id": "user_session_123"}
}
```

### 📊 **Get Session Entities**
```http
GET /entities/{session_id}
```

**Response:**
```json
{
  "session_id": "user_session_123",
  "total_entities": 2,
  "entities": [
    {
      "entity_number": 1,
      "entity_type": "metadata",
      "entity_name": "Credit Risk Score",
      "entity_value": "[Calculated Value]",
      "confidence": 0.9,
      "source_field": "credit_score (Credit Database)",
      "description": "Combined risk assessment based on credit score and utilization",
      "context_provider": "credit_domain"
    }
  ],
  "timestamp": "2025-09-01T23:30:00.000000"
}
```

### 📋 **Get Context Providers**
```http
GET /context-providers
```

**Response:**
```json
{
  "context_providers": [
    {
      "name": "credit_domain",
      "description": "Credit Domain (BC3) data structures with business dictionary",
      "features": ["Segment analysis", "Business dictionary extraction", "Field validation", "Implementation mapping"]
    }
  ]
}
```

### 📝 **Get Logs**
```http
GET /logs?lines=50
```

**Response:**
```json
{
  "log_file": "fastapi.log",
  "total_lines": 150,
  "recent_lines": ["2025-09-01 23:30:00 - INFO - Request processed..."],
  "timestamp": "2025-09-01T23:30:00.000000"
}
```

## 🎨 Frontend Integration Guide

### **React Example**

#### 1. **Install Dependencies**
```bash
npm install axios
```

#### 2. **Create API Service**
```javascript
// services/entityAgent.js
import axios from 'axios';

const API_BASE_URL = 'http://localhost:8001';

export const entityAgentAPI = {
  // Health check
  checkHealth: () => axios.get(`${API_BASE_URL}/health`),
  
  // Chat with agent
  chat: (payload) => axios.post(`${API_BASE_URL}/chat`, payload),
  
  // Get session entities
  getEntities: (sessionId) => axios.get(`${API_BASE_URL}/entities/${sessionId}`),
  
  // Get context providers
  getContextProviders: () => axios.get(`${API_BASE_URL}/context-providers`)
};
```

#### 3. **Create Chat Component**
```jsx
// components/EntityChat.jsx
import React, { useState, useEffect } from 'react';
import { entityAgentAPI } from '../services/entityAgent';

const EntityChat = () => {
  const [message, setMessage] = useState('');
  const [selectedBC3Fields, setSelectedBC3Fields] = useState([]);
  const [selectedAssetColumns, setSelectedAssetColumns] = useState([]);
  const [entities, setEntities] = useState([]);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    
    try {
      const payload = {
        message,
        session_id: `session_${Date.now()}`,
        selected_bc3_fields: selectedBC3Fields,
        selected_asset_columns: selectedAssetColumns
      };
      
      const response = await entityAgentAPI.chat(payload);
      setEntities(response.data.extracted_entities);
      
    } catch (error) {
      console.error('Error:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="entity-chat">
      <h2>Custom Entity Extraction</h2>
      
      {/* BC3 Fields Selection */}
      <div className="selection-section">
        <h3>Select BC3 Fields</h3>
        {/* Add your BC3 field selection UI here */}
      </div>
      
      {/* Asset Columns Selection */}
      <div className="selection-section">
        <h3>Select Asset Columns</h3>
        {/* Add your asset column selection UI here */}
      </div>
      
      {/* Chat Form */}
      <form onSubmit={handleSubmit}>
        <textarea
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          placeholder="Ask the agent to extract entities..."
          rows={4}
        />
        <button type="submit" disabled={loading}>
          {loading ? 'Processing...' : 'Extract Entities'}
        </button>
      </form>
      
      {/* Results */}
      {entities.length > 0 && (
        <div className="results">
          <h3>Extracted Entities ({entities.length})</h3>
          {entities.map((entity, index) => (
            <div key={index} className="entity-card">
              <h4>{entity.entity_name}</h4>
              <p><strong>Type:</strong> {entity.entity_type}</p>
              <p><strong>Value:</strong> {entity.entity_value}</p>
              <p><strong>Confidence:</strong> {entity.confidence}</p>
              <p><strong>Description:</strong> {entity.description}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default EntityChat;
```

#### 4. **Add to Your App**
```jsx
// App.js
import EntityChat from './components/EntityChat';

function App() {
  return (
    <div className="App">
      <header className="App-header">
        <h1>Custom Entity Extraction Agent</h1>
      </header>
      <main>
        <EntityChat />
      </main>
    </div>
  );
}
```

### **Vue.js Example**

#### 1. **Install Dependencies**
```bash
npm install axios
```

#### 2. **Create API Service**
```javascript
// services/entityAgent.js
import axios from 'axios';

const API_BASE_URL = 'http://localhost:8001';

export const entityAgentAPI = {
  checkHealth: () => axios.get(`${API_BASE_URL}/health`),
  chat: (payload) => axios.post(`${API_BASE_URL}/chat`, payload),
  getEntities: (sessionId) => axios.get(`${API_BASE_URL}/entities/${sessionId}`),
  getContextProviders: () => axios.get(`${API_BASE_URL}/context-providers`)
};
```

#### 3. **Create Chat Component**
```vue
<!-- components/EntityChat.vue -->
<template>
  <div class="entity-chat">
    <h2>Custom Entity Extraction</h2>
    
    <!-- BC3 Fields Selection -->
    <div class="selection-section">
      <h3>Select BC3 Fields</h3>
      <!-- Add your BC3 field selection UI here -->
    </div>
    
    <!-- Asset Columns Selection -->
    <div class="selection-section">
      <h3>Select Asset Columns</h3>
      <!-- Add your asset column selection UI here -->
    </div>
    
    <!-- Chat Form -->
    <form @submit.prevent="handleSubmit">
      <textarea
        v-model="message"
        placeholder="Ask the agent to extract entities..."
        rows="4"
      />
      <button type="submit" :disabled="loading">
        {{ loading ? 'Processing...' : 'Extract Entities' }}
      </button>
    </form>
    
    <!-- Results -->
    <div v-if="entities.length > 0" class="results">
      <h3>Extracted Entities ({{ entities.length }})</h3>
      <div
        v-for="(entity, index) in entities"
        :key="index"
        class="entity-card"
      >
        <h4>{{ entity.entity_name }}</h4>
        <p><strong>Type:</strong> {{ entity.entity_type }}</p>
        <p><strong>Value:</strong> {{ entity.entity_value }}</p>
        <p><strong>Confidence:</strong> {{ entity.confidence }}</p>
        <p><strong>Description:</strong> {{ entity.description }}</p>
      </div>
    </div>
  </div>
</template>

<script>
import { entityAgentAPI } from '../services/entityAgent';

export default {
  name: 'EntityChat',
  data() {
    return {
      message: '',
      selectedBC3Fields: [],
      selectedAssetColumns: [],
      entities: [],
      loading: false
    };
  },
  methods: {
    async handleSubmit() {
      this.loading = true;
      
      try {
        const payload = {
          message: this.message,
          session_id: `session_${Date.now()}`,
          selected_bc3_fields: this.selectedBC3Fields,
          selected_asset_columns: this.selectedAssetColumns
        };
        
        const response = await entityAgentAPI.chat(payload);
        this.entities = response.data.extracted_entities;
        
      } catch (error) {
        console.error('Error:', error);
      } finally {
        this.loading = false;
      }
    }
  }
};
</script>
```

## 🔧 Configuration

### **Environment Variables**
```bash
# Google Cloud
GOOGLE_CLOUD_PROJECT=your-project-id
GOOGLE_CLOUD_LOCATION=us-central1

# LLM Settings
LLM_MODEL_NAME=gemini-2.5-flash-lite
LLM_TEMPERATURE=0.1
LLM_MAX_OUTPUT_TOKENS=2048

# Session Management
SESSION_MANAGER_TYPE=memory  # Options: memory, firestore, redis, mongodb
```

### **Session Manager Types**
- **memory**: Fast, in-memory storage (default, good for development)
- **firestore**: Google Cloud Firestore (good for production)

## 🎯 Use Cases

### **1. Credit Risk Assessment**
- **Input**: Credit scores, debt levels, account balances
- **Output**: Risk scores, utilization ratios, alert thresholds

### **2. Customer Segmentation**
- **Input**: Purchase history, demographics, behavior data
- **Output**: Customer tiers, loyalty scores, churn risk

### **3. Fraud Detection**
- **Input**: Transaction patterns, account behavior, location data
- **Output**: Risk indicators, anomaly scores, alert rules

### **4. Business Intelligence**
- **Input**: Sales data, customer data, operational metrics
- **Output**: Performance indicators, trend analysis, predictive insights

## 🚀 Deployment

### **Local Development**
```bash
python main.py --port 8001
```

### **Production Deployment**
```bash
# Using Gunicorn
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8001

# Using Docker
docker build -t entity-agent .
docker run -p 8001:8001 entity-agent
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

- **Documentation**: Check this README
- **Issues**: Create a GitHub issue
- **Questions**: Check the examples above

---

**Happy Entity Extraction! 🎉**
