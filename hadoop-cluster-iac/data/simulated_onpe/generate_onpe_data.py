import csv
import random
from pathlib import Path
from typing import Dict, List, Tuple


OUTPUT_DIR: Path = Path("output")

NUM_MESAS: int = 100
CODIGO_MESA_INICIAL: int = 100001

CANDIDATOS: List[str] = [
    "Candidato_A",
    "Candidato_B",
    "Candidato_C",
]

DEPARTAMENTOS_DISTRITOS: Dict[str, List[str]] = {
    "Lima": ["Lima", "Los Olivos", "Miraflores", "San Isidro"],
    "Arequipa": ["Arequipa", "Cayma", "Yanahuara", "Cerro Colorado"],
    "Cusco": ["Cusco", "Wanchaq", "San Sebastian", "Santiago"],
}

MesaInfo = Dict[str, object]


def generar_mesas() -> Dict[int, MesaInfo]:
    """
    Genera la información base de cada mesa.
    Esta información será reutilizada por los otros archivos para mantener consistencia.
    """
    mesas_info: Dict[int, MesaInfo] = {}

    for i in range(NUM_MESAS):
        codigo_mesa: int = CODIGO_MESA_INICIAL + i

        departamento: str = random.choice(list(DEPARTAMENTOS_DISTRITOS.keys()))
        distrito: str = random.choice(DEPARTAMENTOS_DISTRITOS[departamento])
        provincia: str = departamento
        local: str = f"Local_{codigo_mesa}"
        electores_habiles: int = random.randint(250, 350)

        mesas_info[codigo_mesa] = {
            "codigo_mesa": codigo_mesa,
            "local": local,
            "distrito": distrito,
            "provincia": provincia,
            "departamento": departamento,
            "electores_habiles": electores_habiles,
        }

    return mesas_info


def escribir_mesas(mesas_info: Dict[int, MesaInfo]) -> None:
    """
    Escribe el archivo mesas.csv.
    """
    output_path: Path = OUTPUT_DIR / "mesas.csv"

    with output_path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)

        writer.writerow([
            "codigo_mesa",
            "local",
            "distrito",
            "provincia",
            "departamento",
            "electores_habiles",
        ])

        for mesa in mesas_info.values():
            writer.writerow([
                mesa["codigo_mesa"],
                mesa["local"],
                mesa["distrito"],
                mesa["provincia"],
                mesa["departamento"],
                mesa["electores_habiles"],
            ])


def repartir_votos(votantes: int) -> Dict[str, int]:
    """
    Reparte los votos de una mesa entre candidatos, blanco y nulo.
    Garantiza que la suma total de votos sea exactamente igual a votantes.
    """
    votos: Dict[str, int] = {}

    votos_blanco: int = random.randint(0, max(1, int(votantes * 0.08)))
    votos_nulo: int = random.randint(0, max(1, int(votantes * 0.06)))

    votos_validos: int = votantes - votos_blanco - votos_nulo

    pesos: List[float] = [random.random() for _ in CANDIDATOS]
    suma_pesos: float = sum(pesos)

    votos_asignados: int = 0

    for candidato, peso in zip(CANDIDATOS[:-1], pesos[:-1]):
        votos_candidato: int = int((peso / suma_pesos) * votos_validos)
        votos[candidato] = votos_candidato
        votos_asignados += votos_candidato

    ultimo_candidato: str = CANDIDATOS[-1]
    votos[ultimo_candidato] = votos_validos - votos_asignados

    votos["BLANCO"] = votos_blanco
    votos["NULO"] = votos_nulo

    return votos


def generar_participacion_y_resultados(
    mesas_info: Dict[int, MesaInfo]
) -> Tuple[List[List[object]], List[List[object]]]:
    """
    Genera los registros de participacion.csv y resultados_mesa.csv
    usando la misma cantidad de electores por mesa.
    """
    filas_participacion: List[List[object]] = []
    filas_resultados: List[List[object]] = []

    for codigo_mesa, mesa in mesas_info.items():
        electores_habiles: int = int(mesa["electores_habiles"])

        votantes: int = random.randint(
            int(electores_habiles * 0.65),
            electores_habiles
        )

        ausentes: int = electores_habiles - votantes

        filas_participacion.append([
            codigo_mesa,
            electores_habiles,
            votantes,
            ausentes,
        ])

        votos_por_opcion: Dict[str, int] = repartir_votos(votantes)

        for opcion, votos in votos_por_opcion.items():
            filas_resultados.append([
                codigo_mesa,
                opcion,
                votos,
            ])

    return filas_participacion, filas_resultados


def escribir_participacion(filas_participacion: List[List[object]]) -> None:
    """
    Escribe el archivo participacion.csv.
    """
    output_path: Path = OUTPUT_DIR / "participacion.csv"

    with output_path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)

        writer.writerow([
            "codigo_mesa",
            "electores_habiles",
            "votantes",
            "ausentes",
        ])

        writer.writerows(filas_participacion)


def escribir_resultados(filas_resultados: List[List[object]]) -> None:
    """
    Escribe el archivo resultados_mesa.csv.
    """
    output_path: Path = OUTPUT_DIR / "resultados_mesa.csv"

    with output_path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)

        writer.writerow([
            "codigo_mesa",
            "candidato",
            "votos",
        ])

        writer.writerows(filas_resultados)


def main() -> None:
    """
    Genera los tres archivos simulados de ONPE de forma consistente.
    """
    random.seed(42)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    mesas_info: Dict[int, MesaInfo] = generar_mesas()

    escribir_mesas(mesas_info)

    filas_participacion, filas_resultados = generar_participacion_y_resultados(
        mesas_info
    )

    escribir_participacion(filas_participacion)
    escribir_resultados(filas_resultados)

    print("Archivos generados correctamente en:", OUTPUT_DIR.resolve())


if __name__ == "__main__":
    main()

# python3 generate_onpe_data.py