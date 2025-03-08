# Importación de librerías necesarias
import tkinter as tk  # Interfaz gráfica (GUI)
from tkinter import filedialog, scrolledtext  # Para abrir archivos y mostrar textos largos
import google.generativeai as genai  # Para interactuar con la API de Gemini AI
import fitz  # PyMuPDF para leer PDFs
import pytesseract  # Para OCR (reconocimiento de texto en imágenes)
from PIL import Image  # Para trabajar con imágenes
import io  # Para manejar datos en memoria

# Configuración de la clave de API para Gemini AI
gemini_api_key = ""
genai.configure(api_key=gemini_api_key)  # Configura la clave de API de Gemini
pytesseract.pytesseract.tesseract_cmd = "Tesseract/tesseract.exe"  # Ruta para el ejecutable de Tesseract

# Función para extraer texto de un archivo PDF (incluyendo texto en imágenes)
def extract_text_from_pdf(pdf_path):
    """Extrae texto de un archivo PDF, incluyendo imágenes con texto."""
    text = ""  # Variable donde se almacenará el texto extraído
    try:
        with fitz.open(pdf_path) as doc:  # Abrimos el archivo PDF
            for page in doc:  # Iteramos sobre cada página
                text += page.get_text("text") + "\n"  # Extraemos el texto de la página
                # Buscamos imágenes en cada página
                for img_index, img in enumerate(page.get_images(full=True)):
                    xref = img[0]  # Referencia cruzada de la imagen
                    base_image = doc.extract_image(xref)  # Extraemos la imagen
                    image_data = base_image["image"]  # Datos binarios de la imagen
                    image = Image.open(io.BytesIO(image_data))  # Abrimos la imagen
                    text += pytesseract.image_to_string(image) + "\n"  # Extraemos texto de la imagen
    except Exception as e:
        text = f"Error al leer el PDF: {e}"  # En caso de error, mostramos el mensaje de error
    return text  # Retorna el texto extraído

# Función para alternar entre los diferentes frames de la interfaz
def toggle_frame(frame):
    """Minimiza o expande un frame."""
    # Ocultar todas las secciones primero
    frame_import.pack_forget()
    frame_analyze.pack_forget()
    frame_chat.pack_forget()
    frame_test.pack_forget()
    frame_help.pack_forget()
    
    # Mostrar la sección seleccionada
    frame.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)

# Función para abrir un archivo TXT o PDF y extraer su contenido
def open_file():
    """Abre un archivo TXT o PDF y extrae su contenido."""
    global document_text  # Variable global donde se guarda el texto extraído
    # Abrir un cuadro de diálogo para seleccionar un archivo
    file_path = filedialog.askopenfilename(filetypes=[("Archivos TXT", "*.txt"), ("Archivos PDF", "*.pdf")])
    if not file_path:
        return  # Si no se selecciona ningún archivo, salimos de la función
    
    # Si es un archivo TXT, lo leemos directamente
    if file_path.endswith(".txt"):
        with open(file_path, "r", encoding="utf-8") as file:
            document_text = file.read()
    # Si es un archivo PDF, extraemos el texto usando la función definida
    elif file_path.endswith(".pdf"):
        document_text = extract_text_from_pdf(file_path)
    else:
        document_text = "Formato no compatible."  # En caso de que el formato no sea soportado
    
    # Limpiar el área de texto y mostrar el contenido extraído
    text_area.delete("1.0", tk.END)
    text_area.insert(tk.END, document_text)

    # Preparar la interfaz para generar preguntas de test
    question_label.config(text="Pregunta:")
    option1_btn.config(text="Opción A")
    option2_btn.config(text="Opción B")
    option3_btn.config(text="Opción C")
    result_label.config(text="")
    generate_test_question_button.config(state=tk.NORMAL)

# Función para analizar el texto con Gemini AI y generar un resumen
def analyze_text():
    """Envía el texto a Gemini AI para obtener un resumen."""
    if not document_text:
        result_area.delete("1.0", tk.END)
        result_area.insert(tk.END, "No hay texto para analizar.")
        return  # Si no hay texto, mostramos un mensaje
    
    try:
        model = genai.GenerativeModel(model_name="gemini-2.0-flash-lite")  # Modelo de Gemini AI
        response = model.generate_content(f"Resume y destaca los puntos clave: {document_text}")
        summary = response.text if response.text else "No se pudo generar el resumen."
    except Exception as e:
        summary = f"Error en la consulta a Gemini: {e}"  # En caso de error, mostramos el mensaje
    
    # Mostrar el resumen en el área de resultados
    result_area.delete("1.0", tk.END)
    result_area.insert(tk.END, summary)

# Función para interactuar con Gemini AI y realizar preguntas sobre el documento
def chat_with_ai():
    """Envía preguntas a Gemini AI con el contexto del documento cargado."""
    user_query = chat_entry.get().strip()  # Obtenemos la consulta del usuario
    if not user_query:
        return  # Si no hay consulta, no hacemos nada
    
    try:
        model = genai.GenerativeModel(model_name="gemini-2.0-flash-lite")  # Modelo de Gemini AI
        response = model.generate_content(f"Basado en este documento: {document_text}\nPregunta: {user_query}")
        answer = response.text if response.text else "No se pudo generar una respuesta."
    except Exception as e:
        answer = f"Error en la consulta a Gemini: {e}"  # En caso de error, mostramos el mensaje
    
    # Mostrar la respuesta de Gemini en el área de chat
    chat_area.config(state=tk.NORMAL)  # Habilitar para mostrar texto
    chat_area.insert(tk.END, f"Tú: {user_query}\nGemini: {answer}\n\n")
    chat_area.config(state=tk.DISABLED)  # Deshabilitar para no permitir escritura
    chat_entry.delete(0, tk.END)  # Limpiar la entrada de texto

# Función para generar una pregunta tipo test basada en el documento cargado
def generate_test_question():
    """Genera una pregunta de tipo test basada en el documento importado."""
    if not document_text:
        question_label.config(text="No hay documento cargado.")
        return

    try:
        model = genai.GenerativeModel(model_name="gemini-2.0-flash-lite")
        # Pedirle a Gemini que genere una pregunta tipo test
        response = model.generate_content(f"Genera una pregunta tipo test con 3 opciones basada en el siguiente texto: {document_text}, no generarás ningun texto adicional ya que tu primera línea será la pregunta, las 3 siguientes líneas las copciones y la quinta ultima línea sera una copia exacta de la respuesta correcta.")
        question_data = response.text.strip().split("\n")  # Dividimos la respuesta en líneas
        
        # Validación para asegurar que se reciban las preguntas y respuestas correctamente
        if len(question_data) < 4:
            question_label.config(text="No se pudo generar una pregunta adecuada.")
            return
        
        question = question_data[0]  # La pregunta está en la primera línea
        options = question_data[2:5]  # Las opciones están en las siguientes tres líneas
        correct_option = question_data[6]  # La respuesta correcta está en la séptima línea

    except Exception as e:
        question = "Error generando la pregunta."
        options = ["Error 1", "Error 2", "Error 3"]
        correct_option = "Error en la respuesta."
    
    # Mostrar la pregunta y las opciones en la interfaz
    question_label.config(text=question)
    option1_btn.config(text=options[0])
    option2_btn.config(text=options[1])
    option3_btn.config(text=options[2])
    correct_answer.set(correct_option)

# Función para verificar si la respuesta seleccionada es correcta
def check_answer(selected_option):
    """Comprueba si la respuesta seleccionada es correcta."""
    if selected_option == correct_answer.get():
        result_label.config(text="¡Correcto!", fg="green")  # Si la respuesta es correcta, mostrar verde
    else:
        result_label.config(text=f"Incorrecto. La respuesta correcta era: {correct_answer.get()}", fg="red")  # Si es incorrecta, mostrar rojo
    
    # Generar una nueva pregunta después de responder
    generate_test_question()

# Creación de la ventana principal (root) de la aplicación
root = tk.Tk()
root.title("Bot IA de estudio")  # Título de la ventana

# Iniciar la ventana a tamaño completo
root.state('zoomed')

document_text = ""  # Variable global para almacenar el texto cargado

# Menú desplegable en la esquina superior derecha
menu_bar = tk.Menu(root)
root.config(menu=menu_bar)  # Configuramos el menú en la ventana

app_menu = tk.Menu(menu_bar, tearoff=0)
menu_bar.add_cascade(label="Menú", menu=app_menu)

def show_help():
    toggle_frame(frame_help)  # Mostrar la sección de ayuda

def show_import():
    toggle_frame(frame_import)  # Mostrar la sección de importar archivo

def show_analyze():
    toggle_frame(frame_analyze)  # Mostrar la sección de análisis

def show_chat():
    toggle_frame(frame_chat)  # Mostrar la sección de chat

def show_test():
    toggle_frame(frame_test)  # Mostrar la sección de preguntas tipo test

# Agregar elementos al menú
app_menu.add_command(label="¿Cómo funciona?", command=show_help)
app_menu.add_command(label="Importar Archivo", command=show_import)
app_menu.add_command(label="Analizar Documento", command=show_analyze)
app_menu.add_command(label="Chatear con Gemini", command=show_chat)
app_menu.add_command(label="Preguntas de Examen", command=show_test)

# **Sección de ayuda (funcionamiento de la app)**
frame_help = tk.Frame(root)
help_text = tk.Label(frame_help, text="Esta es una aplicación para analizar y generar preguntas tipo test de documentos.\n\n"
                                        "1. Carga un archivo de texto o PDF.\n"
                                        "2. Analiza el contenido con Gemini AI.\n"
                                        "3. Genera preguntas de opción múltiple basadas en el documento cargado.\n"
                                        "4. Puedes chatear con la IA sobre el contenido del documento.")
help_text.pack(padx=10, pady=10)
frame_help.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)

# **Sección de importar archivo**
frame_import = tk.Frame(root)
btn_open = tk.Button(frame_import, text="Abrir archivo", command=open_file)  # Botón para abrir el archivo
btn_open.pack(pady=10)
text_area = scrolledtext.ScrolledText(frame_import, wrap=tk.WORD, height=10)  # Área de texto para mostrar el contenido
text_area.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)

# **Sección de análisis**
frame_analyze = tk.Frame(root)
btn_analyze = tk.Button(frame_analyze, text="Analizar con Gemini", command=analyze_text)  # Botón para analizar el texto
btn_analyze.pack(pady=10)
result_area = scrolledtext.ScrolledText(frame_analyze, wrap=tk.WORD, height=5)  # Área de texto para mostrar el resultado
result_area.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)

# **Sección de chat**
frame_chat = tk.Frame(root)
chat_label = tk.Label(frame_chat, text="Chatea con Gemini")  # Etiqueta para la sección de chat
chat_label.pack(pady=5)
chat_area = scrolledtext.ScrolledText(frame_chat, wrap=tk.WORD, height=10)  # Área de texto para mostrar el chat
chat_area.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)
chat_area.config(state=tk.DISABLED)  # Deshabilitar el área para evitar que el usuario escriba directamente
chat_entry = tk.Entry(frame_chat, width=50)  # Entrada de texto para que el usuario escriba sus consultas
chat_entry.pack(pady=5)

# **Evento para presionar Enter y enviar el mensaje**
chat_entry.bind("<Return>", lambda event: chat_with_ai())  # Enviar el mensaje al presionar Enter

btn_chat = tk.Button(frame_chat, text="Enviar", command=chat_with_ai)  # Botón para enviar el mensaje
btn_chat.pack(pady=5)

# **Sección de preguntas tipo test**
frame_test = tk.Frame(root)
question_label = tk.Label(frame_test, text="Pregunta:")  # Etiqueta para mostrar la pregunta
question_label.pack(pady=10)

option1_btn = tk.Button(frame_test, text="Opción 1", command=lambda: check_answer(option1_btn.cget("text")))
option1_btn.pack(pady=5)
option2_btn = tk.Button(frame_test, text="Opción 2", command=lambda: check_answer(option2_btn.cget("text")))
option2_btn.pack(pady=5)
option3_btn = tk.Button(frame_test, text="Opción 3", command=lambda: check_answer(option3_btn.cget("text")))
option3_btn.pack(pady=5)

result_label = tk.Label(frame_test, text="")  # Etiqueta para mostrar el resultado de la respuesta
result_label.pack(pady=10)

# Botón para generar preguntas después de importar el archivo
generate_test_question_button = tk.Button(frame_test, text="Generar Pregunta", command=generate_test_question, state=tk.DISABLED)
generate_test_question_button.pack(pady=10)

# Iniciar con la sección de ayuda visible
toggle_frame(frame_help)

# Iniciar la aplicación
correct_answer = tk.StringVar()  # Variable para almacenar la respuesta correcta

root.mainloop()  # Iniciar el bucle principal de la aplicación
