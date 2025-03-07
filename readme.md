# Proyecto de Aplicación IA para Estudio y Generación de Preguntas

Este es un proyecto de una aplicación de escritorio diseñada con la interfaz gráfica de usuario (GUI) usando Tkinter. La aplicación interactúa con la API de Gemini AI para analizar documentos, generar resúmenes, responder preguntas y crear preguntas tipo test a partir de los documentos cargados.

## Funcionalidades Principales

1. Carga de Archivos: Permite abrir archivos de texto (.txt) y PDFs (.pdf). Los archivos PDF son procesados para extraer texto tanto del contenido legible como de las imágenes (mediante OCR).
2. Análisis de Texto: El texto extraído de los archivos se envía a la API de Gemini AI para generar un resumen o destacar los puntos clave.
3. Chat con la IA: Permite al usuario hacer preguntas sobre el documento cargado y obtener respuestas generadas por la IA, facilitando el estudio interactivo.
4. Generación de Preguntas de Examen: A partir del texto cargado, la IA genera preguntas tipo test con tres opciones y señala la respuesta correcta.

## Requisitos

* Python 3.8+
* Tkinter: Para crear la interfaz gráfica.
* Google Gemini API: Para análisis de texto y generación de respuestas (requiere una clave API).
* PyMuPDF: Para leer y procesar documentos PDF.
* Tesseract OCR: Para extraer texto de imágenes dentro de PDFs.

## Uso

### Menú Principal

La aplicación cuenta con un menú desplegable desde donde puedes acceder a las siguientes secciones:

1. ¿Cómo funciona?: Explicación sobre cómo usar la aplicación.
2. Importar Archivo: Cargar un archivo TXT o PDF y extraer su contenido.
3. Analizar Documento: Enviar el contenido del archivo a la IA para generar un resumen.
4. Chatear con Gemini: Realizar preguntas al modelo de IA sobre el documento.
5. Preguntas de Examen: Generar preguntas de opción múltiple basadas en el documento cargado.

### Interfaz

La interfaz de la aplicación está dividida en diferentes secciones:

1. Sección de Ayuda: Explicación sobre cómo funciona la aplicación.
2. Sección de Importar: Permite cargar archivos y ver su contenido extraído.
3. Sección de Análisis: Permite analizar el texto con la IA y generar un resumen.
4. Sección de Chat: Permite interactuar con la IA realizando preguntas sobre el contenido del documento.
5. Sección de Preguntas de Examen: Permite generar preguntas tipo test basadas en el contenido cargado.

### Funciones Importantes

1. Abrir Archivos: Al abrir un archivo, se extrae su contenido (textos de PDFs o TXT) y se muestra en un área de texto.      
2. Generar Resúmenes: Al analizar el texto, se utiliza Gemini AI para generar un resumen de los puntos clave.
3. Generar Preguntas de Examen: Después de analizar el texto, se puede generar una pregunta tipo test con tres opciones.
Interacción con la IA: Puedes enviar preguntas relacionadas con el contenido del documento y recibir respuestas generadas por la IA.
