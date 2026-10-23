#!/usr/bin/env python3
"""Valida el front matter de las propuestas.

Revisa el encabezado YAML contra esquema/propuesta.schema.json, exige un
id único y lo hace coincidir con el nombre del archivo. No lee el cuerpo
ni abre los enlaces.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator, FormatChecker
from jsonschema.exceptions import SchemaError, ValidationError

RAIZ_REPOSITORIO = Path(__file__).resolve().parents[1]
ESQUEMA_RELATIVO = Path("esquema") / "propuesta.schema.json"
CARPETA_PROPUESTAS = "propuestas"

_FRENTE = re.compile(r"\A---[ \t]*\r?\n(.*?)\r?\n---[ \t]*(?:\r?\n|\Z)", re.DOTALL)
_NOMBRE = re.compile(
    r"^(EJEMPLO-)?(PROP-\d{4}-\d{3,})-([a-z0-9]+(?:-[a-z0-9]+)*)\.md$"
)
_CAMPO_EXTRA = re.compile(r"\((.+) (?:was|were) unexpected\)")


class Cargador(yaml.SafeLoader):
    """SafeLoader que conserva las fechas como texto y rechaza claves repetidas."""


def _mapa_sin_claves_repetidas(loader: yaml.SafeLoader, node: yaml.Node, deep: bool = False):
    mapa: dict[object, object] = {}
    for clave_nodo, valor_nodo in node.value:
        clave = loader.construct_object(clave_nodo, deep=deep)
        if clave in mapa:
            raise yaml.constructor.ConstructorError(
                "al leer el front matter",
                node.start_mark,
                f"clave duplicada: {clave}",
                clave_nodo.start_mark,
            )
        mapa[clave] = loader.construct_object(valor_nodo, deep=deep)
    return mapa


Cargador.add_constructor(
    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
    _mapa_sin_claves_repetidas,
)
# PyYAML convertiría 2026-10-23 en datetime.date. El esquema exige texto AAAA-MM-DD.
Cargador.yaml_implicit_resolvers = {
    caracter: [regla for regla in reglas if regla[0] != "tag:yaml.org,2002:timestamp"]
    for caracter, reglas in yaml.SafeLoader.yaml_implicit_resolvers.items()
}


def extraer_front_matter(texto: str) -> dict[str, object]:
    coincidencia = _FRENTE.match(texto.lstrip("\ufeff"))
    if not coincidencia:
        raise ValueError(
            "el archivo debe empezar con un front matter YAML cerrado por una línea ---"
        )
    try:
        datos = yaml.load(coincidencia.group(1), Loader=Cargador)
    except yaml.YAMLError as exc:
        raise ValueError(f"el front matter no es YAML válido ({exc})") from exc
    if not isinstance(datos, dict):
        raise ValueError("el front matter debe ser un conjunto de campos, no una lista ni un valor suelto")
    return datos


def _camino(error: ValidationError) -> str:
    if not error.absolute_path:
        return "encabezado"
    return ".".join(str(parte) for parte in error.absolute_path)


def _resumir(valor: object) -> str:
    texto = repr(valor)
    if len(texto) > 80:
        return texto[:77] + "..."
    return texto


def _mensaje_esquema(error: ValidationError) -> str:
    camino = _camino(error)
    regla = error.validator

    if regla == "required":
        encontrado = re.search(r"'([^']+)'", error.message)
        campo = encontrado.group(1) if encontrado else error.message
        return f"{camino}: falta el campo {campo}"
    if regla == "additionalProperties":
        encontrado = _CAMPO_EXTRA.search(error.message)
        extra = encontrado.group(1) if encontrado else error.message
        return f"{camino}: hay campos que el esquema no admite ({extra})"
    if regla == "enum":
        permitidos = ", ".join(repr(item) for item in error.validator_value)
        return f"{camino}: el valor {_resumir(error.instance)} no está permitido. Use uno de: {permitidos}"
    if regla == "type":
        esperado = error.validator_value
        if isinstance(esperado, list):
            esperado = " o ".join(esperado)
        return f"{camino}: se esperaba {esperado} y llegó {_resumir(error.instance)}"
    if regla == "format" and error.validator_value == "date":
        return f"{camino}: {_resumir(error.instance)} no es una fecha AAAA-MM-DD"
    if regla == "format" and error.validator_value == "uri":
        return f"{camino}: {_resumir(error.instance)} no es una URL"
    if regla == "minLength":
        return f"{camino}: el texto es demasiado corto (mínimo {error.validator_value} caracteres)"
    if regla == "maxLength":
        return f"{camino}: el texto es demasiado largo (máximo {error.validator_value} caracteres)"
    if regla == "minItems":
        cantidad = error.validator_value
        unidad = "elemento" if cantidad == 1 else "elementos"
        return f"{camino}: debe incluir al menos {cantidad} {unidad}"
    if regla == "pattern" and camino == "id":
        return f"{camino}: el id debe tener la forma PROP-AAAA-NNN"
    if regla == "pattern" and camino.endswith("enlace"):
        return f"{camino}: el enlace debe ser una URL https con dominio"
    if regla == "pattern":
        return f"{camino}: el valor {_resumir(error.instance)} no tiene la forma exigida"
    if regla == "contains":
        return (
            f"{camino}: una derogación debe incluir al menos una norma con "
            "relacion deroga y enlace https://github.com/nlecarosg/curia_normativas"
        )
    if regla == "const":
        return f"{camino}: se esperaba {_resumir(error.validator_value)}"
    return f"{camino}: {error.message}"


def cargar_validador(raiz: Path) -> Draft202012Validator:
    ruta = raiz / ESQUEMA_RELATIVO
    if not ruta.is_file():
        raise FileNotFoundError(f"No está el esquema {ESQUEMA_RELATIVO.as_posix()}")
    esquema = json.loads(ruta.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(esquema)
    return Draft202012Validator(esquema, format_checker=FormatChecker())


def validar_datos(datos: dict[str, object], validador: Draft202012Validator) -> list[str]:
    errores = sorted(
        validador.iter_errors(datos),
        key=lambda error: [str(parte) for parte in error.absolute_path],
    )
    return [_mensaje_esquema(error) for error in errores]


def validar_directorio(raiz: Path) -> list[str]:
    try:
        validador = cargar_validador(raiz)
    except (OSError, json.JSONDecodeError, SchemaError) as exc:
        return [f"No se pudo cargar el esquema: {exc}"]

    carpeta = raiz / CARPETA_PROPUESTAS
    if not carpeta.is_dir():
        return [f"No existe la carpeta {CARPETA_PROPUESTAS}/"]

    errores: list[str] = []
    ids_vistos: dict[str, str] = {}
    archivos = sorted(ruta for ruta in carpeta.rglob("*") if ruta.is_file())

    for ruta in archivos:
        visible = ruta.relative_to(raiz).as_posix()
        if ruta.suffix != ".md":
            errores.append(f"{visible}: en {CARPETA_PROPUESTAS}/ solo hay propuestas Markdown")
            continue
        try:
            datos = extraer_front_matter(ruta.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, ValueError) as exc:
            errores.append(f"{visible}: {exc}")
            continue

        coincidencia = _NOMBRE.match(ruta.name)
        if not coincidencia:
            errores.append(
                f"{visible}: el nombre debe ser PROP-AAAA-NNN-slug.md "
                "o EJEMPLO-PROP-AAAA-NNN-slug.md, en minúsculas"
            )
        else:
            identificador = coincidencia.group(2)
            es_ejemplo = coincidencia.group(1) is not None
            if datos.get("id") != identificador:
                errores.append(
                    f"{visible}: el id {datos.get('id')!r} no coincide con {identificador} del nombre"
                )
            if datos.get("ejemplo") is True and not es_ejemplo:
                errores.append(f"{visible}: ejemplo true exige el prefijo EJEMPLO- en el nombre")
            if es_ejemplo and datos.get("ejemplo") is not True:
                errores.append(f"{visible}: el prefijo EJEMPLO- exige ejemplo: true")

        identificador = datos.get("id")
        if isinstance(identificador, str):
            previo = ids_vistos.get(identificador)
            if previo:
                errores.append(f"{visible}: el id {identificador} ya está usado en {previo}")
            else:
                ids_vistos[identificador] = visible

        for mensaje in validar_datos(datos, validador):
            errores.append(f"{visible}: {mensaje}")

    return errores


def main(argumentos: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Valida el front matter de las propuestas en Markdown."
    )
    parser.add_argument(
        "--raiz",
        type=Path,
        default=RAIZ_REPOSITORIO,
        help="Directorio del repositorio. Por defecto, la raíz de este repo.",
    )
    args = parser.parse_args(argumentos)
    raiz = args.raiz.resolve()
    errores = validar_directorio(raiz)
    if errores:
        for error in errores:
            print(error, file=sys.stderr)
        cantidad = len(errores)
        palabra = "error" if cantidad == 1 else "errores"
        print(f"{cantidad} {palabra} de front matter.", file=sys.stderr)
        return 1

    carpeta = raiz / CARPETA_PROPUESTAS
    cantidad = len([ruta for ruta in carpeta.rglob("*.md") if ruta.is_file()]) if carpeta.is_dir() else 0
    if cantidad == 1:
        print("Front matter válido en 1 propuesta.")
    else:
        print(f"Front matter válido en {cantidad} propuestas.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
