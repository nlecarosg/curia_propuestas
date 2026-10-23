# Curia Propuestas

Repositorio público de propuestas de ley y de acción pública de [Curia Máxima](https://github.com/nlecarosg/curia_maxima). Cada propuesta es un archivo Markdown. El texto se publica con [CC0 1.0](LICENSE) para que cualquiera pueda copiarlo, modificarlo y presentarlo sin pedir permiso. El uso previsto es que un legislador o una legisladora pueda llevar el texto a una moción parlamentaria.

SPDX-License-Identifier: CC0-1.0

## Independencia

Este repositorio guarda el contenido público: las propuestas, su plantilla, el esquema del encabezado y la validación de ese encabezado.

- El código de Curia Máxima vive en [nlecarosg/curia_maxima](https://github.com/nlecarosg/curia_maxima). Este repositorio no lo aloja.
- Las normas vigentes viven en [nlecarosg/curia_normativas](https://github.com/nlecarosg/curia_normativas). Una propuesta de derogación enlaza ahí la norma que propone eliminar.

Deje fuera de este repositorio las aplicaciones, las bases de datos, las credenciales y los flujos de despliegue.

## Cómo se usa una propuesta

Cada archivo de [`propuestas/`](propuestas/) es una propuesta.

1. El front matter (el bloque YAML entre líneas `---`) dice qué es: identificador, título, tipo (`nueva` o `derogación`), estado, autores, fecha, normas relacionadas, KPI relacionados e historial de adopción.
2. El cuerpo está escrito como moción: fundamentos y articulado. Ese cuerpo es la exportación. Se copia a la moción; este repositorio no incluye un programa exportador.
3. Los cambios al texto entran como pull requests. En la guía de contribución se llaman indicaciones.
4. Cuando un legislador real presenta, patrocina, indica, aprueba, rechaza o retira el texto en el Congreso, el hecho se anota en `historial_adopcion` mediante otro pull request.

El archivo [`propuestas/EJEMPLO-PROP-2026-000-publicacion-de-plazos.md`](propuestas/EJEMPLO-PROP-2026-000-publicacion-de-plazos.md) muestra el formato. Está marcado como ejemplo. No es una propuesta real y no debe presentarse como moción.

## Licencia

Los textos de este repositorio se ofrecen bajo CC0 1.0 Universal (dominio público). El archivo [`LICENSE`](LICENSE) reproduce el texto canónico en inglés, que es la versión jurídica oficial y la que identifica GitHub. La traducción oficial al español está en <https://creativecommons.org/publicdomain/zero/1.0/legalcode.es>.

La elección de CC0 queda pendiente de confirmación con un abogado. Mientras tanto, el texto de la licencia ya está en el repositorio para que la dedicación al dominio público sea explícita.

## Contribuir

La forma de proponer, de indicar cambios y las reglas de forma están en [`CONTRIBUTING.md`](CONTRIBUTING.md). La plantilla vacía está en [`plantillas/propuesta.md`](plantillas/propuesta.md).

## Validación

En cada pull request, GitHub Actions ejecuta [`herramientas/validar_propuestas.py`](herramientas/validar_propuestas.py). Comprueba el front matter contra [`esquema/propuesta.schema.json`](esquema/propuesta.schema.json), que el identificador sea único y que coincida con el nombre del archivo. No revisa la redacción del articulado ni abre las URLs.

Para correrla en local:

```bash
pip install -r herramientas/requirements.txt
python herramientas/validar_propuestas.py
python herramientas/test_validar.py
```

## Mapa

```text
propuestas/                 textos publicables, incluido el ejemplo
plantillas/propuesta.md     plantilla vacía
esquema/propuesta.schema.json
herramientas/               validador, pruebas y caso inválido
.github/workflows/          validación del front matter en cada pull request
```
