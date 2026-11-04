# Perfil y diagrama por fases

Editor: http://127.0.0.1:5680/workflow/pymesPerfil03
Formulario: http://127.0.0.1:5680/form/pymes-perfil-empresa

## Implementado
Fase 0: consulta del RUC y registro de perfil. Productos/servicios, regiones y experiencia se declaran en el formulario. Se guardan junto con una copia de los datos consultados y su fecha en /data/perfiles.sqlite, dentro del volumen persistente del servicio pymes-sunat. El padrón permanece en un archivo separado; actualizarlo no borra los perfiles.

El mismo RUC actualiza su perfil. Este es un prototipo local de un solo equipo: no acredita identidad ni representación. Antes de publicarlo para varias empresas, incorporar cuentas, autorización por empresa y consentimiento. No está expuesto a internet.

## Notas en el diagrama
- Fase 0: perfil — implementada.
- Fase 1: búsqueda inicial conectada al módulo oficial SEACE. Ver FASE_1.md.
- Fase 2: evaluar requisitos y documentos — pendiente.
- Fase 3: mejorar propuesta — pendiente.
- Fase 4: revisar restricciones — pendiente; revisión transversal desde fase 1.

El diagrama muestra solo títulos por fase. Las fases 0 y 1 tienen nodos funcionales; las fases 2 a 4 siguen pendientes. El RNP queda pendiente de verificación; un perfil guardado no certifica aptitud para contratar.

## Prueba y uso
1. Abrir el formulario.
2. Escribir RUC, productos/servicios, regiones y experiencia real; si no hay experiencia, escribir Sin experiencia.
3. Enviar. Si el RUC no aparece o el servicio falla, no se guarda un perfil nuevo.
4. Un envío correcto muestra Perfil guardado y resume los datos.
5. Para modificar los datos, volver a enviar el formulario con el mismo RUC.

## Validación
Se probaron formato incorrecto, campos vacíos, RUC ausente, guardado y actualización sin duplicado. También se probó el formulario n8n completo con un registro técnico temporal y se retiró ese registro, dejando la tabla lista para el usuario.

## Portabilidad
Importar workflows/03-perfil-empresa-fases.json en el n8n del compañero y reconstruir el servicio con la versión actual de sunat/service.py. Los datos de perfiles no se incluyen en el ZIP compartible.


