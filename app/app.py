from fastapi import FastAPI, UploadFile, File, Form
import xml.etree.ElementTree as ET
import re
import os
import json
import cairosvg
import fitz
import requests

app = FastAPI()

# Função para pegar cores válidas no formato HEX, RGB ou nomes de cores conhecidos
def extract_colors(style_string):
    color_regex = r'(#(?:[0-9a-fA-F]{3}){1,2}|rgb\(\s*\d{1,3}\s*,\s*\d{1,3}\s*,\s*\d{1,3}\s*\)|\b(?:red|blue|green|yellow|black|white|gray|grey|cyan|magenta|orange|pink|purple|brown)\b)'
    return re.findall(color_regex, style_string)

# Função para contar cores no SVG
def get_svg_colors(svg_file):
    tree = ET.parse(svg_file)
    root = tree.getroot()
    colors = []

    for elem in root.iter():
        style = elem.get('style')
        if style:
            colors.extend(extract_colors(style))

        fill = elem.get('fill')
        stroke = elem.get('stroke')
        
        if fill and fill != 'none':
            colors.append(fill)
        if stroke and stroke != 'none':
            colors.append(stroke)

    return list(set(colors))

# Função para substituir cores no SVG
def replace_svg_colors(svg_file, output_file, color_mapping):
    tree = ET.parse(svg_file)
    root = tree.getroot()
    substitution_details = []

    for elem in root.iter():
        style = elem.get('style')
        if style:
            new_style = style
            for old_color, new_color in color_mapping.items():
                if old_color in style:
                    substitution_details.append({"cor_encontrada": old_color, "cor_substituida": new_color})
                    new_style = re.sub(old_color, new_color, new_style)
            elem.set('style', new_style)

        fill = elem.get('fill')
        stroke = elem.get('stroke')

        if fill and fill in color_mapping:
            substitution_details.append({"cor_encontrada": fill, "cor_substituida": color_mapping[fill]})
            elem.set('fill', color_mapping[fill])
        if stroke and stroke in color_mapping:
            substitution_details.append({"cor_encontrada": stroke, "cor_substituida": color_mapping[stroke]})
            elem.set('stroke', color_mapping[stroke])

    tree.write(output_file)
    return substitution_details

# Função para converter PDF em SVG
def convert_pdf_to_svg(pdf_file_path, svg_output_path):
    pdf_document = fitz.open(pdf_file_path)
    svg_content = ""
    
    for page_num in range(len(pdf_document)):
        page = pdf_document.load_page(page_num)
        svg_content += page.get_svg_image()

    with open(svg_output_path, "w") as svg_file:
        svg_file.write(svg_content)

    pdf_document.close()

# Função para converter SVG para PNG
def convert_svg_to_png(svg_file_path, output_png_path):
    cairosvg.svg2png(url=svg_file_path, write_to=output_png_path, background_color=None)

# 1. Conta as cores no SVG (recebendo arquivo binário)
@app.post("/count-colors/")
async def count_colors(file: UploadFile = File(...)):
    file_location = f"temp_{file.filename}"
    
    with open(file_location, "wb+") as f:
        f.write(await file.read())
    
    unique_colors = get_svg_colors(file_location)
    
    os.remove(file_location)

    colors_response = {index + 1: color for index, color in enumerate(unique_colors)}

    return {
        "quantidade_de_cores": len(colors_response),
        "cores": colors_response
    }

# 2. Converte o PDF para SVG diretamente da URL
@app.post("/convert-pdf-to-svg/")
async def convert_pdf_to_svg_route(pdf_url: str = Form(...)):
    pdf_file_location = "temp_input.pdf"
    
    # Faz o download do PDF a partir da URL
    response = requests.get(pdf_url)
    with open(pdf_file_location, "wb") as f:
        f.write(response.content)
    
    svg_file_location = pdf_file_location.replace(".pdf", ".svg")

    convert_pdf_to_svg(pdf_file_location, svg_file_location)
    os.remove(pdf_file_location)

    return {"mensagem": "PDF convertido para SVG com sucesso", "svg_file_location": svg_file_location}

# 3. Substitui as cores no SVG (recebendo arquivo binário)
@app.post("/replace-svg-colors/")
async def replace_svg_colors_route(file: UploadFile = File(...), color_data: str = Form(...)):
    input_file = f"temp_{file.filename}"
    output_file = f"new_{file.filename}"

    with open(input_file, "wb+") as f:
        f.write(await file.read())

    color_data_dict = json.loads(color_data)
    color_mapping = {color['old']: color['new'] for color in color_data_dict['cores']}

    substitution_details = replace_svg_colors(input_file, output_file, color_mapping)
    
    os.remove(input_file)

    return {
        "mensagem": "Cores substituídas com sucesso",
        "substituicoes": substitution_details,
        "output_svg_file": output_file
    }

# 4. Converte o SVG final para PNG (recebendo arquivo binário)
@app.post("/convert-svg-to-png/")
async def convert_svg_to_png_route(file: UploadFile = File(...)):
    svg_file_location = f"temp_{file.filename}"
    
    with open(svg_file_location, "wb+") as f:
        f.write(await file.read())

    png_file_location = svg_file_location.replace(".svg", ".png")

    convert_svg_to_png(svg_file_location, png_file_location)
    os.remove(svg_file_location)

    return {
        "mensagem": "SVG convertido para PNG com sucesso",
        "png_file_location": png_file_location
    }
