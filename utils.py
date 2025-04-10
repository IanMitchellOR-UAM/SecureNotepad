import os
import json
from crypto_manager import encrypt_note, decrypt_note


class NoteManager:
    def __init__(self, notes_dir="notes"):
        self.notes_dir = notes_dir
        os.makedirs(notes_dir, exist_ok=True)
        self.notes = self._load_existing_notes()

    def _load_existing_notes(self):
        """Carga las notas existentes del directorio al iniciar"""
        notes = {}
        for filename in os.listdir(self.notes_dir):
            if filename.endswith(".encryptednote"):
                name = filename[:-14]  # Elimina la extensión .encryptednote
                notes[name] = os.path.join(self.notes_dir, filename)
        return notes

    def create_note(self, name, password):
        """Crea una nueva nota vacía verificando que no exista"""
        if name in self.notes:
            raise ValueError("Ya existe una nota con ese nombre")
        encrypted = encrypt_note("", password)
        self._save_to_disk(name, encrypted)
        self.notes[name] = os.path.join(self.notes_dir, f"{name}.encryptednote")

    def rename_note(self, old_name, new_name):
        """Renombra una nota en el sistema de archivos"""
        if old_name not in self.notes:
            raise ValueError("Nota original no encontrada")
        if new_name in self.notes:
            raise ValueError("Ya existe una nota con el nuevo nombre")

        old_path = self.notes[old_name]
        new_path = os.path.join(self.notes_dir, f"{new_name}.encryptednote")

        os.rename(old_path, new_path)
        self.notes[new_name] = new_path
        del self.notes[old_name]

    def save_note(self, name, content, password):
        """Guarda el contenido de una nota existente"""
        encrypted = encrypt_note(content, password)
        self._save_to_disk(name, encrypted)

    def _save_to_disk(self, name, encrypted_content):
        """Guarda el contenido encriptado en disco"""
        filename = os.path.join(self.notes_dir, f"{name}.encryptednote")
        with open(filename, "w") as f:
            f.write(encrypted_content)

    def load_note_content(self, name):
        """Carga el contenido encriptado de una nota"""
        if name not in self.notes:
            return None
        with open(self.notes[name], "r") as f:
            return f.read()

    def decrypt_note(self, name, password):
        """Desencripta una nota"""
        encrypted = self.load_note_content(name)
        if not encrypted:
            raise ValueError("Nota no encontrada")
        try:
            return decrypt_note(encrypted, password)
        except Exception as e:
            raise ValueError("Contraseña incorrecta o nota corrupta")

    def import_note(self, filepath, password):
        """Importa una nota desde un archivo externo"""
        with open(filepath, "r") as f:
            encrypted_content = f.read()

        # Verificar que la contraseña es correcta intentando desencriptar
        try:
            decrypt_note(encrypted_content, password)
        except Exception as e:
            raise ValueError("Contraseña incorrecta o archivo corrupto")

        # Extraer el nombre del archivo sin extensión
        name = os.path.basename(filepath).replace(".encryptednote", "")

        # Si ya existe una nota con ese nombre, añadir sufijo
        original_name = name
        counter = 1
        while name in self.notes:
            name = f"{original_name}_{counter}"
            counter += 1

        new_path = os.path.join(self.notes_dir, f"{name}.encryptednote")

        # Guardar la nota en nuestro directorio
        with open(new_path, "w") as f:
            f.write(encrypted_content)

        self.notes[name] = new_path
        return name

    def export_note(self, name, dest_path):
        """Exporta una nota a una ubicación específica"""
        if name not in self.notes:
            raise FileNotFoundError(f"No se encontró la nota '{name}'")

        with open(self.notes[name], "r") as source, open(dest_path, "w") as dest:
            dest.write(source.read())

    def delete_note(self, name):
        """Elimina una nota tanto de memoria como del sistema de archivos"""
        if name in self.notes:
            try:
                # Eliminar el archivo físico
                filepath = self.notes[name]
                if os.path.exists(filepath):
                    os.remove(filepath)
                # Eliminar de la lista de notas
                del self.notes[name]
            except Exception as e:
                raise Exception(f"No se pudo eliminar la nota: {str(e)}")