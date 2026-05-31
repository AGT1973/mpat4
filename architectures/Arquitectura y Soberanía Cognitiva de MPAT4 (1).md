La arquitectura de **MPAT4** se organiza como un sistema modular y evolutivo, fundamentado en un modelo de capas y componentes de "inteligencia soberana". Según los documentos del proyecto, la estructura se desglosa de la siguiente manera:

### 1\. Capas Específicas Documentadas

Aunque la documentación técnica sugiere una visión unificada en archivos como ARQUITECTURA\_base\_V4\_UNIF.md 1, se identifican explícitamente las siguientes capas en los registros de investigación:

* **Capa 0 (Nexo Omnicanal):** Se encarga de la conectividad y la interfaz de entrada/salida a través de múltiples canales 2\.  
* **Capa 3:** Identificada en documentos de investigación específicos de arquitectura 2\.  
* **Capa 5:** Descrita como una capa de "investigación unificada", sugiriendo un nivel de abstracción superior o de orquestación 2\.

### 2\. Componentes Núcleo (Core)

La arquitectura se apoya en elementos transversales que actúan como el motor del sistema:

* **Cognitive OS (Sistema Operativo Cognitivo):** Es el corazón de la arquitectura (cognitive\_os.py), encargado de la lógica operativa y la gestión de estados 1, 3\.  
* **Cognitive Event Mesh:** Definido como el "Sistema Operativo de Inteligencia Soberana", este componente gestiona el enrutamiento y la comunicación de eventos a través de la red (cognitive\_event\_mesh.py) 1, 3, 4\.  
* **A2A Economy (Economía Agente-a-Agente):** Una capa dedicada a la soberanía económica y transaccional entre agentes, gestionada por motores de presupuesto y contratos específicos 1, 3\.

### 3\. Pilares de Seguridad y Trazabilidad

La estructura integra mecanismos de auditoría profunda:

* **Auditoría Inmutable y Trazabilidad:** Utiliza protocolos como **OpenTelemetry** y el protocolo **AESP** para garantizar la seguridad biométrica, la soberanía del usuario y el control de la "deriva cognitiva" 4\.  
* **Audit Ledger:** Un registro inmutable (audit\_ledger.py) que asegura que todas las acciones del sistema sean auditables 1, 3\.

### 4\. Infraestructura y Despliegue

La arquitectura contempla el aislamiento y la eficiencia mediante:

* **Integración con Firecracker:** Para el aislamiento de micro-VMs (según la resolución RES.159) 3\.  
* **Grafos de Memoria Cognitiva:** Para la persistencia y relación de conocimientos dentro del sistema 3\.

Esta estructura está diseñada para permitir la **convergencia** entre versiones anteriores (V3) y la nueva arquitectura V4, asegurando que el registro de agentes y los esquemas de comunicación mantengan la coherencia sistémica 1\.  
