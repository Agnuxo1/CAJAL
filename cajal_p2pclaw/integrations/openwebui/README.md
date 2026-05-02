# Open WebUI Integration
# Add this to your Open WebUI connections:

Name: CAJAL-4B
Base URL: http://localhost:11434
Model: cajal

# Or via API:
curl -X POST http://localhost:3000/api/v1/models \
  -H "Content-Type: application/json" \
  -d '{"id": "cajal", "name": "CAJAL-4B-P2PCLAW"}'
