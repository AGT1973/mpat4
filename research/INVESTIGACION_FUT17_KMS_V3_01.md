\# INVESTIGACION\_FUT17\_KMS\_V3\_01.md  
\#\# MPAT — FUT.17 · KMS Key Management Service  
\#\# Autor: ariel.garcia.traba@gmail.com · RELAY\_005 · 2026-05-12  
\#\# RES efectiva: RES.087 (KMSCoordinator)

\*que has usado el formato de razonamiento adaptado por AGT\*

\---

\#\# IDENTIFICACION DEL GAP

| Campo | Valor |  
|---|---|  
| FUT | FUT.17 |  
| Descripcion original | KMS Key Management Service |  
| Capa asignada | Capa 3 (catalogo) / Capa 4 (implementacion real) |  
| RES catalogo | RES.068 |  
| RES real implementada | RES.087 (KMSCoordinator) |  
| Estado anterior | GAP — presente como dependencia en capa\_4\_V2\_86 (RES.090) sin investigacion propia |  
| Estado post-RELAY\_005 | CERRADO — investigacion formal generada |

\---

\#\# CONTEXTO ARQUITECTURAL

FUT.17 fue planificado en el catalogo original como un servicio de gestion de claves  
criptograficas de proposito general. Su implementacion real se materializo como  
\`KMSCoordinator\`, un componente que opera como facade sobre las operaciones de clave  
en todo el sistema MPAT.

La primera evidencia de KMSCoordinator en el codigo aparece en \`capa\_4\_V2\_86\_fut22.md\`  
(RES.090 — Audit Trail E2EE), donde figura como dependencia directa:

\`\`\`  
Depende: KMSCoordinator (RES.087) · AuthMiddleware (Capa 2\)  
\`\`\`

El namespace Redis del KMS es:  
\`\`\`  
mpat:kms:ik:{tenant\_id}        → Identity Key del tenant (IK)  
mpat:kms:audit:{tenant\_id}     → AuditKey derivada (key-wrapping)  
mpat:kms:{proposito}:{id}      → patron general para claves derivadas  
\`\`\`

\---

\#\# DECISION TECNICA — RES.087

| Campo | Valor |  
|---|---|  
| Item cerrado | FUT.17 |  
| Fecha | 2026-05-08 (inferida de RES.090) |  
| Decision | KMSCoordinator como facade centralizado. Almacena IK por tenant cifrada con clave maestra. Provee wrap\_key / unwrap\_key / get\_identity\_key para derivaciones HKDF. Aislamiento por tenant: cada tenant tiene su IK propia. |  
| Patron | Key Wrapping \+ HKDF para derivaciones de proposito especifico |  
| Algoritmo base | AES-256-GCM para wrapping \+ HKDF-SHA256 para derivacion |  
| Capa afectada | Capa 3 (seguridad) \+ Capa 4 (dependencia directa) |

\---

\#\# RESPONSABILIDADES DEL KMSCoordinator

\#\#\# 1\. Gestion de Identity Keys (IK) por tenant

La IK es la clave raiz por tenant. De ella se derivan todas las claves de proposito  
especifico mediante HKDF. Nunca se usa directamente para cifrar datos.

\`\`\`python  
\# Patron de derivacion HKDF en MPAT  
\# Usado por: AuditKeyManager, Signal E2EE (FUT.03), futuros derivadores

from cryptography.hazmat.primitives.kdf.hkdf import HKDF  
from cryptography.hazmat.primitives import hashes

def derivar\_clave(identity\_key: bytes, tenant\_id: str, proposito: str) \-\> bytes:  
    """  
    Patron estandar de derivacion HKDF en MPAT.

    Precondicion: identity\_key \!= None, len(identity\_key) \>= 32  
    Postcondicion: clave derivada de 32 bytes, especifica para (tenant\_id, proposito)  
    INV-KMS.1: claves de distinto proposito son criptograficamente independientes  
    INV-KMS.2: salt=tenant\_id garantiza separacion entre tenants  
    """  
    hkdf \= HKDF(  
        algorithm=hashes.SHA256(),  
        length=32,  
        salt=tenant\_id.encode(),  
        info=proposito.encode(),  
    )  
    return hkdf.derive(identity\_key)

\# Ejemplos de proposito en MPAT:  
\# b"audit\_trail\_v1"     → AuditKey (RES.090)  
\# b"signal\_e2ee\_v1"     → Signal session key (RES.057 / FUT.03)  
\# b"session\_wrap\_v1"    → Session encryption key  
\`\`\`

\#\#\# 2\. Key Wrapping (doble capa)

Las claves derivadas nunca se almacenan en claro en Redis.  
Se cifran con la clave maestra del KMSCoordinator antes de persistir.

\`\`\`  
Flujo de escritura:  
  IK (en memoria) → HKDF → clave\_derivada → wrap(clave\_maestra) → Redis HASH

Flujo de lectura:  
  Redis HASH → unwrap(clave\_maestra) → clave\_derivada (en memoria) → uso  
\`\`\`

\#\#\# 3\. Interfaz publica del KMSCoordinator

\`\`\`python  
class KMSCoordinator:  
    """  
    Facade centralizado de gestion de claves para MPAT.

    RES: RES.087  
    Namespace: mpat:kms:\* (Redis)  
    Capa: 3 (seguridad) — consumido por Capa 4, Capa 9  
    """

    async def get\_identity\_key(self, tenant\_id: str) \-\> bytes:  
        """  
        Retorna la IK del tenant en memoria (nunca loguear).  
        Precondicion: tenant\_id registrado en el sistema.  
        Postcondicion: retorna 32 bytes de IK en claro.  
        INV-KMS.3: IK no se copia a disco ni a logs.  
        """  
        ...

    async def wrap\_key(self, key: bytes, context: str) \-\> bytes:  
        """  
        Cifra una clave derivada con la clave maestra.  
        context: string de auditoria (ej: "audit:tenant\_abc")  
        """  
        ...

    async def unwrap\_key(self, wrapped\_key: bytes, context: str) \-\> bytes:  
        """  
        Descifra una clave derivada previamente wrapeada.  
        """  
        ...

    async def rotate\_identity\_key(self, tenant\_id: str) \-\> None:  
        """  
        Rota la IK del tenant. Invalida todas las claves derivadas activas.  
        Postcondicion: nueva IK generada, claves derivadas re-derivadas o expiradas.  
        INV-KMS.4: rotacion es atomica — no hay ventana donde IK vieja y nueva coexisten.  
        """  
        ...  
\`\`\`

\---

\#\# RELACION CON OTROS COMPONENTES

| Componente | Relacion | RES |  
|---|---|---|  
| Signal E2EE (FUT.03) | Usa IK como base del Double Ratchet | RES.057 |  
| AuditCoordinator (FUT.22) | Deriva AuditKey via HKDF desde IK | RES.090 |  
| NHP Protocol (FUT\_3) | Handshake criptografico agente-a-agente | RES.120 |  
| ZeroTrustSession (FUT\_3) | Claves de sesion derivadas post-NHP | RES.120 |  
| AuthMiddleware (Capa 2\) | RBAC para acceso a operaciones KMS admin | — |

\---

\#\# INVARIANTES DE DISEÑO

\`\`\`  
INV-KMS.1: Separacion criptografica de proposito.  
           HKDF con info distinto → claves independientes aunque la IK sea la misma.

INV-KMS.2: Separacion por tenant.  
           salt=tenant\_id en HKDF → claves distintas para distintos tenants.

INV-KMS.3: IK nunca persiste en claro.  
           La IK solo existe en memoria durante operaciones. Se almacena wrapeada.

INV-KMS.4: Rotacion atomica.  
           No existe ventana donde dos IKs son validas simultaneamente.

INV-KMS.5: Aislamiento de fallo.  
           Un tenant comprometido no expone las IKs de otros tenants.  
\`\`\`

\---

\#\# PARAMETROS CAPA 14

\`\`\`yaml  
kms:  
  master\_key\_rotation\_days: 90        \# rango: \[30, 365\]  
  ik\_ttl\_seconds: 0                   \# 0 \= sin expiracion automatica (rotacion manual/evento)  
  wrap\_algorithm: "AES-256-GCM"       \# no configurable en produccion  
  hkdf\_hash: "SHA-256"                \# no configurable en produccion  
  namespace\_prefix: "mpat:kms"        \# rango: string valido Redis  
\`\`\`

\---

\#\# ESTADO Y CONCLUSION

FUT.17 fue implementado como \`KMSCoordinator\` (RES.087) con anterioridad a este  
documento de investigacion. La implementacion cubre:

\- Gestion de IK por tenant en Redis (wrapeadas)  
\- Patron HKDF para derivacion de claves de proposito especifico  
\- Interfaz wrap\_key / unwrap\_key para componentes dependientes  
\- Soporte a rotacion de claves

La ausencia de investigacion formal no significaba ausencia de implementacion.  
Este documento formaliza el respaldo tecnico de RES.087 y cierra el GAP  
documentario de FUT.17.

\*\*FUT.17 → CERRADO · RES.087 · RELAY\_005 · 2026-05-12\*\*

\---

\#\# COLISION DE NUMERACION DETECTADA

El catalogo original asigno RES.068 a FUT.17 (KMS).  
La implementacion real uso RES.087 (KMSCoordinator).  
Ver MAPA\_RES\_CANONICO\_V3\_01.md para resolucion definitiva.

\---

\*INVESTIGACION\_FUT17\_KMS\_V3\_01.md · RELAY\_005 · ariel.garcia.traba@gmail.com · 2026-05-12\*  
\*que has usado el formato de razonamiento adaptado por AGT\*  
