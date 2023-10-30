#!/usr/bin/env python3

# Ce script (à visée pédagogique :) permet de “scraper” les liens contenus dans la page 
# consacrée aux films de Samuel Beckett sur UbuWeb. Il récupère le titre de chaque page, 
# son contenu textuel et écrit un fichier markdown dans un dossier.

import os

# Paquets installés grâce à : 
# pip install requests beautifulsoup4 python-slugify markdownify  
import requests # Pour faire des requêtes HTTP
from bs4 import BeautifulSoup # puissante librairie de lecture / écriture de HTML
from slugify import slugify # pour transformer des chaînes de caractères en “slugs” (sans accents, espaces, caractères spéciaux)
from markdownify import markdownify as html_to_markdown # Pour transformer du HTML en markdown

# Chaines de caractères à supprimer dans les titres des pages
# Chaque chaîne est suivie de ce par quoi on veut la remplacer
replacements = {
  "UbuWeb Film & Video: Samuel Beckett -": "", 
  "UbuWeb Film &amp; Video:": "", 
  "U B U W E B :: ": "",
  "'": "’", # remplacement des guillemets simples par une apostrophe
  '"':"'" # remplacement des guillemets doubles par un guillemet simple
}

# Main function
def main():

  ubu = "https://ubu.com/film/beckett.html"
  beckett = requests.get(ubu)

  # Parser le document HTML BeautifulSoup obtenu à partir du code source
  beckett_html = BeautifulSoup(beckett.text, 'html.parser')

  # Récupérer tous les liens à l’intérieur du 2e élément <td class="default">
  default = beckett_html.find_all('td', class_="default")[1]
  links = default.find_all('a')

  # index pour préfixer le nom des fichiers (et maintenir l’ordre des pages)
  index = 0
  
  # Parcourt chaque lien pour récupérer son contenu
  for link in links:
    index += 1
    href = link['href']
    # modification de l’URL pour les liens relatifs (on enlève "becket.html")
    url = ubu.replace("beckett.html", "") + href
    page = requests.get(url)
    # Si la page produit une erreur 404, on continue à la page suivante
    if page.status_code == 404:
      continue
    # Sinon, on esaie de lire le contenu de la page
    html = BeautifulSoup(page.text, 'html.parser')
    title = html.title.text

    # On nettoie les titres
    for s, replacement in replacements.items():
      title = title.replace(s, replacement).strip()

    # Feedback utilisateur !
    print(f"Processing {index}/{len(links)}: {title}")
    
    # On lit la description (dans le <div id="ubudesc">)
    desc = html.find(id="ubudesc")
    # On lit l’éventuel lien vers une vidéo (dans le <a id="moviename">)
    moviename = html.find(id="moviename")
    # Si on a trouvé une description…
    if desc:
      # Entête du fichier markdown
      md_content = "---\n"
      md_content += f'title: "{title}"\n'
      md_content += "---\n\n"
      # Contenu du fichier markdown : h1
      md_content += f"# {title}\n\n"
      # Contenu du fichier markdown : vidéo éventuelle
      if moviename:
        md_content += f"<video controls src='{ moviename['href'].replace('../media', 'https://ubu.com/media') }'></video>\n\n"
      # Contenu du fichier markdown : contenu textuel
      md_content += html_to_markdown(desc.text)
      # Contenu du fichier markdown : lien vers la source
      md_content += f"\n\n[Voir sur UbuWeb]({url})"

      # On détermine le nom du fichier 
      prefix = str(index).zfill(2) # pour avoir "01" plutôt que "1"
      slug = slugify(title) # pour avoir "comedie-1966" plutôt que "Comédie (1966)"
      filename = f'{prefix}-{slug}.md'

      # On écrit le fichier dans le dossier "content/films"
      with open(os.path.join("content/films", filename), "w") as f:
        f.write(md_content)
     

# The variable __name__ tells which context this file is running in.
if __name__ == '__main__':
  main()
