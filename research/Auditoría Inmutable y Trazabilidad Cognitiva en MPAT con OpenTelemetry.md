La integración del registro de auditoría con **OpenTelemetry** en la infraestructura de MPAT se realiza mediante un sistema de **rastreo distribuido "agentic"** diseñado para auditar el razonamiento y la ejecución de los agentes de forma granular 1\.  
Esta integración se articula a través de los siguientes componentes técnicos:

* **Decoración de Funciones Críticas:** Se emplea el SDK de OpenTelemetry para decorar funciones relacionadas con llamadas a modelos de lenguaje (LLMs), ejecuciones de herramientas (*skills*) y cambios en los estados internos de los agentes 1\.  
* **Generación de Objetos Span:** El sistema crea objetos de rastreo específicos llamados **AgentSpan, ToolSpan y LLMSpan** 1\. Estos objetos capturan metadatos esenciales como:  
* Los *prompts* de entrada y las respuestas generadas por el modelo 1\.  
* El consumo exacto de tokens y las latencias de ejecución 1\.  
* **Exportación vía Protocolo OLTP:** Los rastreos y métricas se exportan utilizando el **OpenTelemetry Protocol (OLTP)** hacia una instancia local de **Arize Phoenix** 1\. Esto permite una visualización detallada del "hilo de pensamiento" del agente, facilitando la detección de bucles infinitos o fallos lógicos durante las tareas 1\.  
* **Conexión con la Auditoría Inmutable:** Los datos recolectados por esta capa de observabilidad se integran en el registro de auditoría general, donde cada evento y *trace* se empaqueta en una estructura JSON 2\. Para asegurar la integridad, el sistema aplica un **hashing SHA-256 encadenado**, inyectando el hash del bloque anterior en el nuevo, lo que garantiza que los registros de OpenTelemetry persistidos sean matemáticamente inalterables 2\.

Este enfoque permite que la gobernanza del sistema MPAT no solo se limite a ver el resultado final, sino que pueda **auditar cada paso del proceso cognitivo** del agente de manera inmutable y observable 1, 3\.  
