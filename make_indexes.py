#!/usr/bin/env python3

# This script browses an MkDocs source directory to generate an index 
# for each subdirectory that has been listed in MkDocs config under `sections` entry

import re
import os
import yaml
import shutil
from pathlib import Path

# installed packages :
import yamldown
import markdown


# Function to get metadata (title and description) from files
def get_meta(file):

  # By default, set the title to filename without extension
  title = Path(file).stem.capitalize()

  # 1. Try to read title from “frontmatter” (= yaml introduction of markdown file)
  md = open(file.path, "r", encoding="utf-8")
  yml, omd = yamldown.load(md)
  if yml is not None:
    title = yml.get('title')
  
  # 2. No yaml config for file, try to read the first H1 
  else:
    # transform markdown to html
    with open(file.path, "r", encoding="utf-8") as md:
      html = markdown.markdown(md.read())
      # find all <h1>
      h1s = re.findall('<h1>(.*?)</h1>', html)
      if h1s:
        title = h1s[0]
  
  return title


# Main function
def main():
    
  with open('./mkdocs.yml', 'r') as config_file:
    # read info from MkDocs config file
    conf = yaml.safe_load(config_file)
    # if docs_dir has been set, else "docs"
    docs_dir = conf.get('docs_dir', 'docs')
    sections = conf.get('sections', None)
  
  if not sections:
    raise ValueError("Error: you should setup a sections list in mkdocs.yml, mirroring your subfolders list")
  
  # scans source directory for subdirectories
  with os.scandir(docs_dir) as entries:
    for entry in entries:
      
      # If entry is a directory and dirname is in config.sections
      if entry.is_dir() and entry.name in sections.keys() :

        # Get title from config
        section = sections.get(entry.name)

        # Build markdown content (\n is a line break)
        md_content = f"# {section}\n\n"

        with os.scandir(entry) as files:
          for file in files:
            if file.name.endswith('md') and not file.name == "index.md":
              title = get_meta(file)
              md_content += f"- [{title}]({file.name})\n"

        # Write index.md file in dir
        with open(os.path.join(entry, 'index.md'), "w") as f:
          f.write(md_content)

# The variable __name__ tells which context this file is running in.
if __name__ == '__main__':
  main()
