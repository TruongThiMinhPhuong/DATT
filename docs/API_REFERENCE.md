# 🔌 API Reference

Backend API documentation.

---

## Base URL

```
http://localhost:8000
```

---

## Authentication

Admin endpoints require authentication header:
```
Authorization: Bearer <firebase_token>
```

---

## Statistics

### GET /api/stats

Get classification statistics.

**Response:**
```json
{
  "total": 150,
  "category_counts": {
    "fresh_fruit": 80,
    "spoiled_fruit": 50,
    "other": 20
  },
  "avg_confidence": 0.92,
  "avg_processing_time": 0.45
}
```

---

## History

### GET /api/history?limit=100

Get classification history.

**Parameters:**
- `limit` (optional): Max results (default: 100)

**Response:**
```json
{
  "history": [
    {
      "id": 1,
      "timestamp": 1702345678.5,
      "classification": "fresh_fruit",
      "confidence": 0.95,
      "device_id": "rpi_01",
      "image_url": "https://...",
      "processing_time": 0.42
    }
  ]
}
```

---

## Hardware Control (Admin Only)

### POST /api/hardware/conveyor/start

Start conveyor belt.

**Response:**
```json
{"status": "success"}
```

---

### POST /api/hardware/conveyor/stop

Stop conveyor belt.

---

### POST /api/hardware/conveyor/speed

Set conveyor speed.

**Request:**
```json
{"speed": 75}
```

**Response:**
```json
{"status": "success", "speed": 75}
```

---

### POST /api/hardware/servo/move

Move servo.

**Request:**
```json
{"position": "left"}
```

Positions: `left`, `center`, `right`

---

### POST /api/hardware/camera/capture

Manual image capture.

---

### POST /api/hardware/emergency-stop

Emergency stop all systems.

---

### GET /api/hardware/status

Get hardware status.

**Response:**
```json
{
  "status": "online",
  "conveyor_speed": 75,
  "servo_position": "center",
  "trigger_mode": "ir_sensor"
}
```

---

## WebSocket

### WS /ws

Real-time updates.

**Connect:**
```javascript
const ws = new WebSocket('ws://localhost:8000/ws');

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log(data);
};
```

**Messages:**
```json
{
  "type": "classification",
  "data": {
    "classification": "fresh_fruit",
    "confidence": 0.95,
    "timestamp": 1702345678.5
  }
}
```

---

## Error Codes

| Code | Description |
|------|-------------|
| 200 | Success |
| 401 | Unauthorized |
| 403 | Forbidden (not admin) |
| 404 | Not found |
| 500 | Server error |
| 503 | Service unavailable |

---

## Rate Limiting

- Statistics: 60 req/min
- History: 30 req/min
- Hardware control: 10 req/min

---

**For full examples, see: `docs/API_EXAMPLES.md`**
