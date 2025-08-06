# Voice Service Guide - Vocelio AI Call Center

## 🎤 Overview

The Voice Service is the core component responsible for text-to-speech generation, voice cloning, voice recognition, and voice marketplace functionality. It integrates with multiple TTS providers to deliver high-quality, natural-sounding voices for your AI call center.

## 🏗️ Architecture

```
Voice Service Architecture
├── 🎯 Voice Controller (API endpoints)
├── 🔄 Provider Manager (Multi-provider support)
├── 🧪 Voice Lab (Voice cloning & training)
├── 🏪 Voice Marketplace (Voice library)
├── 🎚️ Audio Processing (Quality optimization)
└── 💾 Voice Storage (Voice files & metadata)
```

## ⚙️ Configuration

### Environment Variables

```env
# Voice Service Configuration
VOICE_SERVICE_PORT=3001
VOICE_SERVICE_HOST=0.0.0.0

# ElevenLabs Configuration
ELEVENLABS_API_KEY=your_elevenlabs_api_key
ELEVENLABS_DEFAULT_VOICE=21m00Tcm4TlvDq8ikWAM
ELEVENLABS_MODEL=eleven_monolingual_v1

# Azure Speech Configuration
AZURE_SPEECH_KEY=your_azure_speech_key
AZURE_SPEECH_REGION=eastus
AZURE_SPEECH_ENDPOINT=https://eastus.api.cognitive.microsoft.com/

# Google Cloud TTS Configuration
GOOGLE_CLOUD_PROJECT_ID=your_project_id
GOOGLE_CLOUD_KEY_FILE=path/to/service-account.json

# Amazon Polly Configuration
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
AWS_REGION=us-east-1

# Voice Lab Configuration
VOICE_CLONING_ENABLED=true
MIN_AUDIO_DURATION=30
MAX_AUDIO_DURATION=600
SUPPORTED_AUDIO_FORMATS=wav,mp3,m4a

# Storage Configuration
VOICE_STORAGE_PATH=./storage/voices
TEMP_AUDIO_PATH=./storage/temp
MAX_FILE_SIZE=50MB

# Quality Settings
AUDIO_SAMPLE_RATE=22050
AUDIO_BIT_DEPTH=16
AUDIO_CHANNELS=1
AUDIO_FORMAT=wav

# Cache Configuration
VOICE_CACHE_TTL=3600
AUDIO_CACHE_SIZE=1GB
```

### Provider Configuration

```javascript
// config/providers.js
module.exports = {
  elevenlabs: {
    enabled: true,
    priority: 1,
    features: ['tts', 'voice_cloning', 'voice_design'],
    limits: {
      charactersPerMonth: 10000,
      voicesPerUser: 3,
      cloningMinutes: 30
    },
    settings: {
      stability: 0.5,
      similarityBoost: 0.75,
      style: 0.0,
      speakerBoost: true
    }
  },
  azure: {
    enabled: true,
    priority: 2,
    features: ['tts', 'ssml'],
    limits: {
      charactersPerMonth: 500000,
      requestsPerMinute: 200
    },
    settings: {
      voice: 'en-US-JennyNeural',
      style: 'professional',
      rate: '0%',
      pitch: '0%'
    }
  },
  google: {
    enabled: true,
    priority: 3,
    features: ['tts', 'ssml', 'custom_voices'],
    limits: {
      charactersPerMonth: 1000000,
      requestsPerMinute: 1000
    },
    settings: {
      voice: 'en-US-Wavenet-D',
      speakingRate: 1.0,
      pitch: 0.0,
      volumeGainDb: 0.0
    }
  },
  aws: {
    enabled: true,
    priority: 4,
    features: ['tts', 'ssml', 'neural_voices'],
    limits: {
      charactersPerMonth: 5000000,
      requestsPerMinute: 100
    },
    settings: {
      voice: 'Joanna',
      engine: 'neural',
      textType: 'text'
    }
  }
};
```

## 🚀 API Endpoints

### Voice Management

#### List Available Voices
```http
GET /api/voice/voices
Authorization: Bearer {jwt_token}
```

**Query Parameters:**
- `provider` (optional) - Filter by provider (elevenlabs, azure, google, aws)
- `category` (optional) - Filter by category (professional, conversational, narrative)
- `language` (optional) - Filter by language (en, es, fr, de, etc.)
- `gender` (optional) - Filter by gender (male, female, neutral)

**Response:**
```json
{
  "success": true,
  "data": {
    "voices": [
      {
        "id": "21m00Tcm4TlvDq8ikWAM",
        "name": "Rachel",
        "provider": "elevenlabs",
        "category": "professional",
        "language": "en",
        "gender": "female",
        "description": "Calm and professional voice",
        "sample_url": "https://...",
        "settings": {
          "stability": 0.5,
          "similarity_boost": 0.75
        }
      }
    ],
    "total": 150,
    "pagination": {
      "page": 1,
      "limit": 20,
      "has_more": true
    }
  }
}
```

#### Generate Speech
```http
POST /api/voice/generate
Authorization: Bearer {jwt_token}
Content-Type: application/json
```

**Request Body:**
```json
{
  "text": "Hello, this is a test message for voice generation.",
  "voice_id": "21m00Tcm4TlvDq8ikWAM",
  "provider": "elevenlabs",
  "settings": {
    "stability": 0.6,
    "similarity_boost": 0.8,
    "style": 0.2,
    "use_speaker_boost": true
  },
  "output_format": "mp3",
  "sample_rate": 44100
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "audio_url": "https://storage.../audio/generated_12345.mp3",
    "duration": 3.2,
    "characters_used": 52,
    "cost": 0.0012,
    "provider": "elevenlabs",
    "voice_id": "21m00Tcm4TlvDq8ikWAM",
    "generation_id": "gen_12345",
    "metadata": {
      "sample_rate": 44100,
      "bit_depth": 16,
      "file_size": 51200
    }
  }
}
```

### Voice Cloning

#### Clone Voice from Audio
```http
POST /api/voice/clone
Authorization: Bearer {jwt_token}
Content-Type: multipart/form-data
```

**Form Data:**
- `audio_file` - Audio file (WAV/MP3, 30s-10min)
- `voice_name` - Name for the cloned voice
- `description` - Description of the voice
- `labels` - Comma-separated labels (professional, young, energetic)

**Response:**
```json
{
  "success": true,
  "data": {
    "voice_id": "cloned_voice_12345",
    "name": "Custom Voice 1",
    "status": "training",
    "progress": 0,
    "estimated_completion": "2024-01-15T10:30:00Z",
    "preview_url": null,
    "settings": {
      "stability": 0.5,
      "similarity_boost": 0.75
    }
  }
}
```

#### Get Voice Clone Status
```http
GET /api/voice/clone/{voice_id}/status
Authorization: Bearer {jwt_token}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "voice_id": "cloned_voice_12345",
    "status": "completed",
    "progress": 100,
    "preview_url": "https://storage.../preview_12345.mp3",
    "ready_for_use": true,
    "training_log": [
      {
        "timestamp": "2024-01-15T10:00:00Z",
        "status": "started",
        "message": "Voice training initiated"
      },
      {
        "timestamp": "2024-01-15T10:30:00Z",
        "status": "completed",
        "message": "Voice training completed successfully"
      }
    ]
  }
}
```

### Voice Marketplace

#### Browse Voice Marketplace
```http
GET /api/voice/marketplace
Authorization: Bearer {jwt_token}
```

**Query Parameters:**
- `category` - Filter by category
- `price_range` - Filter by price (free, premium)
- `sort` - Sort by (popular, newest, rating)
- `search` - Search by name or description

**Response:**
```json
{
  "success": true,
  "data": {
    "voices": [
      {
        "id": "marketplace_voice_123",
        "name": "Professional Sarah",
        "creator": "Vocelio Labs",
        "category": "business",
        "rating": 4.8,
        "downloads": 1250,
        "price": 9.99,
        "currency": "USD",
        "preview_url": "https://storage.../preview_123.mp3",
        "description": "Professional female voice perfect for business presentations",
        "tags": ["professional", "clear", "articulate"],
        "duration_sample": 30
      }
    ],
    "categories": [
      "business",
      "conversational", 
      "narrative",
      "character",
      "multilingual"
    ],
    "total": 500
  }
}
```

#### Purchase Voice
```http
POST /api/voice/marketplace/{voice_id}/purchase
Authorization: Bearer {jwt_token}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "transaction_id": "txn_12345",
    "voice_id": "marketplace_voice_123",
    "amount": 9.99,
    "currency": "USD",
    "status": "completed",
    "purchased_at": "2024-01-15T10:00:00Z",
    "download_url": "https://storage.../download_123.zip",
    "license": "standard_commercial"
  }
}
```

## 🧪 Voice Lab Features

### Voice Training

The Voice Lab allows users to train custom voices:

```javascript
// Voice training process
const trainingProcess = {
  1: "Audio Upload & Validation",
  2: "Audio Preprocessing", 
  3: "Feature Extraction",
  4: "Model Training",
  5: "Quality Assessment",
  6: "Voice Generation Testing",
  7: "Deployment"
};
```

### Voice Quality Assessment

```javascript
// Quality metrics
const qualityMetrics = {
  clarity: "Speech clarity and articulation",
  naturalness: "How natural the voice sounds",
  similarity: "Similarity to original voice",
  consistency: "Consistency across different texts",
  emotion: "Ability to convey emotions",
  pronunciation: "Correct pronunciation of words"
};
```

## 🎚️ Audio Processing

### Audio Optimization

```javascript
// Audio processing pipeline
const audioProcessing = {
  normalization: "Volume normalization",
  noiseReduction: "Background noise removal",
  enhancement: "Audio quality enhancement",
  compression: "Dynamic range compression",
  equalization: "Frequency response optimization",
  formatting: "Output format conversion"
};
```

### Supported Formats

**Input Formats:**
- WAV (preferred)
- MP3
- M4A
- FLAC
- OGG

**Output Formats:**
- WAV (highest quality)
- MP3 (compressed)
- OGG (web optimized)
- FLAC (lossless)

## 📊 Usage Analytics

### Voice Usage Tracking

```http
GET /api/voice/analytics/usage
Authorization: Bearer {jwt_token}
```

**Query Parameters:**
- `start_date` - Start date (YYYY-MM-DD)
- `end_date` - End date (YYYY-MM-DD)
- `voice_id` - Specific voice ID
- `provider` - Provider filter

**Response:**
```json
{
  "success": true,
  "data": {
    "summary": {
      "total_generations": 1250,
      "total_characters": 125000,
      "total_duration": 3600,
      "total_cost": 15.50,
      "average_quality": 4.7
    },
    "by_voice": [
      {
        "voice_id": "21m00Tcm4TlvDq8ikWAM",
        "voice_name": "Rachel",
        "generations": 300,
        "characters": 30000,
        "duration": 900,
        "cost": 4.50
      }
    ],
    "by_provider": [
      {
        "provider": "elevenlabs",
        "generations": 800,
        "cost": 12.00,
        "average_quality": 4.9
      }
    ]
  }
}
```

## 🔧 Advanced Configuration

### Custom Voice Models

```javascript
// Custom model configuration
const customModel = {
  name: "custom_model_v1",
  architecture: "transformer",
  parameters: {
    layers: 12,
    attention_heads: 8,
    hidden_size: 512,
    vocabulary_size: 50000
  },
  training: {
    batch_size: 32,
    learning_rate: 0.0001,
    epochs: 100,
    validation_split: 0.2
  },
  optimization: {
    gradient_clipping: 1.0,
    weight_decay: 0.01,
    scheduler: "cosine_annealing"
  }
};
```

### SSML Support

```xml
<!-- Example SSML for advanced speech control -->
<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="en-US">
  <voice name="Rachel">
    <prosody rate="medium" pitch="medium" volume="medium">
      Hello! I'm calling from <emphasis level="strong">Vocelio AI</emphasis>.
      <break time="500ms"/>
      How are you doing today?
      <prosody rate="slow">
        I'd like to tell you about our amazing new product.
      </prosody>
    </prosody>
  </voice>
</speak>
```

### Voice Emotions

```javascript
// Emotional voice settings
const emotionalVoices = {
  happy: {
    stability: 0.6,
    similarity_boost: 0.8,
    style: 0.3,
    pitch_adjustment: +2
  },
  sad: {
    stability: 0.4,
    similarity_boost: 0.7,
    style: 0.6,
    pitch_adjustment: -3
  },
  excited: {
    stability: 0.7,
    similarity_boost: 0.9,
    style: 0.4,
    rate_adjustment: +10
  },
  calm: {
    stability: 0.3,
    similarity_boost: 0.6,
    style: 0.1,
    rate_adjustment: -5
  }
};
```

## 🔒 Security & Privacy

### Data Protection

- **Audio Encryption**: All audio files encrypted at rest
- **Secure Transmission**: HTTPS/TLS for all API calls
- **Access Control**: Role-based access to voice libraries
- **Audit Logging**: Complete audit trail of voice usage

### Privacy Compliance

- **GDPR Compliance**: Right to erasure for voice data
- **Data Retention**: Configurable retention policies
- **Consent Management**: Voice consent tracking
- **Anonymization**: Option to anonymize voice data

## 🚨 Error Handling

### Common Error Codes

| Code | Description | Solution |
|------|-------------|----------|
| VOICE_001 | Invalid voice ID | Check voice ID exists |
| VOICE_002 | Provider API error | Check provider credentials |
| VOICE_003 | Audio file too large | Reduce file size |
| VOICE_004 | Unsupported format | Use supported audio format |
| VOICE_005 | Insufficient credits | Top up account credits |
| VOICE_006 | Rate limit exceeded | Wait before retrying |

### Error Response Format

```json
{
  "success": false,
  "error": {
    "code": "VOICE_002",
    "message": "ElevenLabs API authentication failed",
    "details": {
      "provider": "elevenlabs",
      "endpoint": "/v1/text-to-speech",
      "status_code": 401
    },
    "suggestion": "Check your ElevenLabs API key configuration"
  }
}
```

## 📈 Performance Optimization

### Caching Strategy

```javascript
// Voice caching configuration
const cacheConfig = {
  levels: {
    memory: {
      size: "100MB",
      ttl: 300 // 5 minutes
    },
    redis: {
      size: "1GB", 
      ttl: 3600 // 1 hour
    },
    disk: {
      size: "10GB",
      ttl: 86400 // 24 hours
    }
  },
  strategies: {
    generation: "lru", // Least Recently Used
    voices: "lfu", // Least Frequently Used
    samples: "ttl" // Time To Live
  }
};
```

### Load Balancing

```javascript
// Provider load balancing
const loadBalancing = {
  strategy: "weighted_round_robin",
  weights: {
    elevenlabs: 0.4,
    azure: 0.3,
    google: 0.2,
    aws: 0.1
  },
  failover: {
    enabled: true,
    timeout: 5000,
    retries: 3
  }
};
```

## 🧪 Testing

### Unit Tests

```bash
# Run voice service tests
npm run test:voice

# Test specific functionality
npm run test:voice:generation
npm run test:voice:cloning
npm run test:voice:marketplace
```

### Integration Tests

```bash
# Test provider integrations
npm run test:providers

# Test end-to-end workflows
npm run test:e2e:voice
```

### Load Testing

```javascript
// k6 load test script
import http from 'k6/http';
import { check } from 'k6';

export let options = {
  stages: [
    { duration: '2m', target: 10 },
    { duration: '5m', target: 50 },
    { duration: '2m', target: 0 }
  ]
};

export default function() {
  let response = http.post('http://localhost:3001/api/voice/generate', {
    text: 'Hello world test message',
    voice_id: '21m00Tcm4TlvDq8ikWAM'
  }, {
    headers: {
      'Authorization': 'Bearer ' + __ENV.JWT_TOKEN,
      'Content-Type': 'application/json'
    }
  });

  check(response, {
    'status is 200': (r) => r.status === 200,
    'response time < 5s': (r) => r.timings.duration < 5000
  });
}
```

## 📚 Best Practices

### Voice Selection

1. **Match Voice to Audience**: Choose appropriate voice demographics
2. **Consider Context**: Professional vs conversational settings
3. **Test Different Voices**: A/B test voice performance
4. **Monitor Quality**: Track customer satisfaction scores

### Audio Quality

1. **Use High-Quality Sources**: Clean, noise-free audio for cloning
2. **Optimize Settings**: Tune stability and similarity parameters
3. **Test Thoroughly**: Validate generated audio before use
4. **Monitor Performance**: Track generation quality metrics

### Cost Optimization

1. **Cache Frequently Used Audio**: Reduce regeneration costs
2. **Choose Appropriate Providers**: Balance cost vs quality
3. **Monitor Usage**: Track character usage and costs
4. **Implement Quotas**: Prevent unexpected overages

---

**🎤 Your Voice Service is ready to deliver high-quality, natural-sounding voices for your AI call center!**
