# Consulta local del RUC — etapa 2

El flujo **PYMES 02 - Consultar RUC en padrón SUNAT** ya está importado en este equipo:
http://127.0.0.1:5680/workflow/pymesSunatRuc02

## Funcionamiento

Formulario → validación de 11 dígitos → consulta HTTP al servicio local → lectura SQLite → explicación con fuente y fecha.

El padrón se obtiene de https://www.sunat.gob.pe/descargaPRR/mrc137_padron_reducido.html .
No usa claves SOL, claves API ni modelos de IA. No realiza scraping de la consulta con CAPTCHA.
La validación inicial es de formato, no de dígito verificador.
El padrón es una copia: no verifica el estado en tiempo real, representación legal ni RNP.
Una ausencia solo significa que el RUC no aparece en esta copia.
Las consultas fallidas y la ausencia del padrón se muestran por separado.

## Probar

1. Abrir el flujo 02 y pulsar Execute.
2. Enviar un RUC conocido y contrastar nombre, estado, condición y fecha con SUNAT.
3. Enviar 123: debe pedir corregir el formato.
4. Enviar 00000000000: debe indicar que no aparece en la copia.
5. Si pymes-sunat está detenido, debe indicar que no pudo consultar.

## Instalación actual sin Compose

Este equipo tiene los contenedores pymes-n8n y pymes-sunat.
Se conectan por la red pymes-red. El servicio del padrón no publica puertos al exterior.
Datos persistentes: pymes-agentes_n8n_data y pymes-sunat-data.
Después de iniciar la máquina Podman, iniciar ambos contenedores desde Podman Desktop.
No crear otro entorno Compose sobre el mismo puerto mientras estos estén funcionando.

## Compartir con el equipo

compose.yaml incluye ambos servicios para un entorno NUEVO, con proveedor Compose instalado.
Ejecutar podman compose up -d --build, crear el usuario de n8n e importar workflows/02-consultar-ruc-sunat.json.
Luego cargar el padrón; antes de cargarlo, las consultas informan fuente no disponible.
El ZIP compartible excluye la base, el padrón y los datos de usuarios.

## Actualización del padrón (manual, aún no programada)

Descargar el ZIP desde el enlace oficial y anotar la fecha que muestra SUNAT.
Copiarlo al contenedor del servicio como /data/padron.zip.
Ejecutar dentro de ese contenedor:
python /app/import_padron.py /data/padron.zip /data/padron.sqlite --fecha AAAA-MM-DD

En la instalación actual, por ejemplo:
podman cp RUTA_AL_ZIP pymes-sunat:/data/padron.zip
podman exec pymes-sunat python /app/import_padron.py /data/padron.zip /data/padron.sqlite --fecha FECHA_PUBLICADA

En Compose usar podman compose cp y podman compose exec con el servicio pymes-sunat.
La fecha debe ser la publicada para ese archivo, no simplemente la fecha de descarga.
La importación valida columnas, rechaza un padrón vacío y conserva el anterior ante errores.
Excluye y contabiliza filas cuyo RUC/formato sea inválido; aborta si hay más de 100.
SQLite reemplaza la copia anterior solamente después de terminar la validación.

## Alcance de esta etapa

No decide la aptitud para concursar ni demuestra corrupción.
No hay actualización diaria automática ni despliegue público.
Los cuatro agentes y la web de clientes corresponden a etapas posteriores.


## Validacion realizada el 23/10/2026

Padron: 18.483.783 filas de datos; 18.483.782 registros cargados y una fila excluida por formato invalido.
Pruebas del formulario completo: formato incorrecto, fuente aun no cargada, RUC encontrado (20131312955, SUNAT) y no encontrado (00000000000). Se comprobaron nombre, ACTIVO, HABIDO y fecha del padron en la respuesta final.
El formulario local esta publicado en http://127.0.0.1:5680/form/pymes-consulta-padron-sunat . Publicarlo aqui no lo expone a internet.
