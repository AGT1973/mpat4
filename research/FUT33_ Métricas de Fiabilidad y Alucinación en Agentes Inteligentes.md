La investigación **FUT33**, titulada específicamente como **"Métrica de Alucinación"** en los registros de MPAT4, tiene como objetivo establecer parámetros medibles para evaluar la fiabilidad de las respuestas de los agentes inteligentes 1\.  
Aunque el contenido detallado de las fórmulas matemáticas no se encuentra íntegro en los fragmentos, la documentación de arquitectura y las guías de evaluación de agentes para 2026 vinculadas al proyecto identifican las siguientes métricas y criterios de evaluación relacionados:

* **Tasa de Alucinación (Hallucination Rate):** Es la métrica principal, definida como el porcentaje de respuestas que contienen errores factuales. El objetivo establecido para un sistema de producción es que sea **inferior al 2%** 2\.  
* **Umbrales de Confianza (Confidence Thresholds):** FUT33 se encarga de determinar los niveles de confianza aceptables antes de que el sistema proceda con una tarea. Si la respuesta del modelo cae por debajo de este umbral, el sistema puede derivar la acción a un estado de **"REVIEW"** (revisión humana) en lugar de ejecutarla directamente Conversación Previa, 385, 104\.  
* **Alineación con la Memoria (Grounding):** La métrica evalúa la consistencia de la respuesta frente a los **grafos de memoria cognitiva** (RES167). El **Hallucination Guard** (FUT19) utiliza esta memoria como punto de referencia veraz para contrastar si la información generada es factual o inventada Conversación Previa, 385\.  
* **Métricas de Desempeño Relacionadas:** Para una evaluación integral del agente, se consideran también:  
* **Tasa de Éxito (Success Rate):** Porcentaje de consultas completadas con éxito (objetivo \> 95%) 2\.  
* **Tasa de Éxito de Herramientas:** Precisión en las llamadas a funciones externas (objetivo \> 98%) 2\.  
* **Iteraciones Promedio:** Cantidad de ciclos de razonamiento (ReAct) antes de llegar a una conclusión, lo que ayuda a detectar bucles infinitos o razonamientos erróneos 2\.

En el contexto de la seguridad, estas métricas permiten diferenciar entre operaciones **"SAFE"** e **"INAPPROPRIATE"** o de riesgo, permitiendo que el **Cognitive OS** bloquee o modifique salidas que no cumplan con los estándares de veracidad establecidos por la investigación de FUT33 1, 3\.  
