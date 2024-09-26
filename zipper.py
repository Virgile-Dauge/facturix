import zipfile

from pathlib import Path
from datetime import date

import os
import zipfile

from pathlib import Path
from datetime import date


def create_zip(zip_path: Path, file_list: list[Path]):
    """
    Creates a zip archive containing the specified files.

    Parameters:
    zip_path (Path): The destination path for the created zip file.
    file_list (list[Path]): A list of Path objects representing the files to include in the zip archive.

    Returns:
    None
    """
    with zipfile.ZipFile(zip_path, 'w') as zipf:
        for file in file_list:
            zipf.write(file, arcname=file.name)

def gen_zip_path(dest_dir: Path, batch_counter: int, name:str) -> Path:
    return dest_dir / f"{date.today().strftime('%Y%m%d')}_{name}_{batch_counter}.zip"

def create_zip_batches(files: list[Path], dest_dir: Path, 
                       max_files: int=500, max_size_mo: int=20, 
                       name:str='arch'):
    max_size_o = max_size_mo * 1024 * 1024  # Convertir Mo en octets

    if not files:
        raise ValueError("La liste des fichiers est vide.")
    max_file_size = max(file.stat().st_size for file in files)
    if max_file_size > max_size_o:
        raise ValueError(f"File size {max_file_size} bytes exceeds the allowed maximum of {max_size_o} bytes.")

    # Vérifie si le répertoire de destination existe, sinon le crée
    if not dest_dir.exists():
        dest_dir.mkdir(parents=True, exist_ok=True)

    
    batch_counter = 0

    current_zip = None
    current_batch = []
    while files:
        # Crée un nouveau fichier zip s'il n'y en a pas de courant
        if current_zip is None:
            current_zip_path = gen_zip_path(dest_dir, batch_counter, name)
            current_zip = zipfile.ZipFile(current_zip_path, 'w')
        
        # Vérifie si le nombre maximal de fichiers dans le batch est atteint
        if len(current_batch) + 1 > max_files:
            # Ferme le fichier zip actuel
            current_zip.close()
            # Réinitialise le batch courant et passe au suivant
            batch_counter += 1
            current_zip = None
            current_batch = []
            continue
        
        # Ajoute un fichier au zip courant
        candidate = files[0]
        current_zip.write(candidate, arcname=candidate.name)
        
        # Vérifie si la taille maximale du zip est dépassée
        if current_zip_path.stat().st_size > max_size_o:
            # Supprime le fichier zip trop volumineux
            current_zip.close()
            os.remove(current_zip_path)

            # Crée un nouveau zip avec tous les fichiers sauf le dernier ajouté
            create_zip(current_zip_path, current_batch)

            # Réinitialise le batch courant et passe au suivant
            batch_counter += 1
            current_zip = None
            current_batch = []
            continue
            
        current_batch.append(candidate)
        files.pop(0)

# Example usage
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Create zip files in batches.")
    parser.add_argument('-i', '--input', type=str, required=True, help='Input directory')
    parser.add_argument('-o', '--output', type=str, required=True, help='Output directory')
    parser.add_argument('-s', '--max_size', type=int, default=20, help='Maximum size of each zip file in MB')
    parser.add_argument('-f', '--max_files', type=int, default=500, help='Maximum number of files per zip file')

    args = parser.parse_args()

    input_dir = Path(args.input).expanduser()
    output_dir = Path(args.output).expanduser()

    files = list(input_dir.glob('*'))
    create_zip_batches(files, output_dir, max_files=args.max_files, max_size_mo=args.max_size)
