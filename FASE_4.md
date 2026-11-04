# FASE 4: solicitud de revisión de bases

Formulario: http://127.0.0.1:5680/form/pymes-revision

## Uso
1. Indica RUC y folio de la FASE 2.
2. Opcionalmente describe el requisito que te preocupa, su página o sección y una fuente adicional. Si lo dejas vacío, se registra una solicitud de revisión general.
3. Conserva el identificador de solicitud del comprobante.

No necesitas completar la FASE 3 ni subir de nuevo las bases. Hay enlaces a este formulario desde los comprobantes de las fases 2 y 3.

## Qué funciona
- Comprueba que el expediente existe y corresponde al RUC indicado.
- Comprueba que las bases están almacenadas y conservan su hash original.
- Guarda cada solicitud por separado en /data/expedientes/FOLIO/revisiones/ID/solicitud.json, en el volumen persistente.
- Muestra el trabajo pendiente y conserva la inquietud como información declarada, no como hallazgo.

## Qué está pendiente
No hay análisis de contenido, consulta normativa, detección automática, conclusión legal ni borrador de observación. Los campos de hallazgos, conclusión y borrador permanecen nulos. Registrar la solicitud no programa un agente para ejecutarla en segundo plano.

Para habilitar el agente se requiere conectar un modelo y la recuperación de texto y fuentes normativas verificables. Cada posible restricción deberá vincularse al fragmento de las bases, la fuente aplicable y la evidencia. Una alerta no prueba corrupción. Todo borrador debe revisarse antes de presentarlo; este flujo no envía comunicaciones a la entidad.

La fuente adicional es solo texto declarado y no se descarga automáticamente. El prototipo permanece local; conocer el RUC y folio no sustituye autenticación ni permisos de acceso para un servicio multiempresa.
