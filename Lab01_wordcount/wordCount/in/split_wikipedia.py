from pathlib import Path


INPUT_FILE: Path = Path("wikipedia.txt")
OUTPUT_DIR: Path = Path("split")

NUM_PARTS: int = 16


def get_file_size_bytes(file_path: Path) -> int:
    """
    Devuelve el tamaño del archivo en bytes.
    """
    return file_path.stat().st_size


def format_size(size_bytes: int) -> str:
    """
    Convierte bytes a una representación legible.
    """
    size_mb: float = size_bytes / (1024 ** 2)
    size_gb: float = size_bytes / (1024 ** 3)

    if size_gb >= 1:
        return f"{size_gb:.2f} GiB"

    return f"{size_mb:.2f} MiB"


def open_part_file(part_index: int):
    """
    Abre un archivo de salida para una parte específica.
    """
    output_path: Path = OUTPUT_DIR / f"wiki_part_{part_index:04d}.txt"

    return output_path.open("wb"), output_path


def split_file_by_lines() -> None:
    """
    Divide wikipedia.txt en NUM_PARTS archivos de tamaño parecido.

    La división se hace por líneas completas:
    - No corta palabras.
    - No corta líneas a la mitad.
    - Cada parte queda con tamaño aproximado.
    """
    if not INPUT_FILE.exists():
        raise FileNotFoundError(f"No existe el archivo: {INPUT_FILE}")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    total_size: int = get_file_size_bytes(INPUT_FILE)
    target_part_size: int = total_size // NUM_PARTS

    print(f"Archivo original: {INPUT_FILE}")
    print(f"Tamaño original: {format_size(total_size)}")
    print(f"Número de partes: {NUM_PARTS}")
    print(f"Tamaño objetivo por parte: {format_size(target_part_size)}")
    print()

    current_part: int = 1
    current_part_size: int = 0

    output_file, output_path = open_part_file(current_part)

    with INPUT_FILE.open("rb") as input_file:
        for line in input_file:
            if (
                current_part < NUM_PARTS
                and current_part_size >= target_part_size
            ):
                output_file.close()

                print(
                    f"Parte {current_part:04d}: "
                    f"{output_path} -> {format_size(current_part_size)}"
                )

                current_part += 1
                current_part_size = 0

                output_file, output_path = open_part_file(current_part)

            output_file.write(line)
            current_part_size += len(line)

    output_file.close()

    print(
        f"Parte {current_part:04d}: "
        f"{output_path} -> {format_size(current_part_size)}"
    )

    print()
    print("División completada correctamente.")


def main() -> None:
    """
    Punto de entrada del script.
    """
    split_file_by_lines()


if __name__ == "__main__":
    main()