import tkinter as tk
from tkinter import filedialog, scrolledtext
import google.generativeai as genai
import fitz  # PyMuPDF para leer PDFs
import pytesseract
from PIL import Image
import io

gemini_api_key = "AIzaSyDygrN4dfBjdXrdfvpe55cAMgpFRCC-2hQ"
genai.configure(api_key=gemini_api_key)
pytesseract.pytesseract.tesseract_cmd = "C:/Program Files/Tesseract-OCR/tesseract.exe"

def extract_text_from_pdf(pdf_path):
    """Extrae texto de un archivo PDF, incluyendo imágenes con texto."""
    text = ""
    try:
        with fitz.open(pdf_path) as doc:
            for page in doc:
                text += page.get_text("text") + "\n"
                for img_index, img in enumerate(page.get_images(full=True)):
                    xref = img[0]
                    base_image = doc.extract_image(xref)
                    image_data = base_image["image"]
                    image = Image.open(io.BytesIO(image_data))
                    text += pytesseract.image_to_string(image) + "\n"
    except Exception as e:
        text = f"Error al leer el PDF: {e}"
    return text

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

def open_file():
    """Abre un archivo TXT o PDF y extrae su contenido."""
    global document_text
    file_path = filedialog.askopenfilename(filetypes=[("Archivos TXT", "*.txt"), ("Archivos PDF", "*.pdf")])
    if not file_path:
        return
    
    if file_path.endswith(".txt"):
        with open(file_path, "r", encoding="utf-8") as file:
            document_text = file.read()
    elif file_path.endswith(".pdf"):
        document_text = extract_text_from_pdf(file_path)
    else:
        document_text = "Formato no compatible."
    
    text_area.delete("1.0", tk.END)
    text_area.insert(tk.END, document_text)

    # Generar la primera pregunta de test
    question_label.config(text="Pregunta:")
    option1_btn.config(text="Opción A")
    option2_btn.config(text="Opción B")
    option3_btn.config(text="Opción C")
    result_label.config(text="")
    generate_test_question_button.config(state=tk.NORMAL)

def analyze_text():
    """Envía el texto a Gemini AI para obtener un resumen."""
    if not document_text:
        result_area.delete("1.0", tk.END)
        result_area.insert(tk.END, "No hay texto para analizar.")
        return
    
    try:
        model = genai.GenerativeModel(model_name="gemini-2.0-flash-lite")
        response = model.generate_content(f"Resume y destaca los puntos clave: {document_text}")
        summary = response.text if response.text else "No se pudo generar el resumen."
    except Exception as e:
        summary = f"Error en la consulta a Gemini: {e}"
    
    result_area.delete("1.0", tk.END)
    result_area.insert(tk.END, summary)

def chat_with_ai():
    """Envía preguntas a Gemini AI con el contexto del documento cargado."""
    user_query = chat_entry.get().strip()
    if not user_query:
        return
    
    try:
        model = genai.GenerativeModel(model_name="gemini-2.0-flash-lite")
        response = model.generate_content(f"Basado en este documento: {document_text}\nPregunta: {user_query}")
        answer = response.text if response.text else "No se pudo generar una respuesta."
    except Exception as e:
        answer = f"Error en la consulta a Gemini: {e}"
    
    chat_area.config(state=tk.NORMAL)  # Habilitar para mostrar texto
    chat_area.insert(tk.END, f"Tú: {user_query}\nGemini: {answer}\n\n")
    chat_area.config(state=tk.DISABLED)  # Deshabilitar para no permitir escritura
    chat_entry.delete(0, tk.END)

def generate_test_question():
    """Genera una pregunta de tipo test basada en el documento importado."""
    if not document_text:
        question_label.config(text="No hay documento cargado.")
        return

    try:
        model = genai.GenerativeModel(model_name="gemini-2.0-flash-lite")
        # Genera una pregunta basada en el contenido del documento
        response = model.generate_content(f"Genera una pregunta tipo test con 3 opciones basada en el siguiente texto: {document_text}, no generarás ningun texto adicional ya que tu primera línea será la pregunta, las 3 siguientes líneas las copciones y la quinta ultima línea sera una copia exacta de la respuesta correcta.")
        question_data = response.text.strip().split("\n")
        
        # Validación para asegurar que se reciban las preguntas y respuestas correctamente
        if len(question_data) < 4:
            question_label.config(text="No se pudo generar una pregunta adecuada.")
            return
        
        question = question_data[0]  # Primera línea: la pregunta
        options = question_data[2:5]  # Las siguientes tres líneas luego de un intro: las opciones
        correct_option = question_data[6]  # La septima línea: la respuesta correcta

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

def check_answer(selected_option):
    """Comprueba si la respuesta seleccionada es correcta."""
    if selected_option == correct_answer.get():
        result_label.config(text="¡Correcto!", fg="green")
    else:
        result_label.config(text=f"Incorrecto. La respuesta correcta era: {correct_answer.get()}", fg="red")
    
    # Generar una nueva pregunta después de responder
    generate_test_question()

# Crear la interfaz gráfica
root = tk.Tk()
root.title("Bot IA de estudio")

# Iniciar la ventana a tamaño completo
root.state('zoomed')

document_text = ""

# Menú desplegable en la esquina superior derecha
menu_bar = tk.Menu(root)
root.config(menu=menu_bar)

app_menu = tk.Menu(menu_bar, tearoff=0)
menu_bar.add_cascade(label="Menú", menu=app_menu)

def show_help():
    toggle_frame(frame_help)

def show_import():
    toggle_frame(frame_import)

def show_analyze():
    toggle_frame(frame_analyze)

def show_chat():
    toggle_frame(frame_chat)

def show_test():
    toggle_frame(frame_test)

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
btn_open = tk.Button(frame_import, text="Abrir archivo", command=open_file)
btn_open.pack(pady=10)
text_area = scrolledtext.ScrolledText(frame_import, wrap=tk.WORD, height=10)
text_area.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)

# **Sección de análisis**
frame_analyze = tk.Frame(root)
btn_analyze = tk.Button(frame_analyze, text="Analizar con Gemini", command=analyze_text)
btn_analyze.pack(pady=10)
result_area = scrolledtext.ScrolledText(frame_analyze, wrap=tk.WORD, height=5)
result_area.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)

# **Sección de chat**
frame_chat = tk.Frame(root)
chat_label = tk.Label(frame_chat, text="Chatea con Gemini")
chat_label.pack(pady=5)
chat_area = scrolledtext.ScrolledText(frame_chat, wrap=tk.WORD, height=10)
chat_area.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)
chat_area.config(state=tk.DISABLED)  # Deshabilitar el cuadro de texto para que no sea editable
chat_entry = tk.Entry(frame_chat, width=50)
chat_entry.pack(pady=5)

# **Evento para presionar Enter y enviar el mensaje**
chat_entry.bind("<Return>", lambda event: chat_with_ai())

btn_chat = tk.Button(frame_chat, text="Enviar", command=chat_with_ai)
btn_chat.pack(pady=5)

# **Sección de preguntas tipo test**
frame_test = tk.Frame(root)
question_label = tk.Label(frame_test, text="Pregunta:")
question_label.pack(pady=10)

option1_btn = tk.Button(frame_test, text="Opción 1", command=lambda: check_answer(option1_btn.cget("text")))
option1_btn.pack(pady=5)
option2_btn = tk.Button(frame_test, text="Opción 2", command=lambda: check_answer(option2_btn.cget("text")))
option2_btn.pack(pady=5)
option3_btn = tk.Button(frame_test, text="Opción 3", command=lambda: check_answer(option3_btn.cget("text")))
option3_btn.pack(pady=5)

result_label = tk.Label(frame_test, text="")
result_label.pack(pady=10)

# Botón para generar preguntas después de importar el archivo
generate_test_question_button = tk.Button(frame_test, text="Generar Pregunta", command=generate_test_question, state=tk.DISABLED)
generate_test_question_button.pack(pady=10)

# Iniciar con la sección de ayuda visible
toggle_frame(frame_help)

# Iniciar la aplicación
correct_answer = tk.StringVar()

root.mainloop()