En la práctica, el **handoff de agentes** es el proceso mediante el cual un agente inteligente transfiere el control, el contexto y la responsabilidad de una tarea a otro agente especializado o a un supervisor humano 1-3. Este mecanismo es fundamental para resolver problemas complejos que requieren diversas áreas de experiencia o niveles de autoridad.  
Según las fuentes, el handoff funciona a través de los siguientes modelos y mecanismos prácticos:

### 1\. Arquitecturas de Transferencia de Control

Existen diferentes enfoques según el marco de trabajo (framework) utilizado:

* **Handoff basado en SDK (OpenAI):** El **OpenAI Agents SDK** utiliza una arquitectura específicamente diseñada para el handoff, donde los agentes tienen la capacidad intrínseca de transferir el control mutuo de forma directa 1\.  
* **Delegación Jerárquica (Google ADK):** En este modelo, existe un **agente raíz** que organiza "árboles de agentes" y delega subtareas a sub-agentes especializados 2\. Este sistema soporta el protocolo **A2A (Agent-to-Agent)**, permitiendo que agentes de diferentes plataformas se comuniquen y colaboren 2\.  
* **Orquestación Centralizada (Modelo "Lobster"):** En sistemas como SafeClaw-R, un nodo principal (denominado *lobster*) actúa como orquestador, procesando la solicitud inicial y realizando el **enrutamiento de tareas** hacia agentes funcionales específicos que poseen las habilidades ("skills") necesarias 4, 5\.

### 2\. Mecanismos Operativos del Handoff

Para que la transferencia sea efectiva y segura, el sistema implementa:

* **Enrutamiento de Tareas:** Un componente de orquestación analiza la consulta y determina qué agente especialista es el más adecuado para continuar el flujo de trabajo 2, 6\.  
* **Preservación de Contexto:** Durante el handoff, se debe asegurar que el historial de la conversación y los datos relevantes se transfieran al nuevo agente para evitar que el usuario tenga que repetir información 7\.  
* **Protocolos de Comunicación (A2A):** Estos estándares facilitan que los agentes intercambien datos de manera estructurada, incluso si fueron construidos con diferentes tecnologías 2\.

### 3\. Handoff de IA a Humano (Human-in-the-Loop)

Un aspecto crítico en sectores como la salud es la capacidad de escalar la tarea a un profesional humano:

* **Escalada por Juicio Clínico:** En proyectos como **Agent PULSE**, se implementan mecanismos de handoff hacia proveedores de salud cuando se requiere un juicio clínico complejo que la IA no puede proporcionar 8\.  
* **Interrupciones y Alertas:** El sistema puede generar alertas automáticas o pausar el flujo de trabajo (interrupciones estáticas o dinámicas) para solicitar la intervención de un supervisor antes de proceder con acciones críticas 9-11.

### 4\. Seguridad y Trazabilidad en la Delegación

Desde el punto de vista de la gobernanza, el handoff no es solo una transferencia técnica, sino también legal y de seguridad:

* **Cadena de Autoridad:** El sistema debe realizar un seguimiento de la **cadena de autoridad** para saber qué agente delegó a quién y bajo qué permisos 3\.  
* **Herencia de Permisos:** Se definen reglas sobre cómo se heredan los permisos de acceso a recursos cuando una tarea se delega entre sub-agentes 3\.  
* **Auditoría Inmutable:** Cada transferencia de control y delegación de subtareas queda registrada para permitir auditorías posteriores sobre el comportamiento del sistema 3\.

En resumen, el handoff permite que el ecosistema de agentes funcione como un **equipo dinámico**, donde la tarea fluye hacia el recurso (IA o humano) más capacitado para resolverla en cada momento, siempre bajo un marco de control y seguridad.  
