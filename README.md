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

* **Vehicle Nodes (Agentes):** Scripts en Python que simulan la física del vehículo y generan telemetría (sintética/ABM).
* **Message Broker (Redis/MQTT):** La "tubería" de comunicación en tiempo real.
* **Central Brain (Orquestador):** Servicio que recibe alertas, gestiona el estado de la flota y asigna recursos.
* **Dashboard (Streamlit):** Visualización en tiempo real del estado de los gemelos y alertas predictivas.

---

## 🚀 Roadmap & Consideraciones Futuras

Para escalar AEGIS a un entorno de producción masivo y mejorar la autonomía de los agentes, el proyecto contempla las siguientes evoluciones arquitectónicas:

### A. Defensa Predictiva Bio-inspirada en el Edge

Mover la inferencia de anomalías directamente al hardware del vehículo (IoT) para reducir latencia y dependencia de la red.

* **Estrategia:** Transición de modelos tradicionales a Autoencoders LSTM o **Redes Neuronales Pulsantes (SNNs)**. El uso de SNNs, inspiradas en la neurociencia computacional, permitirá procesar series de tiempo de telemetría de forma asíncrona, reduciendo drásticamente el consumo energético en los microcontroladores del vehículo.

### B. Ecosistema MARL (Multi-Agent Reinforcement Learning)

Eliminar el punto único de fallo del "Cerebro Central" permitiendo que los agentes negocien rutas y prioridades entre ellos.

* **Estrategia:** Implementar algoritmos como MAPPO integrados con Graph Neural Networks (GNNs). Esto permitirá modelar la ciudad como un grafo espacial, donde cada gemelo digital aprende a tomar decisiones descentralizadas para maximizar una recompensa global (ej. minimizar el tiempo de respuesta de toda la flota ante un desastre).

### C. Motor de Simulación de Alta Concurrencia

Superar las limitaciones del Global Interpreter Lock (GIL) de Python en la generación masiva de telemetría sintética.

* **Estrategia:** Reescritura del motor físico y de generación de agentes utilizando lenguajes de bajo nivel seguros en memoria como **Rust**. Esto habilitará una concurrencia masiva real, permitiendo simular miles de vehículos enviando datos vía WebSockets a altos *tick rates* sin colapsar el orquestador, manteniendo a Python exclusivamente para la inferencia de IA pesada.

## 👥 Contribución

* Main Branch: Código estable y funcional (POC).

* Release Branch: Integración de nuevas funcionalidades.

* Feature Branches: feature/simulacion-motor, feature/frontend-mapa.

> La clave no es el vehículo en sí, sino la capacidad de anticiparse.
