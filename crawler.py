import requests
from bs4 import BeautifulSoup
import os
from time import sleep

# URLs of the main page with the information of the funds
brochures_url = 'https://www.cnmv.es/portal/consultas/mostrarlistados.aspx?id=3&lang=es&page='
cnmv_url = 'https://www.cnmv.es/portal/consultas/'

# Folder to store the donwloaded PDFs
download_dir = '/Users/egi/tmp/FinGuruDocs/test'

# Number of pages to analyze
total_pages = 133


def get_brochures(url):

    # GET the page
    response = requests.get(url)

    # Verify if the page exists and is reacheable
    if response.status_code == 200:
        print("Received 200 OK from the page")
        # Parsear el contenido HTML de la página
        soup = BeautifulSoup(response.text, 'html.parser')

        # Encontrar todos los enlaces en la página que contienen 'iic/fondo.aspx?nif='
        links = soup.find_all('a', href=lambda href: href and 'iic/fondo.aspx?nif=' in href)

        # Iterar sobre los enlaces encontrados
        print("Encontrados " + str(len(links)) + " enlaces")
        for link in links:

            sleep(1)
            
            # Obtener el atributo 'href' de cada enlace
            href = link.get('href')

            # Obtener el titulo del enlace, que será el nombre del fondo
            pdf_name = link.get('title')[:-3].replace("/","-")
            if pdf_name[-1] == ',':
                pdf_name = pdf_name[:-1]
            pdf_name = pdf_name + ".pdf"

            # Construir la URL completa del enlace
            full_link = cnmv_url + href
            # Hacer una solicitud GET a la página del enlace
            link_response = requests.get(full_link)
            # Verificar si la solicitud fue exitosa
            if link_response.status_code == 200:
                # Encontrar el enlace al folleto del fondo en la página específica del fondo. Será e
                pdf_link = BeautifulSoup(link_response.text, 'html.parser').find('a', href=lambda href: href and 'verdocumento/ver' in href)
                # Si se encuentra el enlace al PDF
                if pdf_link:
                    # Obtener la URL completa del archivo PDF
                    pdf_url = pdf_link.get('href')
                
                    # Guardar el archivo PDF en el directorio de descarga
                    with open(os.path.join(download_dir, pdf_name), 'wb') as f:
                        pdf_response = requests.get(pdf_url)
                        f.write(pdf_response.content)
                        print(f"Descargado: {pdf_name}")
                        
            else:
                print("Error al cargar la página del enlace:", full_link)
            
    else:
        print("Error al cargar la página principal:", response.status_code)

def main():
    # Create folder 
    if not os.path.exists(download_dir):
        os.makedirs(download_dir) 

    # Go through all the pages to download all tha brochures
    for i in range(38,total_pages+1):
        url_to_process = brochures_url + str(i)
        get_brochures(url_to_process)


if __name__ == '__main__':
    main()
