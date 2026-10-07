# AI Industrial Energy Intelligence

AI-powered platform that reads industrial electricity bills, estimates machine-wise
consumption, forecasts future bills, flags abnormal usage and recommends savings.
Supports Pharmacy, Dairy, Steel and Cold Storage industries.

## Features
- Bill upload with OCR (JPG, PNG, PDF)
- Machine-wise units, cost and share, with an automatic "Others" category
- 3-month forecast, bill and machine anomaly detection
- Savings recommendations with estimated cost impact
- PDF, Excel and CSV reports
- JWT authentication with role-based access (admin, analyst, viewer)

## Repository layout
| Folder | Purpose |
|---|---|
| frontend | Next.js + TypeScript + Tailwind + Recharts dashboard |
| backend | FastAPI REST API |
| ai-engine | Forecasting, anomaly detection, recommendations |
| ocr | Tesseract/OpenCV bill reader service |
| database | PostgreSQL schema and seed data |
| iot | Planned smart meter and ESP32 integration |
| docs | Architecture, API, setup, user manual |
| docker | Dockerfiles and nginx config |
| tests | pytest suite |

## Quick start
    cp .env.example .env
    docker compose up --build

See docs/setup.md for local development and free hosting on Vercel + Render.

## Roadmap
IoT smart meters, live monitoring, carbon footprint, multi-factory support,
WhatsApp/email alerts, predictive maintenance, ERP integration, mobile app.

## License
MIT