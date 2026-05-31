# MPAT4

Infraestructura Cognitiva Distribuida.

## Filosofía

MPAT4 deja de ser un framework multiagente tradicional.
Ahora funciona como:

- Cognitive Infrastructure OS
- Runtime cognitivo efímero
- Gobernanza ejecutable
- Event sourcing cognitivo
- Memory Fabric soberano

## Orden recomendado

1. contracts/
2. schemas/
3. event_bus/
4. memory_fabric/
5. governance_engine/
6. session_scheduler/
7. runtimes/
8. agent_registry/
9. observability/

## Regla crítica

NO comenzar implementando agentes.

Primero:
- contratos,
- eventos,
- memoria,
- gobernanza,
- runtime.
