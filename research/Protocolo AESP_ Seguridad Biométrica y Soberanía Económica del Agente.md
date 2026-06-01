Dentro del protocolo **AESP** (Agent Economic Sovereignty Protocol) que utiliza la infraestructura de MPAT, la **validación biométrica** (como Face ID o huella dactilar) representa el nivel más alto de seguridad y se activa específicamente ante **cambios críticos en las políticas** que rigen la autonomía económica del agente 1, 2\.  
Las transacciones o modificaciones que activan obligatoriamente este nivel de validación son 3, 4:

1. **Aumento de presupuesto (budget\_increase):** Cualquier solicitud para incrementar los límites máximos de gasto, ya sea en la ventana diaria, semanal o mensual 4, 5\.  
2. **Escalación de alcance (scope\_escalation):** Cuando se intenta elevar el rango de permisos del agente hacia un nivel de mayor autoridad (por ejemplo, pasar de una política de "solo negociación" a una de "compromiso financiero total") 3, 4\.  
3. **Eliminación total de la lista de permitidos (addr\_remove\_all):** Si se intenta limpiar o vaciar la lista de direcciones (allowlist) a las que el agente tiene permitido enviar fondos, lo cual eliminaría las restricciones de destino 4\.  
4. **Adición de una nueva dirección (addr\_add):** El registro de un nuevo destinatario de pagos en la lista de confianza del agente 4\.

### Justificación de Seguridad

Este mecanismo implementa un modelo de **validación progresiva** 2, 6\. Mientras que las transacciones rutinarias que cumplen con la política se aprueban automáticamente, estas cuatro acciones se consideran de alto riesgo porque podrían permitir que un agente (o un atacante que haya tomado control de él) drene los activos del usuario. La validación biométrica garantiza que el usuario humano mantenga la **soberanía económica**, exigiendo su presencia física y autenticación antes de que los límites o permisos del sistema puedan ser matemáticamente alterados 2, 6, 7\.  
