from pathlib import Path
from typing import Any, Dict, List

import pandas as pd
from flask import Flask, jsonify
from flask_cors import CORS


app: Flask = Flask(__name__)
CORS(app)

BASE_DIR: Path = Path(__file__).resolve().parent
DATA_DIR: Path = BASE_DIR / "data"


def read_two_column_tsv(
    file_name: str,
    col1: str,
    col2: str,
) -> pd.DataFrame:
    file_path: Path = DATA_DIR / file_name

    return pd.read_csv(
        file_path,
        sep="\t",
        header=None,
        names=[col1, col2],
    )


@app.route("/api/health", methods=["GET"])
def health() -> Any:
    return jsonify({"status": "ok"})


@app.route("/api/votos-totales", methods=["GET"])
def votos_totales() -> Any:
    df: pd.DataFrame = read_two_column_tsv(
        "votos_totales.tsv",
        "organizacion",
        "votos",
    )

    df["votos"] = df["votos"].astype(int)
    df = df.sort_values("votos", ascending=False)

    total_votos: int = int(df["votos"].sum())
    df["porcentaje"] = (df["votos"] / total_votos) * 100

    return jsonify(df.to_dict(orient="records"))


@app.route("/api/votos-region", methods=["GET"])
def votos_region() -> Any:
    df: pd.DataFrame = read_two_column_tsv(
        "votos_region.tsv",
        "region_organizacion",
        "votos",
    )

    split_df: pd.DataFrame = df["region_organizacion"].str.split(
        "|",
        expand=True,
    )

    df["region"] = split_df[0]
    df["organizacion"] = split_df[1]
    df["votos"] = df["votos"].astype(int)

    df = df[["region", "organizacion", "votos"]]
    df = df.sort_values(["region", "votos"], ascending=[True, False])

    return jsonify(df.to_dict(orient="records"))


@app.route("/api/ganador-region", methods=["GET"])
def ganador_region() -> Any:
    df: pd.DataFrame = read_two_column_tsv(
        "ganador_region.tsv",
        "region",
        "ganador_votos",
    )

    split_df: pd.DataFrame = df["ganador_votos"].str.rsplit(
        "|",
        n=1,
        expand=True,
    )

    df["ganador"] = split_df[0]
    df["votos"] = split_df[1].astype(int)

    df = df[["region", "ganador", "votos"]]
    df = df.sort_values("region")

    return jsonify(df.to_dict(orient="records"))


@app.route("/api/nulos-blancos-region", methods=["GET"])
def nulos_blancos_region() -> Any:
    df: pd.DataFrame = read_two_column_tsv(
        "nulos_blancos_region.tsv",
        "region_tipo",
        "votos",
    )

    split_df: pd.DataFrame = df["region_tipo"].str.split(
        "|",
        expand=True,
    )

    df["region"] = split_df[0]
    df["tipo_voto"] = split_df[1]
    df["votos"] = df["votos"].astype(int)

    df = df[["region", "tipo_voto", "votos"]]
    df = df.sort_values(["region", "tipo_voto"])

    return jsonify(df.to_dict(orient="records"))


@app.route("/api/participacion-region", methods=["GET"])
def participacion_region() -> Any:
    df: pd.DataFrame = read_two_column_tsv(
        "participacion_region.tsv",
        "region",
        "valores",
    )

    split_df: pd.DataFrame = df["valores"].str.split(
        "|",
        expand=True,
    )

    df["total_votos"] = split_df[0].astype(int)
    df["total_electores"] = split_df[1].astype(int)
    df["participacion"] = split_df[2].astype(float)
    df["participacion_pct"] = df["participacion"] * 100

    df = df[
        [
            "region",
            "total_votos",
            "total_electores",
            "participacion",
            "participacion_pct",
        ]
    ]

    df = df.sort_values("participacion", ascending=False)

    return jsonify(df.to_dict(orient="records"))


@app.route("/api/votos-provincia", methods=["GET"])
def votos_provincia() -> Any:
    df: pd.DataFrame = read_two_column_tsv(
        "votos_provincia.tsv",
        "region_provincia_organizacion",
        "votos",
    )

    split_df: pd.DataFrame = df["region_provincia_organizacion"].str.split(
        "|",
        expand=True,
    )

    df["region"] = split_df[0]
    df["provincia"] = split_df[1]
    df["organizacion"] = split_df[2]
    df["votos"] = df["votos"].astype(int)

    df = df[["region", "provincia", "organizacion", "votos"]]
    df = df.sort_values(["region", "provincia", "votos"], ascending=[True, True, False])

    return jsonify(df.to_dict(orient="records"))


@app.route("/api/resumen", methods=["GET"])
def resumen() -> Any:
    votos_df: pd.DataFrame = read_two_column_tsv(
        "votos_totales.tsv",
        "organizacion",
        "votos",
    )
    votos_df["votos"] = votos_df["votos"].astype(int)

    participacion_df: pd.DataFrame = read_two_column_tsv(
        "participacion_region.tsv",
        "region",
        "valores",
    )

    split_df: pd.DataFrame = participacion_df["valores"].str.split(
        "|",
        expand=True,
    )

    participacion_df["total_votos"] = split_df[0].astype(int)
    participacion_df["total_electores"] = split_df[1].astype(int)

    total_votos: int = int(votos_df["votos"].sum())
    votos_nulos: int = int(
        votos_df.loc[votos_df["organizacion"] == "VOTOS NULOS", "votos"].sum()
    )
    votos_blancos: int = int(
        votos_df.loc[votos_df["organizacion"] == "VOTOS EN BLANCO", "votos"].sum()
    )
    total_electores: int = int(participacion_df["total_electores"].sum())

    participacion_general: float = (
        total_votos / total_electores if total_electores > 0 else 0.0
    )

    data: Dict[str, Any] = {
        "total_votos": total_votos,
        "votos_nulos": votos_nulos,
        "votos_blancos": votos_blancos,
        "total_electores": total_electores,
        "participacion_general": participacion_general,
        "participacion_general_pct": participacion_general * 100,
    }

    return jsonify(data)


if __name__ == "__main__":
    app.run(debug=True, port=5000)

# python app.py     