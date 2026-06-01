El **registro de auditoría inmutable** asegura la trazabilidad mediante el uso de estructuras de datos criptográficamente encadenadas que impiden la alteración de los registros históricos. 1 En la arquitectura de MPAT, este mecanismo se fundamenta en los siguientes pilares técnicos:

### 1\. Criptografía de Bloques Encadenados

El sistema utiliza una arquitectura de **"Ledger" o Árboles de Merkle** para garantizar la integridad de los datos. 1 Cada evento de ejecución de un agente, log, cambio en la memoria o llamada a herramientas se empaqueta en una estructura JSON. 1 Para cada bloque, el sistema calcula un hash **SHA-256** e inyecta obligatoriamente el hash del bloque cronológico anterior, creando una cadena lógica inalterable. 1 Esto hace matemáticamente imposible que un atacante o un agente malicioso borre sus huellas o altere los registros históricos sin invalidar toda la cadena de auditoría. 1

### 2\. Trazabilidad del "Hilo de Pensamiento"

La trazabilidad no se limita a las acciones finales, sino que abarca el proceso de razonamiento del agente. 2 Mediante el uso de **OpenTelemetry y Arize Phoenix**, el sistema genera objetos específicos (*Spans*) que capturan los prompts de entrada, las respuestas del modelo, los tokens consumidos y las latencias exactas. 2 Esto permite realizar auditorías visuales del "hilo de pensamiento" y detectar bucles infinitos o fallos lógicos durante la ejecución. 2

### 3\. Etiquetas de Contexto (Context Tags)

Para conciliar la privacidad con la necesidad de supervisión, protocolos como **AESP** implementan **"Context Tags" cifrados**. 3 Estas etiquetas registran:

* El ID del agente y el ID de la política aplicada. 3  
* El ID del compromiso y las direcciones efímeras utilizadas. 3  
* Metadatos de la transacción. 3Estas etiquetas se almacenan localmente y pueden archivarse de forma cifrada en almacenamiento permanente (como Arweave), permitiendo que el propietario de los activos reconstruya el historial completo para fines de auditoría sin comprometer la privacidad frente a observadores externos. 3, 4

### 4\. Visibilidad y Gobernanza en Sistemas Distribuidos

En entornos multiagente (A2A), la trazabilidad es esencial para la rendición de cuentas. 5 El protocolo permite retener **pistas de auditoría detalladas** que monitorean la actividad de los agentes a través de sistemas distribuidos. 5 Esta visibilidad es un requisito crítico en sectores altamente regulados, como los servicios financieros y la salud, donde cada decisión debe ser rastreable y justificada ante las autoridades. 5

### 5\. Registro de Eventos de Gobernanza

El sistema de revisión de MPAT emite seis tipos de eventos específicos (creación, aprobación, rechazo, modificación, expiración y cancelación de solicitudes) a los que los sistemas externos de auditoría pueden suscribirse. 6 Esto garantiza que cualquier intervención humana en el bucle de decisión quede registrada de forma permanente como parte de la historia operativa del sistema. 6  
