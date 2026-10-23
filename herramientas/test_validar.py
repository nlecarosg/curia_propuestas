#!/usr/bin/env python3
"""Pruebas del validador de front matter.

El árbol público debe pasar. Un caso inválido, guardado fuera de
propuestas/, debe hacer fallar el validador.
"""

from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
import unittest
from contextlib import contextmanager
from pathlib import Path

CARPETA = Path(__file__).resolve().parent
RAIZ = CARPETA.parents[0]
SCRIPT = CARPETA / "validar_propuestas.py"
PRUEBAS = CARPETA / "pruebas"

sys.path.insert(0, str(CARPETA))
import validar_propuestas as validador  # noqa: E402


def ejecutar(raiz: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), "--raiz", str(raiz)],
        check=False,
        capture_output=True,
        text=True,
    )


@contextmanager
def repositorio_temporal(archivos: dict[str, Path | str]):
    with tempfile.TemporaryDirectory() as carpeta:
        raiz = Path(carpeta)
        (raiz / "esquema").mkdir()
        shutil.copy(RAIZ / "esquema" / "propuesta.schema.json", raiz / "esquema" / "propuesta.schema.json")
        (raiz / "propuestas").mkdir()
        for nombre, origen in archivos.items():
            destino = raiz / "propuestas" / nombre
            if isinstance(origen, Path):
                shutil.copy(origen, destino)
            else:
                destino.write_text(origen, encoding="utf-8")
        yield raiz


class ValidacionPublica(unittest.TestCase):
    def test_el_ejemplo_pasa_en_el_repositorio(self) -> None:
        resultado = ejecutar(RAIZ)
        self.assertEqual(resultado.returncode, 0, resultado.stderr)
        self.assertIn("Front matter válido en 1 propuesta.", resultado.stdout)

    def test_el_ejemplo_esta_marcado(self) -> None:
        archivos = sorted((RAIZ / "propuestas").glob("EJEMPLO-*.md"))
        self.assertEqual([ruta.name for ruta in archivos], ["EJEMPLO-PROP-2026-000-publicacion-de-plazos.md"])
        texto = archivos[0].read_text(encoding="utf-8")
        self.assertIn("**EJEMPLO.**", texto)
        datos = validador.extraer_front_matter(texto)
        self.assertIs(datos["ejemplo"], True)
        self.assertEqual(datos["id"], "PROP-2026-000")
        self.assertIsInstance(datos["fecha"], str)

    def test_el_caso_invalido_falla(self) -> None:
        with repositorio_temporal(
            {"PROP-2026-999-front-matter-invalido.md": PRUEBAS / "front-matter-invalido.md"}
        ) as raiz:
            resultado = ejecutar(raiz)
        self.assertEqual(resultado.returncode, 1, resultado.stdout)
        self.assertIn("PROP-2026-999", resultado.stderr)
        self.assertIn("no está permitido", resultado.stderr)
        self.assertIn("no es una fecha AAAA-MM-DD", resultado.stderr)
        self.assertIn("debe incluir al menos 1 elemento", resultado.stderr)
        self.assertIn("no admite", resultado.stderr)

    def test_derogacion_sin_repositorio_de_normativas_falla(self) -> None:
        with repositorio_temporal(
            {"PROP-2026-998-derogacion-sin-repositorio.md": PRUEBAS / "derogacion-sin-repositorio.md"}
        ) as raiz:
            resultado = ejecutar(raiz)
        self.assertEqual(resultado.returncode, 1, resultado.stdout)
        self.assertIn("curia_normativas", resultado.stderr)

    def test_derogacion_enlazada_pasa(self) -> None:
        with repositorio_temporal(
            {"PROP-2026-997-derogacion-valida.md": PRUEBAS / "derogacion-valida.md"}
        ) as raiz:
            resultado = ejecutar(raiz)
        self.assertEqual(resultado.returncode, 0, resultado.stderr)

    def test_el_cuerpo_no_se_valida(self) -> None:
        texto = (PRUEBAS / "derogacion-valida.md").read_text(encoding="utf-8")
        cierre = texto.find("\n---\n")
        self.assertGreater(cierre, 0)
        mutilado = texto[: cierre + len("\n---\n")] + "esto no es una moción\n"
        with repositorio_temporal({"PROP-2026-997-derogacion-valida.md": mutilado}) as raiz:
            resultado = ejecutar(raiz)
        self.assertEqual(resultado.returncode, 0, resultado.stderr)

    def test_id_repetido_falla(self) -> None:
        base = (PRUEBAS / "derogacion-valida.md").read_text(encoding="utf-8")
        with repositorio_temporal(
            {
                "PROP-2026-997-una.md": base,
                "PROP-2026-997-otra.md": base,
            }
        ) as raiz:
            resultado = ejecutar(raiz)
        self.assertEqual(resultado.returncode, 1, resultado.stdout)
        self.assertIn("ya está usado", resultado.stderr)

    def test_enlace_sin_dominio_falla(self) -> None:
        texto = (PRUEBAS / "derogacion-valida.md").read_text(encoding="utf-8")
        roto = texto.replace(
            "https://github.com/nlecarosg/curia_normativas/blob/main/normas/ley-99999.md",
            "https://",
        )
        with repositorio_temporal({"PROP-2026-997-derogacion-valida.md": roto}) as raiz:
            resultado = ejecutar(raiz)
        self.assertEqual(resultado.returncode, 1, resultado.stdout)
        self.assertIn("URL https con dominio", resultado.stderr)

    def test_id_distinto_del_nombre_falla(self) -> None:
        with repositorio_temporal(
            {"PROP-2026-996-nombre-distinto.md": PRUEBAS / "derogacion-valida.md"}
        ) as raiz:
            resultado = ejecutar(raiz)
        self.assertEqual(resultado.returncode, 1, resultado.stdout)
        self.assertIn("no coincide", resultado.stderr)


if __name__ == "__main__":
    unittest.main()
