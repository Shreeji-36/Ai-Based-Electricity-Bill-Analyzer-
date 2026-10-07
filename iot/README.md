# IoT Integration (planned)

Planned flow: ESP32 + current sensor -> MQTT broker -> bridge service -> POST /api/iot/readings.

Topic format: `factory/<industry>/<machine_code>/power` with payload `{"kw": 41.2, "ts": 1760000000}`.

Status: design only. Implement after real hardware and a meter protocol are confirmed with the client.