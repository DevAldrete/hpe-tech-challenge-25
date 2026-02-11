# 🚑 Project AEGIS: Sistema de Gemelos Digitales para Defensa Predictiva
>
> **HPE GreenLake Tech Challenge - Fase II**

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![Docker](https://img.shields.io/badge/Docker-Enabled-blue.svg)](https://www.docker.com/)
[![Status](https://img.shields.io/badge/Status-POC_Development-orange.svg)]()

## 📖 Visión del Proyecto

AEGIS no es solo un monitor de vehículos; es un **ecosistema de agentes autónomos**.
Creamos **Gemelos Digitales** de vehículos de emergencia (ambulancias, bomberos) capaces de:

1. **Predecir sus propios fallos** antes de que ocurran (Defensa Predictiva).
2. **Operar autónomamente** como nodos en una red distribuida.
3. **Coordinarse en tiempo real** ante situaciones de crisis.

---

## 🏗️ Arquitectura del Sistema

### 1. La Visión

*Lo que aspiramos construir en un entorno real de HPE GreenLake.*

* **Arquitectura:** Microservicios distribuidos con orquestación Kubernetes.
* **Inteligencia:** Modelos locales en el borde (Edge Computing) y entrenamiento federado en la nube.
* **Comunicación:** V2X (Vehicle-to-Everything) usando 5G y WebSockets seguros.

### 2. La Implementación Actual

*Lo que corre actualmente en este repositorio para la demostración.*
El sistema se simula utilizando contenedores Docker para representar los nodos de la red:

1. **Vehicle Nodes (Agentes):** Scripts en Python que simulan la física del vehículo y generan telemetría (sintética/ABM).
2. **Message Broker (Redis/MQTT):** La "tubería" de comunicación en tiempo real.
3. **Central Brain (Orquestador):** Servicio que recibe alertas, gestiona el estado de la flota y asigna recursos.
4. **Dashboard (Frontend):** Visualización en tiempo real del estado de los gemelos y alertas predictivas.

## 👥 Contribución

* Main Branch: Código estable y funcional (POC).

* Release Branch: Integración de nuevas funcionalidades.

* Feature Branches: feature/simulacion-motor, feature/frontend-mapa.

> La clave no es el vehículo en sí, sino la capacidad de anticiparse.
