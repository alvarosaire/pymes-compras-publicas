# FASE 2: carga de documentos

En el mismo diagrama aparecen FASE 0, FASE 1 y FASE 2. FASE 3 permite cargar propuestas vinculadas al expediente (ver FASE_3.md). FASE 4 permite registrar una solicitud de revisión de bases (ver FASE_4.md); el análisis está pendiente.

1. Guarda primero el perfil de la empresa en FASE 0.
2. Abre http://127.0.0.1:5680/form/pymes-documentos.
3. Introduce el RUC y la referencia de la convocatoria elegida.
4. Adjunta un archivo de bases y entre uno y diez documentos de empresa.
5. Guarda y conserva el folio mostrado en el comprobante.

Formatos: PDF, DOCX o TXT UTF-8. Máximo 5 MB por archivo y 10 MB por envío. Cada envío crea un expediente nuevo. La referencia de convocatoria es declarada por el usuario.

Los documentos y su manifiesto se guardan en /data/expedientes dentro del volumen persistente del servicio pymes-sunat. Reiniciar el contenedor no los borra; eliminar el volumen sí. Este volumen contiene datos privados y no se incluye en el ZIP compartible.

Esta fase comprueba formato y recepción. No extrae texto, no evalúa requisitos, no verifica autenticidad y no envía documentos a un modelo. El siguiente paso será conectar el análisis de bases y la comparación con los documentos usando una API de IA.

Es un prototipo local para un equipo de confianza. Antes de ofrecerlo a varias empresas se requiere autenticación y separación de expedientes por usuario: conocer un RUC no acredita representación.


