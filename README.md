# Compras públicas para PYMES peruanas

Prototipo de equipo para una hackatón de agentes de IA. ¿Cómo puede una PYME encontrar una convocatoria relevante y saber qué le falta antes de preparar su oferta? La demo conecta formularios de n8n con un servicio en Python para recorrer ese proceso y conservar la evidencia que respalda cada revisión.

| Fase | Qué hace la demo |
| --- | --- |
| 0 · Perfil | Consulta el RUC en una copia local del padrón reducido de SUNAT y guarda lo que ofrece la empresa. |
| 1 · Oportunidades | Busca convocatorias por productos, región y fechas. Las coincidencias son un filtro inicial. |
| 2 · Documentos | Recibe las bases y los documentos de la empresa. Un flujo opcional con Gemini compara requisitos, indica qué no puede verificar y propone referencias para revisión humana. |
| 3 · Propuesta | Guarda versiones de la oferta y, si existe, una referencia para compararla. La puntuación automática quedó como trabajo futuro. |
| 4 · Revisión de barreras | Registra una inquietud sobre las bases para su revisión. No determina que exista corrupción. |

**Cómo probarlo:** con Podman y un proveedor de Compose disponibles, ejecuta `podman compose up -d --build` desde esta carpeta. Abre <http://127.0.0.1:5680>, crea tu usuario local e importa `workflows/01-recibir-ruc.json` desde el editor de n8n. Pulsa **Execute** y escribe un RUC: esta primera prueba solo comprueba el formato, sin descargar datos ni configurar claves.

Para continuar, consulta la [guía de instalación](GUIA_LOCAL.md), las [instrucciones del padrón](CONSULTA_RUC.md) y la [revisión opcional con Gemini](GEMINI_FASE_2.md). Cada instalación usa sus propios datos y credenciales. Los resultados de IA son borradores: una cita propuesta o una coincidencia no acreditan que el proveedor cumpla las bases.

**Tecnologías:** n8n, Python, SQLite y Podman. Los flujos visuales están en `workflows/` y el servicio que consulta y guarda los datos en `sunat/`.
