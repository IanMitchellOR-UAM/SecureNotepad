import os
import customtkinter as ctk
from tkinter import filedialog, messagebox, Menu
from utils import NoteManager

class SecureNotepadApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Secure Notepad")
        self.root.geometry("800x600")
        self.context_menu = None
        self.current_note_context = None
        ctk.set_appearance_mode("system")

        self.manager = NoteManager()
        self.selected_note = None
        self.password_cache = {}  # Cache de contraseñas temporales

        self.setup_ui()

    def setup_ui(self):
        self.sidebar = ctk.CTkFrame(self.root, width=200)
        self.sidebar.pack(side="left", fill="y")

        # Frame para botones principales (Nueva nota e Importar)
        self.top_buttons_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        self.top_buttons_frame.pack(fill="x", padx=5, pady=(5, 0))

        # Botón para nueva nota
        self.add_note_button = ctk.CTkButton(
            self.top_buttons_frame,
            text="Nueva Nota",
            command=self.new_note
        )
        self.add_note_button.pack(side="left", fill="x", expand=True, padx=(0, 2))

        # Botón para importar nota
        self.import_button = ctk.CTkButton(
            self.top_buttons_frame,
            text="Importar",
            command=self.import_note,
            width=80
        )
        self.import_button.pack(side="right", padx=(2, 0))

        # Frame para la lista de notas con scrollbar
        self.note_list_frame = ctk.CTkScrollableFrame(self.sidebar)
        self.note_list_frame.pack(fill="both", expand=True, padx=5, pady=5)

        # Frame para botones inferiores (Guardar y Tema)
        self.bottom_buttons_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        self.bottom_buttons_frame.pack(fill="x", padx=5, pady=(5, 10))

        # Botón para cambiar tema con iconos
        self.toggle_theme_button = ctk.CTkButton(
            self.bottom_buttons_frame,
            text="☀️",
            command=self.toggle_theme,
            width=50
        )
        self.toggle_theme_button.pack(side="left", padx=(0, 2))

        # Botón para guardar nota
        self.save_button = ctk.CTkButton(
            self.bottom_buttons_frame,
            text="Guardar",
            command=self.save_note,
            fg_color="#2e8b57",
            hover_color="#3cb371"
        )
        self.save_button.pack(side="right", fill="x", expand=True, padx=(2, 0))

        # Área de texto principal
        self.text_area = ctk.CTkTextbox(self.root)
        self.text_area.pack(fill="both", expand=True, padx=5, pady=5)

        # Cargar lista de notas y establecer tema inicial
        self.load_note_list()
        self.update_theme_icon()

    def load_note_list(self):
        for widget in self.note_list_frame.winfo_children():
            widget.destroy()

        for note in self.manager.notes.keys():
            note_frame = ctk.CTkFrame(self.note_list_frame, corner_radius=5)
            note_frame.pack(fill="x", padx=2, pady=2)

            note_btn = ctk.CTkButton(
                note_frame,
                text=note,
                corner_radius=5,
                height=30,
                fg_color="transparent",
                hover_color=("#e0e0e0", "#3a3a3a"),
                anchor="w",
                command=lambda n=note: self.select_note(n)
            )
            note_btn.pack(side="left", fill="x", expand=True, padx=0)

            menu_btn = ctk.CTkButton(
                note_frame,
                text="⋯",
                width=30,
                height=30,
                corner_radius=5,
                command=lambda n=note: self.show_context_menu(n)
            )
            menu_btn.pack(side="right", padx=0)

    def show_context_menu(self, note_name):
        # Destruir el menú anterior si existe
        if hasattr(self, 'context_menu') and self.context_menu:
            self.context_menu.destroy()

        self.current_note_context = note_name

        # Crear menú contextual usando tkinter.Menu
        self.context_menu = Menu(self.root, tearoff=0, bg='#333333', fg='white',
                                 activebackground='#4a4a4a', activeforeground='white')

        # Añadir opciones al menú
        self.context_menu.add_command(
            label="Cambiar nombre",
            command=self.rename_note_dialog
        )
        self.context_menu.add_command(
            label="Cambiar contraseña",
            command=self.change_password_dialog
        )
        self.context_menu.add_separator()
        self.context_menu.add_command(
            label="Exportar",
            command=self.export_note
        )
        self.context_menu.add_separator()
        self.context_menu.add_command(
            label="Eliminar",
            command=self.delete_note_context,
            foreground='#ff6b6b'
        )

        # Mostrar el menú cerca del botón
        try:
            self.context_menu.tk_popup(
                self.root.winfo_pointerx(),
                self.root.winfo_pointery()
            )
            # Asegurarse de que el menú se cierre al hacer clic en otro lugar
            self.root.bind("<Button-1>", lambda e: self.context_menu.unpost())
        except Exception as e:
            print(f"Error al mostrar menú contextual: {e}")

    def delete_note_context(self):
        """Wrapper para eliminar desde el menú contextual"""
        if self.current_note_context:
            self.selected_note = self.current_note_context
            self.delete_note()

    def new_note(self):
        name = self.ask_text("Nombre de la nota")
        if not name:
            return
        password = self.ask_password("Contraseña para la nota")
        if not password:
            return
        self.manager.create_note(name, password)
        self.password_cache[name] = password  # Guardar contraseña temporalmente
        self.load_note_list()

    def select_note(self, name):
        if name not in self.manager.notes:
            messagebox.showerror("Error", "La nota no existe")
            return

        try:
            password = self.password_cache.get(name)
            if not password:
                password = self.ask_password(f"Contraseña para '{name}'")
                if not password:  # Si el usuario cancela el diálogo
                    return

            content = self.manager.decrypt_note(name, password)
            self.password_cache[name] = password
            self.selected_note = name
            self.text_area.delete("1.0", "end")
            self.text_area.insert("1.0", content)
        except ValueError as e:
            messagebox.showerror("Error", str(e))
        except Exception as e:
            messagebox.showerror("Error", f"Error inesperado: {str(e)}")

    def save_note(self):
        if not self.selected_note:
            messagebox.showwarning("Advertencia", "No hay ninguna nota seleccionada")
            return

        content = self.text_area.get("1.0", "end").strip()
        password = self.password_cache.get(self.selected_note)

        if not password:
            password = self.ask_password(f"Contraseña para guardar '{self.selected_note}'")
            if not password:
                return

        try:
            self.manager.save_note(self.selected_note, content, password)
            messagebox.showinfo("Éxito", f"'{self.selected_note}' guardada exitosamente")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def export_note(self):
        if self.selected_note:
            export_path = filedialog.asksaveasfilename(
                defaultextension=".encryptednote",
                filetypes=[("Encrypted Note", "*.encryptednote")],
                initialfile=f"{self.selected_note}.encryptednote"
            )
            if export_path:
                try:
                    self.manager.export_note(self.selected_note, export_path)
                    messagebox.showinfo("Exportación Exitosa", f"'{self.selected_note}' exportada a {export_path}")
                except Exception as e:
                    messagebox.showerror("Error", str(e))

    def import_note(self):
        import_path = filedialog.askopenfilename(
            filetypes=[("Encrypted Note", "*.encryptednote")]
        )
        if import_path:
            password = self.ask_password("Contraseña para importar la nota")
            if password:
                try:
                    name = self.manager.import_note(import_path, password)
                    self.load_note_list()
                    messagebox.showinfo("Importación Exitosa", f"'{name}' importada correctamente")
                    # Seleccionar automáticamente la nota importada
                    self.select_note(name)
                except Exception as e:
                    messagebox.showerror("Error", str(e))

    def delete_note(self):
        if not self.selected_note:
            messagebox.showwarning("Advertencia", "No hay ninguna nota seleccionada")
            return

        confirm = messagebox.askyesno(
            "Confirmar eliminación",
            f"¿Estás seguro de que quieres eliminar la nota '{self.selected_note}'?\nEsta acción no se puede deshacer."
        )

        if confirm:
            try:
                self.manager.delete_note(self.selected_note)
                # Limpiar caché de contraseñas si existe
                self.password_cache.pop(self.selected_note, None)
                # Limpiar el área de texto
                self.text_area.delete("1.0", "end")
                # Deseleccionar la nota
                self.selected_note = None
                # Recargar la lista
                self.load_note_list()
                messagebox.showinfo("Éxito", "Nota eliminada correctamente")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo eliminar la nota: {str(e)}")

    def rename_note_dialog(self):
        if not self.current_note_context:
            return

        old_name = self.current_note_context
        new_name = self.ask_text(f"Cambiar nombre de '{old_name}'", default_text=old_name)

        if new_name and new_name != old_name:
            try:
                # Verificar si la nueva nota ya existe
                if new_name in self.manager.notes:
                    raise ValueError("Ya existe una nota con ese nombre")

                # Obtener el contenido actual
                password = self.password_cache.get(old_name) or self.ask_password(f"Contraseña para '{old_name}'")
                if not password:
                    return

                content = self.manager.decrypt_note(old_name, password)

                # Crear nueva nota con el nuevo nombre
                self.manager.create_note(new_name, password)
                self.manager.save_note(new_name, content, password)

                # Eliminar la nota antigua
                self.manager.delete_note(old_name)

                # Actualizar caché de contraseñas
                if old_name in self.password_cache:
                    self.password_cache[new_name] = self.password_cache.pop(old_name)

                # Actualizar selección si es necesario
                if self.selected_note == old_name:
                    self.selected_note = new_name

                messagebox.showinfo("Éxito", f"Nota renombrada de '{old_name}' a '{new_name}'")
                self.load_note_list()

            except Exception as e:
                messagebox.showerror("Error", str(e))

    def change_password_dialog(self):
        if not self.current_note_context:
            return

        note_name = self.current_note_context

        # Pedir contraseña actual
        current_password = self.password_cache.get(note_name) or self.ask_password(
            f"Contraseña actual de '{note_name}'")
        if not current_password:
            return

        try:
            # Verificar que la contraseña actual es correcta
            content = self.manager.decrypt_note(note_name, current_password)

            # Pedir nueva contraseña
            new_password = self.ask_password(f"Nueva contraseña para '{note_name}'", is_password=True)
            if not new_password:
                return

            # Guardar con la nueva contraseña
            self.manager.save_note(note_name, content, new_password)

            # Actualizar caché
            self.password_cache[note_name] = new_password

            messagebox.showinfo("Éxito", "Contraseña cambiada correctamente")

        except Exception as e:
            messagebox.showerror("Error", str(e))

    def toggle_theme(self):
        current_mode = ctk.get_appearance_mode()
        new_mode = "light" if current_mode == "Dark" else "dark"
        ctk.set_appearance_mode(new_mode)
        self.update_theme_icon()

    def update_theme_icon(self):
        """Actualiza el icono del botón de tema según el modo actual"""
        current_mode = ctk.get_appearance_mode()
        if current_mode == "Dark":
            self.toggle_theme_button.configure(text="🌙")  # Luna para modo oscuro
        else:
            self.toggle_theme_button.configure(text="☀️")  # Sol para modo claro

    def update_button_colors(self, mode):
        """Opcional: Actualiza colores de botones para que coincidan con el tema"""
        if mode == "dark":
            self.delete_button.configure(fg_color="#d03e3e", hover_color="#a83232")
        else:
            self.delete_button.configure(fg_color="#ff4d4d", hover_color="#cc4040")

    def ask_text(self, prompt, default_text=""):
        dialog = ctk.CTkInputDialog(text=prompt, title="Entrada de texto")
        # Intentar acceder al campo de entrada
        if hasattr(dialog, '_entry'):
            entry = dialog._entry
        elif hasattr(dialog, 'entry'):
            entry = dialog.entry
        else:
            return dialog.get_input()

        if default_text:
            entry.delete(0, 'end')
            entry.insert(0, default_text)

        return dialog.get_input()

    def ask_password(self, prompt, is_password=True):
        dialog = ctk.CTkInputDialog(text=prompt, title="Contraseña")
        # En CustomTkinter 5.x, el campo de entrada se accede diferente
        if hasattr(dialog, '_entry'):  # Para algunas versiones
            entry = dialog._entry
        elif hasattr(dialog, 'entry'):  # Para otras versiones
            entry = dialog.entry
        else:
            # Si no encontramos el entry, mostramos el diálogo sin modificar
            return dialog.get_input()

        if is_password:
            entry.configure(show="•")
        return dialog.get_input()

if __name__ == "__main__":
    root = ctk.CTk()
    app = SecureNotepadApp(root)
    root.mainloop()
