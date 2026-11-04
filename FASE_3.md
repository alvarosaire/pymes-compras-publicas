# FASE 3: preparar la revisión de propuesta

Disponible en el mismo diagrama, con la etiqueta FASE 3.
Formulario: http://127.0.0.1:5680/form/pymes-propuesta

## Uso
1. Completa la carga de documentos de la FASE 2 y conserva su folio.
2. Introduce ese folio y el RUC en la FASE 3.
3. Adjunta tu propuesta (PDF, DOCX o TXT UTF-8).
4. Opcionalmente adjunta una propuesta pública o autorizada de referencia e indica su procedencia. El sistema no obtiene ofertas de otros postores ni verifica la procedencia declarada.
5. Guarda. Recibirás el identificador de una versión nueva, sin sobrescribir versiones previas.

Máximo 5 MB por archivo y 10 MB por envío. Se almacena en el volumen persistente, bajo /data/expedientes/FOLIO/propuestas/VERSION. El sistema comprueba que el expediente exista y que su RUC coincida; esto no sustituye autenticación de usuarios.

## Estado real
Funciona la recepción, validación básica de formato, asociación al expediente, almacenamiento y comprobante. No se realiza análisis de contenido ni comparación automática. No se calculan puntajes ni probabilidades de ganar.

Para la evaluación falta conectar un modelo, extraer texto y evidencias, disponer de la matriz de requisitos de FASE 2 y aplicar los criterios publicados de cada convocatoria. Una propuesta de referencia por sí sola no permite estimar una probabilidad de adjudicación.

Los documentos permanecen locales y no se incluyen en el paquete ZIP. No usar como servicio multiempresa hasta añadir autenticación y permisos por expediente.
