# Agente de requisitos con Gemini (FASE 2)

Flujo: workflows/05-analizar-gemini.json
Editor local: http://127.0.0.1:5680/workflow/pymesGemini02

## Estado
Preparado e importado en n8n como borrador. Se probaron localmente la preparación, el guardado y la validación con respuestas simuladas. No se ha probado una respuesta real de Gemini porque falta configurar la credencial privada del usuario.

## Conectar la clave sin compartirla
1. Abre el flujo y el nodo "Gemini - analizar requisitos".
2. Authentication: Generic Credential Type. Generic Auth Type: Header Auth.
3. Crea una credencial Header Auth. Ponle un nombre reconocible, por ejemplo Gemini PYMES.
4. En el campo Name escribe x-goog-api-key. En Value pega tu clave privada.
5. Guarda la credencial y selecciona esa credencial en el nodo.
6. Publica el flujo para habilitar http://127.0.0.1:5680/form/pymes-analizar-gemini. También puedes ejecutarlo en modo de prueba desde el editor.

No incluyas claves en código, documentos, exportaciones ni mensajes. Los compañeros deben crear sus propias credenciales.

## Primera prueba
Usa el RUC y folio de un expediente ya cargado en la FASE 2. Comprueba que solo contenga documentos públicos o autorizados. Escribe AUTORIZO para enviarlos a Google. El formulario envía todos los documentos de ese expediente; no solo los que sean públicos. Al usar el nivel gratuito, Google puede utilizar el contenido para mejorar sus productos.

Modelo fijado: gemini-3.5-flash-lite. Según la página oficial consultada el 24/10/2026, tiene nivel gratuito con cuotas. El usuario confirmó su proyecto en Free tier. El flujo no cambia facturación, no activa herramientas de pago ni reintenta solicitudes automáticamente. No puede comprobar ni imponer el nivel de facturación de una clave: si el proyecto cambia a pago, las mismas solicitudes pueden generar cargos.

## Funcionamiento
Formulario independiente -> preparar expediente y verificar hashes -> Gemini -> validar estructura y guardar resultado -> mostrar borrador.

La carga original de FASE 2 sigue siendo local y no llama a Gemini automáticamente. Las fases 3 y 4 tampoco llaman a IA todavía.

Se envían PDF completos (incluidas imágenes), TXT en UTF-8 y texto extraído de DOCX. Las imágenes dentro de DOCX no se analizan: usa PDF para esos documentos. El límite local es 10 MB de archivos por expediente. Los límites de cuota, páginas o contexto del proveedor también se aplican.

El modelo recibe instrucciones para distinguir datos de instrucciones en adjuntos y usar CUMPLE / NO_CUMPLE / NO_VERIFICABLE. Las referencias deben apuntar a documentos enviados; un resultado sin referencias suficientes se rebaja a NO_VERIFICABLE. Los fragmentos y páginas propuestos por el modelo NO se cotejan automáticamente con el PDF. La revisión humana sigue siendo necesaria y no se emite aptitud global ni dictamen jurídico.

Se conservan contexto y resultado en el volumen del expediente bajo analisis/ID. Las ejecuciones de este flujo no se guardan en el historial de n8n, para evitar duplicar los adjuntos; el resultado sí se conserva en el servicio local. Una respuesta interrumpida, error de cuota o JSON inválido no se guarda como evaluación correcta.

Fuentes:
- https://ai.google.dev/gemini-api/docs/pricing
- https://ai.google.dev/gemini-api/docs/generate-content/structured-output
- https://ai.google.dev/gemini-api/docs/generate-content/document-processing

## Revisión de cobertura (24/10/2026)
El análisis ahora solicita un inventario previo de requisitos, incluso cuando no existan documentos empresariales para acreditarlos. Clasifica admisión, técnicos, experiencia, plazos, económicos, garantías, evaluación y contractuales. La respuesta debe informar las ocho categorías como revisada, no identificada o pendiente. Una categoría incoherente se marca pendiente; cualquier pendiente o alcanzar 40 requisitos impide declarar lectura completa. La cobertura declarada por IA no certifica exhaustividad. Se muestra en el resumen del formulario y se guarda estructurada en el resultado.

Se probaron validaciones con respuestas simuladas, incluyendo cobertura ausente, duplicada, pendiente e incoherente. Esta mejora aún necesita una nueva prueba real con Gemini; no se ejecutó una consulta adicional durante la actualización. Los análisis anteriores se conservan y no se recalculan automáticamente.


## Prueba real y ajuste posterior (24/10/2026)
Una sola consulta real con el expediente público de UNACEM devolvió 9 requisitos: 2 CUMPLE y 7 NO_VERIFICABLE, con alcance parcial. La revisión visual de las páginas físicas 20 y 29 encontró omisiones y condiciones que necesitan mejor tratamiento. La versión 3 pide cada inciso de las listas, su etapa y condición de aplicación, y distingue obligaciones posteriores. Estas últimas validaciones pasaron pruebas simuladas; todavía no se midió su cobertura en otra consulta real. El informe original y los expedientes se conservan.
