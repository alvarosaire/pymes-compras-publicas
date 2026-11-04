# FASE 1: radar inicial de convocatorias

Diagrama completo: http://127.0.0.1:5680/workflow/pymesPerfil03
Registrar perfil y buscar: http://127.0.0.1:5680/form/pymes-perfil-empresa
Repetir solo la búsqueda: http://127.0.0.1:5680/form/pymes-buscar-oportunidades
Editor del buscador independiente: http://127.0.0.1:5680/workflow/pymesRadar04

Las notas del diagrama contienen únicamente FASE 0, FASE 1, FASE 2, FASE 3 y FASE 4.
Las fases 0 y 1 tienen ejecución real. Las fases 2 a 4 aún son espacios reservados.

## Qué hace
1. Recupera el perfil persistente por RUC.
2. Consulta el módulo público oficial de oportunidades del SEACE.
3. Busca coincidencias de palabras en descripción e ítems, normalizando tildes y algunos plurales.
4. Excluye registros cuyo plazo publicado de inscripción terminó.
5. Revisa hasta 20 fichas candidatas y contrasta la región de los ítems, no la sede de la entidad.
6. Muestra hasta 10 resultados con motivos, plazos, montos publicados, ficha oficial y enlaces a bases.
7. Guarda el último resumen en la tabla busquedas de perfiles.sqlite.

## Fuente
Servicio oficial descriptivo: https://www.gob.pe/703
Módulo: https://prod4.seace.gob.pe/openegocio/
La conexión utiliza las consultas públicas que usa ese módulo, sin claves ni sesión del proveedor.
Es una integración al servicio del portal; no se presupone un contrato de API estable. Un cambio del portal podría exigir adaptar el conector.
Cache de respuestas: 3 minutos. Se muestra la fecha de consulta de la fuente.
No abarca todos los canales de contratación (por ejemplo, catálogos electrónicos y otros módulos).
No se realizan inscripciones, cotizaciones ni envíos a entidades.

## Límites visibles
La coincidencia es léxica, no una evaluación de requisitos ni una probabilidad de ganar.
Si no se reconoce la región del perfil se informa y no se excluyen resultados por región.
Si una ficha no responde o carece de región, el resultado queda por verificar.
Si hay más de 20 candidatos o falla alguna ficha, la búsqueda se marca parcial.
El plazo usado es el de registro de participantes; presentación de ofertas se muestra aparte.
Cero coincidencias no significa ausencia de oportunidades en todo el Estado.
Una fuente caída se diferencia de una búsqueda sin coincidencias.
Las bases se enlazan: todavía no se descarga ni analiza su contenido con IA.
Esta fase no requiere instalar un chat en CMD ni configurar un modelo de IA.

## Pruebas realizadas
Normalización singular/plural, duplicados, plazo vencido, región del ítem y error de fuente.
Prueba real completa: perfil temporal de muebles a nivel nacional, seis coincidencias en la consulta del 23/10/2026, fichas y enlaces a bases.
Prueba de búsqueda sin perfil: aviso para completar fase 0.
Prueba de búsqueda independiente por RUC: utiliza el perfil guardado.
El perfil y su resumen de prueba se eliminaron de la base de perfiles; las ejecuciones de prueba pueden aparecer en el historial de n8n.

## Compartir
Importar los workflows 03 y 04 incluidos. Reconstruir el servicio pymes-sunat con el Containerfile actualizado, que incluye opportunities.py.
El paquete no contiene usuarios, perfiles, claves ni bases SQLite.

