# 🚀 AEGIS Docker Quick Reference

## ⚡ Quick Start
```bash
make init          # First-time setup
make up            # Start services
make logs          # View logs
make down          # Stop services
```

## 🎯 Essential Commands

### Start/Stop
```bash
make up            # Start all services
make dev-up        # Start with dev tools
make down          # Stop services
make restart       # Restart all
```

### Monitoring
```bash
make logs          # All logs (follow)
make ps            # Service status
make stats         # Resource usage
make health        # Health checks
```

### Database
```bash
make db-shell      # PostgreSQL CLI
make db-backup     # Backup database
make redis-cli     # Redis CLI
make redis-keys    # Show all keys
```

### Development
```bash
make rebuild       # Rebuild images
make shell-orchestrator    # Container shell
make test-all      # Test connectivity
```

### Maintenance
```bash
make clean         # Remove volumes (⚠️ deletes data)
make prune         # Clean Docker resources
make db-backup     # Backup before clean!
```

## 🌐 Access URLs

| Service | URL | Credentials |
|---------|-----|-------------|
| **Orchestrator** | http://localhost:8000 | - |
| **Dashboard** | http://localhost:3000 | - |
| **API Docs** | http://localhost:8000/docs | - |
| **Redis UI** | http://localhost:8081 | admin/aegis2026 |
| **PgAdmin** | http://localhost:5050 | admin@aegis.local/aegis2026 |

## 📊 Useful Queries

### PostgreSQL
```bash
# Latest telemetry
make db-query SQL="SELECT * FROM latest_telemetry"

# Active alerts
make db-query SQL="SELECT * FROM active_alerts"

# Fleet health
make db-query SQL="SELECT * FROM fleet_health"
```

### Redis
```bash
# Vehicle telemetry keys
docker exec aegis-redis redis-cli KEYS "vehicle:*:telemetry"

# Check message queue
docker exec aegis-redis redis-cli LLEN alerts_queue
```

## 🔧 Troubleshooting

### Services won't start
```bash
make down
docker system prune -f
make build
make up
```

### View specific service logs
```bash
make logs-orchestrator
make logs-vehicles
make logs-redis
make logs-postgres
```

### Check connectivity
```bash
make test-all
```

### Reset everything (⚠️ DELETES DATA)
```bash
make clean
make init
```

## 📝 Notes

- Use `make dev-up` for development (includes Redis Commander & PgAdmin)
- Always run `make db-backup` before `make clean`
- Check `.env` file for configuration
- Services auto-restart unless stopped

## 🆘 Help

```bash
make help          # Show all available commands
```

---
**Project AEGIS** | Digital Twin Emergency Vehicle System
