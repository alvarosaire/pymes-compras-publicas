# Próximas fases del proyecto

## Qué construimos primero

Una demostración con unas bases de prueba y el perfil de una empresa ficticia. El primer agente funcional será el evaluador de requisitos. Después se conectarán fuentes oficiales y los demás agentes. No se necesita cargar documentos privados para aprender el recorrido.

## Flujo objetivo

Perfil y documentos → convocatoria seleccionada → expediente → evaluación de requisitos y alertas → revisión de propuesta → informe para decisión humana.

| Función | Entradas | Herramientas que debemos preparar | Resultado |
| --- | --- | --- | --- |
| Agente 1 Oportunidades | Perfil y convocatorias disponibles | Búsqueda habilitada y lectura de bases | Compatibilidad y resumen con fuentes |
| Agente 2 Requisitos | Requisitos y documentos de empresa | Recuperación de evidencias en el expediente | Cumple, no cumple o no verificable |
| Agente 3 Propuesta | Oferta, matriz de requisitos y criterios publicados | Consulta de criterios y cálculos deterministas | Mejoras y simulación de puntaje |
| Agente 4 Alertas | Bases, contexto y normativa aplicable | Búsqueda normativa con versión y citas | Posibles restricciones e inconsistencias |

Cada agente requiere instrucciones, modelo de IA y herramientas. Un coordinador convencional organiza las llamadas. La revisión normativa comienza al leer las bases; no se espera hasta la adjudicación. No se garantizan victorias ni se considera que una alerta pruebe corrupción.

## Entregas

1. Entorno reproducible con Podman y prueba del formulario.
2. Demostración pequeña del agente de requisitos, con modelo y credenciales elegidos por el usuario.
3. Base documental, citas verificables y matriz persistente por expediente.
4. Búsqueda de oportunidades, revisión normativa y propuesta.
5. Interfaz web y seguimiento de cambios.

El código de la aplicación puede conservar FastAPI y la estructura del proyecto de la hackathon. n8n coordinaría las tareas y llamaría las herramientas del servidor. Antes de conectar un servicio externo hay que confirmar acceso, condiciones, datos disponibles y costos.
