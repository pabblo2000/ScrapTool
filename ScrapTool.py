import os
import sys
import subprocess
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
from tkinter import ttk
import threading

# Definir la ruta base del proyecto
ScrapTool_dir = os.path.dirname(os.path.abspath(__file__))

# Definir rutas específicas dentro de la estructura del proyecto
config_dir = os.path.join(ScrapTool_dir, 'Config')
env_dir = os.path.join(config_dir, 'ScraperEnvironment')
download_dir = os.path.join(config_dir, 'Downloads')
chrome_dir = os.path.join(config_dir, 'Chrome')
scrap_engines_dir = os.path.join(ScrapTool_dir, 'ScrapEngines')

# Crear la interfaz gráfica
root = tk.Tk()
root.title("Scraper Tool")

style = ttk.Style()
style.theme_use('clam')

root.geometry("600x500")
root.resizable(False, False)
root.configure(bg='#f0f0f0')

# Función para seleccionar el archivo de scraping
def select_file():
    file_path = filedialog.askopenfilename(
        initialdir=scrap_engines_dir,
        filetypes=[("Python files", "*.py")],
    )
    if file_path:
        entry_file_path.set(os.path.basename(file_path))

# Función para validar la longitud de entrada en los campos de texto
def validate_entry(new_value):
    # Permite solo números y una longitud máxima de 3 caracteres
    if new_value == "" or (new_value.isdigit() and len(new_value) <= 3):
        return True
    return False

# Función para incrementar el valor del campo
def increment_var(entry_var):
    current_value = entry_var.get()
    if current_value.isdigit():
        entry_var.set(str(min(int(current_value) + 1, 999)))

# Función para decrementar el valor del campo
def decrement_var(entry_var):
    current_value = entry_var.get()
    if current_value.isdigit():
        entry_var.set(str(max(int(current_value) - 1, 0)))

# Configurar la validación
vcmd = (root.register(validate_entry), '%P')

# Función para ejecutar el scraping
def run_scraping(event=None):  # Se agrega `event=None` para manejar el evento de la tecla "Enter"
    file_name = entry_file_path.get()
    if not file_name:
        messagebox.showerror("Error", "Por favor, selecciona un archivo .py")
        return

    file_path = os.path.join(scrap_engines_dir, file_name)
    python_executable = os.path.join(env_dir, "Scripts", "python.exe")

    # Imprimir rutas para depuración
    print("Python Executable Path:", python_executable)
    print("File Path:", file_path)

    # Variables adicionales obtenidas de la interfaz
    to_search = entry_search.get()
    products_to_visit = int(entry_links.get())
    max_comment_pages_to_visit = int(entry_pages.get())
    max_images_to_download = int(entry_images.get())
    show_search_engine = show_search_engine_var.get() == 0
    image_download = image_download_var.get() == 1
    see_window = see_window_var.get() == 1
    close_after_finish = close_var.get() == 1

    def execute_script():
        # Verifica la ruta del ejecutable de Python y el archivo Python
        print("Python Executable Path:", python_executable)
        print("File Path:", file_path)

        # Mostrar el mensaje en la consola
        console_text.insert(tk.END, "Ejecutando Scraper...\n")
        console_text.yview(tk.END)

        try:
            process = subprocess.Popen(
                [python_executable, file_path, to_search, str(products_to_visit),
                str(max_comment_pages_to_visit), str(max_images_to_download),
                str(show_search_engine), str(image_download), str(see_window),
                str(close_after_finish)],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, shell=True
            )
            for line in process.stdout:
                console_text.insert(tk.END, line)
                console_text.yview(tk.END)
            for line in process.stderr:
                console_text.insert(tk.END, line)
                console_text.yview(tk.END)
            process.stdout.close()
            process.stderr.close()
        except FileNotFoundError as e:
            print(f"FileNotFoundError: {e}")
        except Exception as e:
            print(f"Error: {e}")

    threading.Thread(target=execute_script).start()

# Variables para la interfaz
entry_file_path = tk.StringVar(value="AMAZON.py")
entry_search = tk.StringVar(value="smartphone")
entry_links = tk.StringVar(value="3")
entry_pages = tk.StringVar(value="3")
entry_images = tk.StringVar(value="3")
show_search_engine_var = tk.IntVar(value=0)
image_download_var = tk.IntVar(value=1)
see_window_var = tk.IntVar(value=1)
close_var = tk.IntVar(value=1)

# Interfaz de entrada de datos
frame_inputs = ttk.Frame(root, padding="10 10 10 10")
frame_inputs.pack(pady=10, fill=tk.X)

ttk.Label(frame_inputs, text="Seleccionar Scraper:").grid(row=0, column=0, sticky="e", padx=5, pady=5)
ttk.Entry(frame_inputs, textvariable=entry_file_path, width=40).grid(row=0, column=1, padx=5, pady=5)
ttk.Button(frame_inputs, text="Buscar", command=select_file).grid(row=0, column=2, padx=5, pady=5)

ttk.Label(frame_inputs, text="Producto a Buscar:").grid(row=1, column=0, sticky="e", padx=5, pady=5)
ttk.Entry(frame_inputs, textvariable=entry_search, width=40).grid(row=1, column=1, padx=5, pady=5)

ttk.Label(frame_inputs, text="Max links a Visitar:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
ttk.Entry(frame_inputs, textvariable=entry_links, width=5, validate='key', validatecommand=vcmd).grid(row=2, column=1, sticky="w", padx=5, pady=5)
ttk.Button(frame_inputs, text="+", width=3, command=lambda: increment_var(entry_links)).grid(row=2, column=2)
ttk.Button(frame_inputs, text="-", width=3, command=lambda: decrement_var(entry_links)).grid(row=2, column=3)

ttk.Label(frame_inputs, text="Max pags de Comentarios:").grid(row=3, column=0, sticky="w", padx=5, pady=5)
ttk.Entry(frame_inputs, textvariable=entry_pages, width=5, validate='key', validatecommand=vcmd).grid(row=3, column=1, sticky="w", padx=5, pady=5)
ttk.Button(frame_inputs, text="+", width=3, command=lambda: increment_var(entry_pages)).grid(row=3, column=2)
ttk.Button(frame_inputs, text="-", width=3, command=lambda: decrement_var(entry_pages)).grid(row=3, column=3)

ttk.Label(frame_inputs, text="Máx Img por producto:").grid(row=4, column=0, sticky="w", padx=5, pady=5)
ttk.Entry(frame_inputs, textvariable=entry_images, width=5, validate='key', validatecommand=vcmd).grid(row=4, column=1, sticky="w", padx=5, pady=5)
ttk.Button(frame_inputs, text="+", width=3, command=lambda: increment_var(entry_images)).grid(row=4, column=2)
ttk.Button(frame_inputs, text="-", width=3, command=lambda: decrement_var(entry_images)).grid(row=4, column=3)

ttk.Checkbutton(frame_inputs, text="Mostrar Motor de Búsqueda", variable=show_search_engine_var).grid(row=5, columnspan=2, sticky="w", padx=5, pady=5)
ttk.Checkbutton(frame_inputs, text="Descargar Imágenes", variable=image_download_var).grid(row=6, columnspan=2, sticky="w", padx=5, pady=5)
ttk.Checkbutton(frame_inputs, text="Ver Ventana", variable=see_window_var).grid(row=7, columnspan=2, sticky="w", padx=5, pady=5)
ttk.Checkbutton(frame_inputs, text="Cerrar después de Terminar", variable=close_var).grid(row=8, columnspan=2, sticky="w", padx=5, pady=5)

ttk.Button(root, text="Ejecutar Scraping", command=run_scraping).pack(pady=10)

# Consola para mostrar la salida
console_frame = ttk.Frame(root)
console_frame.pack(pady=10, fill=tk.BOTH, expand=True)

console_text = scrolledtext.ScrolledText(console_frame, wrap=tk.WORD, height=10, width=70, state=tk.NORMAL)
console_text.pack(fill=tk.BOTH, expand=True)
console_text.insert(tk.END, "Consola de Salida:\n")

# Binding de la tecla "Enter" para ejecutar el scraping
root.bind('<Return>', run_scraping)

# Iniciar la aplicación
root.mainloop()
