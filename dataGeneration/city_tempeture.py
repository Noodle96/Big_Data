from datetime import date, datetime, timedelta
import random
import pandas as pd
from pathlib import Path
from typing import Dict, Tuple, List

def generate_weather_data(
    num_records: int,
    start_date: date,
    end_date: date,
    cities: Dict[str, Tuple[float, float]]
) -> pd.DataFrame:
    """
    Genera un DataFrame con registros de fecha, ciudad y temperatura.

    Args:
        num_records (int): Número de registros a generar.
        start_date (date): Fecha inicial del rango.
        end_date (date): Fecha final del rango.
        cities (Dict[str, Tuple[float, float]]): Mapa de ciudades a tupla (temp_min, temp_max).

    Returns:
        pd.DataFrame: DataFrame ordenado por fecha con columnas ['date', 'city', 'temperature'].
    """
    date_range: int = (end_date - start_date).days + 1
    records: List[Dict[str, object]] = []

    for _ in range(num_records):
        random_days: int = random.randint(0, date_range - 1)
        dt: date = start_date + timedelta(days=random_days)
        city: str = random.choice(list(cities.keys()))
        temp_min, temp_max = cities[city]
        temperature: float = round(random.uniform(temp_min, temp_max), 1)
        records.append({
            "date": dt,
            "city": city,
            "temperature": temperature
        })

    df: pd.DataFrame = pd.DataFrame(records)
    df_sorted: pd.DataFrame = df.sort_values(by="date").reset_index(drop=True)
    return df_sorted

def save_to_txt(
    df: pd.DataFrame,
    output_path: Path,
    separator: str = ","
) -> None:
    """
    Guarda un DataFrame en un archivo de texto con el formato date,city,temperature.

    Args:
        df (pd.DataFrame): DataFrame a guardar.
        output_path (Path): Ruta del archivo de salida.
        separator (str): Separador de campos.
    """
    df.to_csv(output_path, sep=separator, index=False, header=False)

def main() -> None:
    # Parámetros
    num_records: int = 50000
    start_date: date = date(2025, 1, 1)
    end_date: date = date(2025, 12, 31)
    cities: Dict[str, Tuple[float, float]] = {
        "Lima": (20.0, 25.0),   # mean range for Lima
        "Cusco": (10.0, 20.0),   # mean range for Cusco
        "Arequipa": (15.0, 25.0), # mean range for Arequipa
        "Trujillo": (18.0, 28.0), # mean range for Trujillo
        "Piura": (22.0, 32.0),   # mean range for Piura
        "Iquitos": (25.0, 35.0), # mean range for Iquitos
        "Puno": (5.0, 15.0),     # mean range for Puno
        "Tacna": (10.0, 20.0),   # mean range for Tacna
        "Huancayo": (10.0, 20.0), # mean range for Huancayo
        "Chiclayo": (20.0, 30.0), # mean range for Chiclayo
    }
    output_path: Path = Path("generated_weather_data.txt")

    # Generar y guardar
    df_sorted: pd.DataFrame = generate_weather_data(num_records, start_date, end_date, cities)
    save_to_txt(df_sorted, output_path)

    # Mostrar primeras 10 líneas
    print(df_sorted.head(10).to_string(index=False))

if __name__ == "__main__":
    main()
