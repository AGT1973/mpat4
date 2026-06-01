Aunque los documentos describen el **Cognitive Drift** (deriva cognitiva) y el protocolo **AESP** como conceptos complementarios en la infraestructura de MPAT, el protocolo AESP previene estos ataques y fallos sistémicos mediante mecanismos de control de soberanía que blindan el comportamiento del agente frente a "empujones" contextuales maliciosos.  
El protocolo AESP mitiga el **Cognitive Drift** a través de las siguientes estrategias técnicas:

### 1\. Detección de Violaciones Agregadas y Límites de Presupuesto

Los ataques de deriva cognitiva suelen ocurrir mediante pequeños cambios incrementales que, de forma aislada, parecen normales 1\. AESP contrarresta esto mediante su **Engine de Políticas de 8 comprobaciones** 2:

* **Límites de Presupuesto Rodantes:** AESP no solo revisa transacciones individuales, sino totales diarios, semanales y mensuales 3\. Esto bloquea las **"violaciones agregadas"**, donde una secuencia de transacciones individualmente permitidas intenta agotar recursos o desviar fondos de forma gradual 4, 5\.  
* **Comprobación de Primer Pago:** Cualquier interacción con un destinatario nuevo (que podría ser el resultado de un cambio en las "creencias" del agente sobre en quién confiar) es rechazada automáticamente para revisión humana 3, 6\.

### 2\. Aislamiento de Contexto mediante HKDF

Una de las causas del Cognitive Drift es que la memoria persistente y las señales de telemetría distorsionan el marco interpretativo del modelo 7, 8\. AESP utiliza **Privacidad Aislada por Contexto** basada en **HKDF** 9, 10:

* Cada transacción genera una dirección efímera e independiente basada en un **string de contexto único** (ID de agente, dirección, número de secuencia y ID de transacción) 10\.  
* Al ser claves criptográficamente independientes, se evita la "gravedad interpretativa" donde una transacción pasada influye erróneamente en el contexto de una nueva 11, 12\.

### 3\. Clasificación de Cambios Críticos y Validación Biométrica

El Cognitive Drift puede intentar que un agente "reescriba" sus propios permisos de forma silenciosa 13\. AESP previene esto clasificando las modificaciones de políticas 14:

* Cualquier cambio que amplíe el alcance del agente (*scope escalation*) o incremente presupuestos requiere **confirmación biométrica** del usuario (Face ID, huella) en su dispositivo personal 15, 16\.  
* Esto asegura que los "pequeños empujones" contextuales no puedan alterar matemáticamente el sistema de creencias (permisos) del protocolo sin una presencia física explícita 2, 16\.

### 4\. Gobernanza Humana (Human-in-the-Loop)

El reporte sobre seguridad cognitiva identifica la supervisión humana como una mitigación crítica para que los agentes expongan sus vías de razonamiento 17\. AESP implementa esto mediante su **ReviewManager** 18:

* Cualquier acción sospechosa o fuera de la política establecida se coloca en una **cola de revisión prioritaria** 19\.  
* Esto permite al usuario auditar el "hilo de pensamiento" del agente antes de que la deriva cognitiva se traduzca en una acción económica irreversible 20, 21\.

### 5\. Invariante de Soberanía y Congelación de Emergencia

Para evitar que un agente que ha sufrido deriva continúe operando, el protocolo mantiene la máxima de que los agentes son "económicamente capaces pero nunca soberanos" 9\. El principal humano posee un **comando de congelación (Emergency Freeze)** que detiene inmediatamente toda actividad económica y rechaza cualquier solicitud pendiente si detecta anomalías en el comportamiento del agente 22, 23\.  
