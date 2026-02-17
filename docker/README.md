# 🐳 Docker Deployment Guide - Project AEGIS

Complete Docker setup for the AEGIS Emergency Vehicle Digital Twin System.

---

## 📋 Table of Contents

1. [Quick Start](#quick-start)
2. [Architecture Overview](#architecture-overview)
3. [Service Details](#service-details)
4. [Configuration](#configuration)
5. [Common Operations](#common-operations)
6. [Monitoring & Debugging](#monitoring--debugging)
7. [Production Deployment](#production-deployment)
8. [Troubleshooting](#troubleshooting)

---

## 🚀 Quick Start

### Prerequisites

- Docker Engine 24.0+ ([Install](https://docs.docker.com/engine/install/))
- Docker Compose 2.20+ (included with Docker Desktop)
- 4GB RAM minimum, 8GB recommended
- 10GB free disk space

### Initial Setup

```bash
# 1. Clone and navigate to project
cd /path/to/hpe-tech-challenge-25

# 2. Create environment file
cp .env.example .env

# 3. Build and start all services
docker-compose -f docker/docker-compose.yml up -d

# 4. Verify services are running
docker-compose -f docker/docker-compose.yml ps

# 5. View logs
docker-compose -f docker/docker-compose.yml logs -f
```

### Access Points

Once running, access the system at:

| Service | URL | Purpose |
|---------|-----|---------|
| **Orchestrator API** | http://localhost:8000 | REST & WebSocket API |
| **Dashboard** | http://localhost:3000 | Real-time visualization |
| **Redis Commander** | http://localhost:8081 | Redis web UI (dev mode) |
| **PgAdmin** | http://localhost:5050 | PostgreSQL UI (dev mode) |

---

## 🏗️ Architecture Overview

```
┌─────────────────┐     ┌─────────────────┐
│   Dashboard     │────▶│  Orchestrator   │
│   (Port 3000)   │     │   (Port 8000)   │
└─────────────────┘     └────────┬────────┘
                                 │
                    ┌────────────┼────────────┐
                    ▼            ▼            ▼
              ┌─────────┐  ┌──────────┐  ┌──────────┐
              │  Redis  │  │PostgreSQL│  │Vehicle   │
              │(Port    │  │(Port     │  │Agents    │
              │ 6379)   │  │ 5432)    │  │(x3)      │
              └─────────┘  └──────────┘  └──────────┘
```

### Network Configuration

- **Network Name**: `aegis-network`
- **Subnet**: 172.20.0.0/16
- **IP Allocation**:
  - Redis: 172.20.0.10
  - PostgreSQL: 172.20.0.11
  - Orchestrator: 172.20.0.20
  - Dashboard: 172.20.0.30
  - Vehicles: DHCP

---

## 📦 Service Details

### Core Services

#### 1. Redis (Message Broker)
- **Image**: `redis:7.2-alpine`
- **Purpose**: Real-time telemetry pub/sub
- **Port**: 6379
- **Memory Limit**: 512MB
- **Persistence**: AOF (append-only file)
- **Health Check**: `redis-cli ping`

#### 2. PostgreSQL (Time-series Database)
- **Image**: `postgres:16-alpine`
- **Purpose**: Persistent telemetry and alert storage
- **Port**: 5432
- **Memory Limit**: 1GB
- **Database**: `aegis_db`
- **Credentials**: See `.env` file
- **Init Script**: `docker/init-db.sql`

#### 3. Orchestrator (Central Brain)
- **Build**: Custom (Python 3.13)
- **Purpose**: WebSocket coordinator, fleet management
- **Port**: 8000
- **API Docs**: http://localhost:8000/docs
- **Health Endpoint**: http://localhost:8000/health
- **Command**: `uvicorn src.orchestrator.main:app --host 0.0.0.0 --port 8000`

#### 4. Vehicle Agents (Digital Twins)
- **Build**: Custom (Python 3.13)
- **Purpose**: Simulate vehicle telemetry and behavior
- **Count**: 3 (AMB-001, FIR-001, AMB-002)
- **Memory Limit**: 256MB each
- **Telemetry Interval**: 5 seconds (configurable)

#### 5. Dashboard (Web UI)
- **Build**: Custom (Python 3.13)
- **Purpose**: Real-time visualization interface
- **Port**: 3000
- **WebSocket**: Connects to orchestrator:8000/ws

### Development Tools (Profile: `dev`)

Start with: `docker-compose -f docker/docker-compose.yml --profile dev up -d`

#### Redis Commander
- **Purpose**: Web-based Redis browser
- **Port**: 8081
- **Credentials**: admin / aegis2026 (see `.env`)

#### PgAdmin
- **Purpose**: PostgreSQL web interface
- **Port**: 5050
- **Credentials**: admin@aegis.local / aegis2026 (see `.env`)

---

## ⚙️ Configuration

### Environment Variables

Edit `.env` file to customize:

```bash
# Application
AEGIS_ENV=production        # production | development | test
LOG_LEVEL=INFO             # DEBUG | INFO | WARNING | ERROR

# Database
POSTGRES_PASSWORD=your-secure-password-here

# Redis
REDIS_HOST=redis
REDIS_PORT=6379

# Vehicles
TELEMETRY_INTERVAL=5       # Seconds between updates
```

### Scaling Vehicle Fleet

Add more vehicles by copying a vehicle service block:

```yaml
vehicle-agent-4:
  build:
    context: .
    dockerfile: Dockerfile
    target: runtime
  container_name: aegis-vehicle-pol-001
  command: ["python", "-m", "src.scripts.start_vehicle", "--vehicle-id", "POL-001", "--vehicle-type", "police"]
  environment:
    VEHICLE_ID: POL-001
    VEHICLE_TYPE: police
    REDIS_HOST: redis
    REDIS_PORT: 6379
  depends_on:
    redis:
      condition: service_healthy
  networks:
    - aegis-network
```

---

## 🛠️ Common Operations

### Start/Stop Services

```bash
# Start all services
docker-compose -f docker/docker-compose.yml up -d

# Start specific services
docker-compose -f docker/docker-compose.yml up -d redis postgres

# Stop all services
docker-compose -f docker/docker-compose.yml down

# Stop and remove volumes (CAUTION: deletes data)
docker-compose -f docker/docker-compose.yml down -v
```

### View Logs

```bash
# All services
docker-compose -f docker/docker-compose.yml logs -f

# Specific service
docker-compose -f docker/docker-compose.yml logs -f orchestrator

# Last 100 lines
docker-compose -f docker/docker-compose.yml logs --tail=100

# Filter by time
docker-compose -f docker/docker-compose.yml logs --since 30m
```

### Rebuild After Code Changes

```bash
# Rebuild images
docker-compose -f docker/docker-compose.yml build

# Rebuild and restart
docker-compose -f docker/docker-compose.yml up -d --build

# Force rebuild (no cache)
docker-compose -f docker/docker-compose.yml build --no-cache
```

### Execute Commands Inside Containers

```bash
# Open shell in orchestrator
docker exec -it aegis-orchestrator bash

# Run Python script
docker exec aegis-orchestrator python -m src.utils.diagnostics

# Check Redis keys
docker exec aegis-redis redis-cli KEYS "vehicle:*"

# PostgreSQL query
docker exec aegis-postgres psql -U aegis_user -d aegis_db -c "SELECT COUNT(*) FROM telemetry;"
```

### Backup & Restore

```bash
# Backup PostgreSQL
docker exec aegis-postgres pg_dump -U aegis_user aegis_db > backup_$(date +%Y%m%d).sql

# Restore PostgreSQL
docker exec -i aegis-postgres psql -U aegis_user aegis_db < backup_20260217.sql

# Backup Redis
docker exec aegis-redis redis-cli SAVE
docker cp aegis-redis:/data/dump.rdb ./redis_backup_$(date +%Y%m%d).rdb
```

---

## 📊 Monitoring & Debugging

### Health Checks

```bash
# Check service health
docker-compose -f docker/docker-compose.yml ps

# Inspect specific service
docker inspect aegis-orchestrator

# View resource usage
docker stats
```

### API Testing

```bash
# Test orchestrator health
curl http://localhost:8000/health

# WebSocket connection test
wscat -c ws://localhost:8000/ws

# View API documentation
open http://localhost:8000/docs
```

### Database Queries

```bash
# Latest telemetry
docker exec aegis-postgres psql -U aegis_user -d aegis_db -c \
  "SELECT * FROM latest_telemetry LIMIT 10;"

# Active alerts
docker exec aegis-postgres psql -U aegis_user -d aegis_db -c \
  "SELECT * FROM active_alerts;"

# Fleet health
docker exec aegis-postgres psql -U aegis_user -d aegis_db -c \
  "SELECT * FROM fleet_health;"
```

---

## 🚢 Production Deployment

### Security Checklist

- [ ] Change all default passwords in `.env`
- [ ] Set `AEGIS_ENV=production`
- [ ] Enable HTTPS/TLS for public endpoints
- [ ] Configure firewall rules
- [ ] Set up SSL certificates for PostgreSQL
- [ ] Enable Redis authentication
- [ ] Review and adjust resource limits
- [ ] Set up log aggregation
- [ ] Configure backup automation

### Docker Swarm (Orchestration)

```bash
# Initialize swarm
docker swarm init

# Deploy stack
docker stack deploy -c docker/docker-compose.yml aegis

# Scale services
docker service scale aegis_vehicle-agent-1=5

# View services
docker stack services aegis
```

### Kubernetes Alternative

For Kubernetes deployment, use the provided manifests (if available) or convert:

```bash
# Convert compose to k8s (using kompose)
kompose convert -f docker/docker-compose.yml
```

---

## 🔧 Troubleshooting

### Common Issues

#### Services Won't Start

```bash
# Check logs
docker-compose -f docker/docker-compose.yml logs

# Verify ports aren't in use
netstat -tuln | grep -E ':(6379|5432|8000|3000)'

# Remove conflicting containers
docker container prune
```

#### Connection Issues

```bash
# Test Redis connectivity
docker exec aegis-orchestrator sh -c "python -c 'import redis; r=redis.Redis(host=\"redis\"); print(r.ping())'"

# Test PostgreSQL connectivity
docker exec aegis-orchestrator sh -c "python -c 'import psycopg2; conn=psycopg2.connect(\"host=postgres dbname=aegis_db user=aegis_user\"); print(\"OK\")'"
```

#### Performance Issues

```bash
# Check resource usage
docker stats --no-stream

# Increase memory limits in docker-compose.yml
deploy:
  resources:
    limits:
      memory: 2G  # Increase as needed
```

#### Data Loss

```bash
# Verify volumes exist
docker volume ls | grep aegis

# Inspect volume
docker volume inspect hpe-tech-challenge-25_postgres-data
```

---

## 📚 Additional Resources

- **Project README**: [../README.md](../README.md)
- **Testing Guide**: [../TESTING.md](../TESTING.md)
- **Agent Instructions**: [../AGENTS.md](../AGENTS.md)
- **Docker Docs**: https://docs.docker.com/
- **Compose Reference**: https://docs.docker.com/compose/compose-file/

---

## 📝 Notes

- This setup uses multi-stage Dockerfile for optimized image sizes
- Services use health checks for reliable startup ordering
- Volumes persist data across container restarts
- Dev tools (redis-commander, pgadmin) are optional (use `--profile dev`)
- All services run as non-root user `aegis` for security

---

**Last Updated**: February 2026  
**Maintainer**: Project AEGIS Team
