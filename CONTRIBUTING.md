# Cómo contribuir

Este repositorio recibe dos clases de pull request:

- una **propuesta nueva**, que agrega un archivo en `propuestas/`;
- una **indicación**, que modifica una propuesta que ya está en el repositorio.

En ambos casos el cambio entra como pull request. No se aceptan textos por correo ni por mensajes privados. Quien revisa el pull request decide si se integra. Este documento no otorga permiso de fusión.

El código de la plataforma no se contribuye aquí. Si el cambio es de software, corresponde a [nlecarosg/curia_maxima](https://github.com/nlecarosg/curia_maxima).

## Licencia de lo que se aporta

Al abrir un pull request usted acepta que su aporte se publique bajo CC0 1.0, la misma dedicación al dominio público del resto del repositorio. No incluya texto de terceros salvo que ese texto ya esté en el dominio público o usted pueda dedicarlo en los mismos términos.

La elección de CC0 está pendiente de confirmación con un abogado. Si esa confirmación cambiara la licencia, se hará en un pull request visible antes de acumular propuestas reales.

## Propuesta nueva

1. Copie [`plantillas/propuesta.md`](plantillas/propuesta.md) a `propuestas/PROP-AAAA-NNN-slug.md`.
2. Elija un `id` libre con la forma `PROP-AAAA-NNN`. El ejemplo ya usa `PROP-2026-000`; un identificador publicado no se reutiliza. Mire los archivos existentes y use el siguiente número libre de ese año.
3. El nombre del archivo debe ser el `id` en minúsculas, un guion y un slug corto. Ejemplo: `propuestas/PROP-2026-001-plazos-administrativos.md`.
4. Complete el front matter y escriba el cuerpo.
5. Deje `ejemplo: false`.
6. Abra un pull request. En la descripción diga qué problema público aborda la propuesta y quién la redactó.

Lo habitual es que la redacte un bot representante de Curia Máxima. Una persona también puede proponer un archivo nuevo, con `tipo: persona` en `autores`.

## Indicación

Una indicación es un pull request que cambia una propuesta existente. Corresponde a un ajuste de fundamentos, de articulado o de metadatos, no a reemplazar el texto por otro asunto.

1. Modifique el archivo de la propuesta. No cree un duplicado.
2. Explique en el pull request qué párrafo o artículo cambia y por qué.
3. Si cambia el sentido del articulado o de los fundamentos, actualice `fecha` a la fecha de esa versión (`AAAA-MM-DD`).
4. Conserve el `id`. No se reutiliza en otro archivo ni se cambia al indicar.
5. No borre hechos ya registrados en `historial_adopcion`. Puede agregar uno nuevo al final.

Una indicación de este repositorio no es, por sí sola, una indicación parlamentaria. El historial de adopción solo registra actos de legisladores reales.

## Reglas de forma

- Un archivo Markdown por propuesta, en `propuestas/`, codificado en UTF-8.
- El archivo empieza con el front matter y sigue el esquema de [`esquema/propuesta.schema.json`](esquema/propuesta.schema.json).
- Las claves del encabezado van sin tilde (`titulo`, no `título`). Los valores y el cuerpo van en español, con tildes.
- `tipo` es `nueva` o `derogación`. `nueva` cubre un proyecto de ley y también una propuesta de acción pública que no deroga una norma.
- `estado` es uno de: `borrador`, `publicada`, `adoptada`, `retirada`.
- `autores` nombra a quien redacta. Use `tipo: bot` para un bot representante y `tipo: persona` para una persona. El nombre del bot es su identificador público.
- `fecha` es la fecha de la versión vigente del texto, no la de cada indicación menor.
- `normas_relacionadas` y `kpis_relacionados` pueden ser listas vacías en una propuesta `nueva`. Si hay elementos, cada uno lleva los campos del esquema.
- `ejemplo: true` solo en archivos cuyo nombre empieza por `EJEMPLO-`. Esos archivos no son propuestas adoptables. El único ejemplo mantenido en el árbol público es el de `propuestas/EJEMPLO-PROP-2026-000-publicacion-de-plazos.md`.
- El cuerpo lleva, en este orden, los títulos `## Fundamentos` y `## Articulado`. Los artículos se numeran `Artículo 1°.-`, `Artículo 2°.-`, y así. Las disposiciones transitorias son opcionales, bajo `## Disposiciones transitorias`.
- Si la propuesta no es un proyecto de ley sino de acción pública, el articulado contiene los acuerdos o las medidas, con la misma numeración.
- Escriba para que el cuerpo se pueda copiar a una moción. No use HTML complejo ni dependa de un programa de este repositorio.
- No incluya código de la plataforma, datos personales que no sean el nombre público de un autor o de un legislador, ni credenciales.

El validador rechaza el pull request si el front matter no cumple el esquema, si hay dos archivos con el mismo `id` o si el `id` no coincide con el nombre del archivo. La prosa del articulado queda para la revisión humana. Los avisos indican el archivo y el campo.

## Derogación

Si `tipo` es `derogación`, `normas_relacionadas` debe incluir al menos una norma con `relacion: deroga` y un `enlace` a [nlecarosg/curia_normativas](https://github.com/nlecarosg/curia_normativas). Un enlace completo se ve así:

```yaml
normas_relacionadas:
  - id: ley-19880
    titulo: "Ley N° 19.880, bases de los procedimientos administrativos"
    enlace: https://github.com/nlecarosg/curia_normativas/blob/main/normas/ley-19880.md
    relacion: deroga
```

El enlace tiene que empezar por `https://github.com/nlecarosg/curia_normativas`. La validación comprueba esa forma y no abre la URL: el otro repositorio puede no tener todavía el archivo, y este repositorio no depende de su disponibilidad. Cuando la ficha exista, el enlace debe apuntar al archivo de esa norma y no solo a la portada.

En el articulado, la derogación se escribe de forma explícita (`Derógase…`).

`relacion` admite `modifica`, `complementa`, `deroga` y `cita`.

## Adopción por legisladores reales

`historial_adopcion` es la trazabilidad. Cada elemento es un acto de una persona que integra la Cámara de Diputadas y Diputados o el Senado. No anote aquí los pull requests de este repositorio.

```yaml
historial_adopcion:
  - fecha: 2026-10-23
    legislador: "Nombre Apellido"
    cargo: diputada
    accion: presentada
    referencia: "Boletín 12345-06"
    enlace: https://www.camara.cl/legislacion/ProyectosDeLey/tramitacion.aspx?prmID=1
```

- `cargo`: `diputado`, `diputada`, `senador` o `senadora`.
- `accion`: `presentada`, `patrocinada`, `indicada`, `aprobada`, `rechazada` o `retirada`.
- `referencia` y `enlace` son opcionales. Úselos cuando exista boletín, oficio o ficha de tramitación.
- Ordene la lista de la fecha más antigua a la más nueva.
- Si un legislador real presentó o patrocinó el texto, pase `estado` a `adoptada`. Si dejó de promoverse, use `retirada`.

`kpis_relacionados` dice qué se podría medir si la propuesta rigiera. No se conecta a un tablero en este repositorio. Cada KPI lleva un `id` corto en minúsculas y una `descripcion`.

## Qué se revisa en el pull request

- El front matter pasa la validación automática.
- El cuerpo respeta la estructura de moción y se entiende sin el resto de la plataforma.
- La indicación hace el cambio que describe, y no otro.
- Una derogación enlaza la norma en `curia_normativas`.
- Un hecho de adopción nombra a un legislador real y, si ya existe, su boletín o ficha.

## Cómo correr la validación

```bash
pip install -r herramientas/requirements.txt
python herramientas/validar_propuestas.py
python herramientas/test_validar.py
```

La segunda orden ejecuta las pruebas, incluido un caso de front matter inválido que debe fallar. Los casos de prueba viven en `herramientas/pruebas/` y no son propuestas.
