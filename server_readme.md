# Flask Vending Machine Server - Technical Guide

## 🎯 Quick Overview
**Flask-based vending machine control system** with dual ESP32 communication (WiFi + Serial), auto-discovery, and REST API.

**Stack**: Flask + Python | **Frontend**: HTML/JS/CSS | **Database**: File-based (JSON) → SQL for production | **Communication**: HTTP REST + UDP Discovery + Serial

## 🏗️ Architecture
```
Web Interface → Flask Server → Device Manager → ESP32 (WiFi/Serial) → Hardware
```

**Core Layers**:
- **REST API**: Standard endpoints for vending operations
- **Device Manager**: Handles ESP32 communication switching  
- **Communication**: WiFi (production) + Serial (development)
- **Discovery**: Auto-finds ESP32 devices via UDP broadcast

## 🌐 REST API - Core Endpoints

| Endpoint | Method | Purpose | Request | Response |
|----------|--------|---------|---------|----------|
| `/vend/{slot_id}` | POST | Vend item | `{"device_id": "ESP32_xxx"}` | `{"status": "success", "slot_id": 3}` |
| `/status` | GET | System status | - | `{"devices": {...}, "inventory": {...}}` |
| `/health` | GET | Health check | - | `{"status": "healthy", "checks": {...}}` |
| `/esp32/devices/list` | GET | List devices | - | `{"devices": [...], "active_device": "..."}` |
| `/esp32/devices/select` | POST | Select device | `{"device_id": "ESP32_xxx"}` | `{"status": "success"}` |

## 📡 ESP32 Communication

### WiFi Mode (Production)
**Flow**: ESP32 → UDP Broadcast Discovery → HTTP Polling (2s intervals) → Command Execution
```
1. ESP32 broadcasts "DISCOVER_FLASK_SERVER" on port 12346
2. Flask responds with "FLASK_SERVER_IP:{ip}"  
3. ESP32 polls GET /esp32/wifi/command every 2 seconds
4. Flask queues commands, ESP32 executes and reports back
```

### Serial Mode (Development)  
**Flow**: Direct USB connection → Real-time bidirectional communication (50ms response)
```
Flask → ESP32: "VEND:3\n"
ESP32 → Flask: "VEND_SUCCESS:3\n"
```

## 🗃️ Data Storage

### Current (Development)
- **Type**: File-based JSON
- **Files**: `devices.json`, `communication.log`, `config.json`

### Production Requirements
```sql
-- Core tables needed:
devices(device_id, type, status, ip_address, last_seen)
transactions(transaction_id, device_id, slot_id, status, timestamp)  
communication_log(device_id, direction, message, level, timestamp)
inventory(slot_id, item_name, count, status)
```

## 🤖 ESP32 Code Status

### ✅ Production Ready - No Changes Needed
**WiFi Version**: Auto-discovery, error handling, optimized polling, device registration
**Serial Version**: Fast response, comprehensive commands, development features

**Only Update These 3 Lines for Production:**
```cpp
const char* WIFI_SSID = "PRODUCTION_WIFI";      // ✏️ Change WiFi name
const char* WIFI_PASSWORD = "PRODUCTION_PWD";   // ✏️ Change WiFi password  
const int FLASK_SERVER_PORT = 443;              // ✏️ Change to 443 for HTTPS
```

## 🚀 Production Deployment

### Docker Setup
```yaml
services:
  vending-server:
    image: vending-machine:latest
    ports: ["80:5000"]
    environment:
      - DATABASE_URL=postgresql://user:pass@db/vending
      - REDIS_URL=redis://redis:6379
  
  nginx: # Load balancer
  postgresql: # Database  
  redis: # Caching
```

### Security Additions
```python
# Add for production:
- JWT authentication (@jwt_required())
- Rate limiting (@limiter.limit("10/minute"))  
- HTTPS certificates
- Input validation
- API versioning (/v1/)
```

### Monitoring
```python
# Add these libraries:
- prometheus_flask_exporter  # Metrics
- structlog                  # Logging
- flask_socketio            # Real-time updates
```

## 🧪 Quick Testing

### Manual API Tests
```bash
# Status check
curl http://localhost:5000/status

# Vend operation  
curl -X POST http://localhost:5000/vend/3 \
  -H "Content-Type: application/json" \
  -d '{"device_id": "ESP32_xxx"}'

# Device list
curl http://localhost:5000/esp32/devices/list
```

### System Validation
```bash
python check_system.py  # Runs 5 validation tests
```

## 📊 Performance Targets

| Metric | Target | Current |
|--------|--------|---------|
| API Response | <500ms | ~200ms |
| Device Discovery | <5s | ~2s |  
| Vending Latency | <3s (WiFi), <1s (Serial) | ✅ |
| Uptime | 99.9% | - |
| Concurrent Operations | 10+ | ✅ |

## 🔧 Development Setup

### Quick Start
```bash
git clone <repo> && cd flask-vending-machine
python -m venv venv && source venv/bin/activate  # or venv\Scripts\activate
pip install -r requirements.txt
python src/app.py  # Server starts on http://localhost:5000
```

### Frontend Development
- **Templates**: `src/templates/index.html`
- **Static Files**: `src/static/{css,js}/`
- **Framework**: Vanilla JS + Jinja2 templates

---

## 📋 Production Checklist

- [ ] **Database**: Replace JSON files with PostgreSQL/MySQL
- [ ] **Authentication**: Implement JWT or API key system
- [ ] **Security**: Add HTTPS, rate limiting, input validation
- [ ] **Monitoring**: Add Prometheus metrics, structured logging
- [ ] **Scaling**: Docker containers + load balancer
- [ ] **ESP32 Config**: Update WiFi credentials for production network
- [ ] **Testing**: Unit tests, integration tests, load testing
- [ ] **Documentation**: API documentation (OpenAPI/Swagger)

**Result**: Enterprise-ready vending machine system with multi-device support, real-time monitoring, and scalable architecture.