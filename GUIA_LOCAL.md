# Entorno n8n para el equipo PYMES

Este paquete describe un entorno local de n8n para ejecutar con Podman. Comparte la configuración y los flujos; cada compañero conserva su propio usuario, contraseñas y datos. No es todavía una aplicación pública ni un espacio de edición simultánea para todo el equipo.

## Contenido y estado

- `compose.yaml`: imagen oficial n8n 2.44.6, puerto local 5680 y almacenamiento persistente.
- `workflows/01-recibir-ruc.json`: formulario, validación de 11 dígitos y resultado. La consulta SUNAT no está conectada.
- `PLAN_AGENTES.md`: funciones y dependencias de los cuatro agentes que construiremos después.
- `.env.example`: ejemplo opcional para cambiar el puerto.

Podman ya está instalado y n8n funciona en el puerto 5680. Esta máquina usa contenedores iniciados directamente, sin Compose. Para la consulta oficial del RUC y los pasos de actualización, leer CONSULTA_RUC.md. Compose permite reproducir el entorno en otro equipo; no iniciarlo en paralelo sobre el mismo puerto.

## 1 Instalar Podman

En Windows, instalar Podman Desktop siguiendo https://podman-desktop.io/docs/installation/windows-install . Completar el inicio de Podman y configurar un proveedor de Compose desde las opciones de instalación de Podman Desktop. `podman compose` necesita un proveedor externo como podman-compose o Docker Compose; instalar Podman por sí solo no garantiza que Compose esté disponible.

Comprobar desde una nueva terminal:

```text
podman --version
podman machine list
podman info
podman compose version
```

En Windows, si no existe ninguna máquina, ejecutar `podman machine init` y después `podman machine start`. Si ya existe, iniciar esa máquina cuando esté detenida. En Linux, normalmente no se necesita una máquina virtual.

## 2 Iniciar el entorno

Descomprimir el ZIP. Abrir una terminal dentro de la carpeta que contiene `compose.yaml` y ejecutar:

```text
podman compose up -d
podman compose logs -f n8n
```

Esperar el mensaje de que el editor está disponible. Abrir **http://localhost:5680** en el navegador. Para salir de la vista de registros usar Ctrl+C; el contenedor continuará ejecutándose en segundo plano.

Crear el usuario propietario local. Es una instancia nueva: no copia automáticamente tu cuenta ni los flujos del n8n que usabas en el puerto 5678. La configuración usa el puerto 5680 para poder mantener ambos entornos durante la prueba.

## 3 Importar y probar el flujo

1. En Overview crear un workflow.
2. Usar Import from File y elegir `workflows/01-recibir-ruc.json`.
3. Guardar y ejecutar el flujo en modo de prueba.
4. Enviar `123`: debe solicitar corregir el formato.
5. Repetir con `12345678901`: debe indicar verificación oficial pendiente. Este número es solo una entrada de prueba, no una empresa validada.

El resultado nunca debe afirmar que el RUC existe o que está activo/habido: todavía falta conectar la fuente oficial. La prueba no usa IA, claves API ni datos privados.

## 4 Detener y volver a abrir

```text
podman compose stop
podman compose start
```

Los datos y la clave de cifrado generada por n8n se conservan en el volumen `n8n_data`. No borrar ese volumen si se quieren conservar usuarios, flujos y credenciales. Para comprobar la persistencia, guardar un flujo, detener e iniciar y verificar que siga en Overview.

## Cómo colaborar

Compartir este paquete o subir su contenido a un repositorio del equipo. Después de editar un flujo, exportarlo desde n8n, revisar que no incluya datos privados o ejemplos sensibles y actualizar el JSON de `workflows/`. Cada persona importa la nueva versión y configura sus propias credenciales. Evitar que varias personas editen el mismo JSON a la vez sin coordinarse.

No copiar la base local ni las credenciales del propietario al repositorio. Guardar las claves de los modelos en Credentials dentro de cada instancia de n8n. El archivo `.gitignore` ayuda a excluir datos locales, pero no sustituye la revisión de los archivos a compartir.

## Alcance del contenedor

Para esta prueba no hace falta un Containerfile propio: utilizamos la imagen oficial ya construida. El contenedor agrupa n8n y sus dependencias; el archivo Compose define cómo iniciarlo. Todavía no incluye una web para clientes, el padrón SUNAT ni cuatro agentes conectados a modelos.

Más adelante podremos añadir un servicio para nuestra aplicación Python, una base de datos empresarial y almacenamiento de documentos. La base interna de n8n guarda su configuración y ejecuciones; no debe confundirse con el padrón de empresas.

Los nodos AI Agent no requieren habilitar el producto n8n Assistant. El paquete no configura la infraestructura adicional del Assistant. Esta configuración es para desarrollo local, no despliegue público.

## Si no abre

- `podman info` debe responder y la máquina debe estar iniciada en Windows.
- Si Compose no aparece, completar la instalación de su proveedor.
- Consultar `podman compose ps` y `podman compose logs --tail 100 n8n`.
- Si el puerto 5680 está ocupado, copiar `.env.example` a `.env`, cambiar el puerto y repetir `podman compose up -d`.
- No ejecutar de nuevo el instalador npm: esta modalidad descarga una imagen de contenedor.

## Fuentes

- https://podman.io/docs/installation
- https://docs.podman.io/en/latest/markdown/podman-compose.1.html
- https://docs.n8n.io/hosting/installation/docker/


## Fases disponibles
El flujo workflows/03-perfil-empresa-fases.json contiene el perfil (FASE 0), la búsqueda (FASE 1), la recepción de documentos (FASE 2) y la recepción de propuestas vinculadas (FASE 3). Ver FASE_2.md y FASE_3.md. El análisis con IA está pendiente. FASE 4 registra solicitudes de revisión de las bases existentes; ver FASE_4.md. No realiza análisis jurídico automático.



## Conectar Gemini
El flujo adicional workflows/05-analizar-gemini.json prepara el análisis de requisitos. Sigue GEMINI_FASE_2.md para configurar tu propia credencial. No se incluyen claves. La conexión real aún debe probarse con la clave del usuario.

