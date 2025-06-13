import os
import sys
import tempfile
import atexit
import shutil
import time
from pathlib import Path

src_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '5.Codebase'))
sys.path.insert(0, src_path)
sys.path.insert(0, os.path.join(src_path, 'src'))

# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'Property Tycoon V1.0 Documentation'
copyright = '2025, Software Engineering Project Group 5 Eric Shi, Stuart Baker, Lin Moe Hein, Duncan Law, Owen Chen'
author = 'Eric Shi, Stuart Baker, Lin Moe Hein, Duncan Law, Owen Chen.'

version = 'V1.0'
release = 'V1.0'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.viewcode',
    'sphinx.ext.todo',
    'sphinx.ext.graphviz',
    'sphinxcontrib.plantuml',
]

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# PlantUML configuration
plantuml = f'java -jar "{os.path.abspath("plantuml.jar")}"'
plantuml_output_format = 'png'

# Ensure the output directory exists
plantuml_output_dir = os.path.join('_build', 'html', '_images')
os.makedirs(plantuml_output_dir, exist_ok=True)

# Set environment variables for PlantUML
os.environ['PLANTUML_LIMIT_SIZE'] = '8192'
os.environ['JAVA_OPTS'] = '-Djava.awt.headless=true -Dfile.encoding=UTF-8'

def safe_cleanup():
    try:
        if os.path.exists(plantuml_output_dir):
            time.sleep(1)
            shutil.rmtree(plantuml_output_dir)
    except Exception as e:
        print(f"Warning: Could not clean up {plantuml_output_dir}: {e}")
atexit.register(safe_cleanup)

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']

html_theme_options = {
    'navigation_depth': 4,  
    'collapse_navigation': True, 
    'sticky_navigation': True,  
    'includehidden': True,  
    'titles_only': False     
}

# -- Extension configuration -------------------------------------------------

on_windows = os.name == 'nt'

if on_windows:
    plantuml = 'java -jar "' + os.path.abspath('plantuml.jar') + '" -Djava.awt.headless=true'
else:
    plantuml = 'plantuml'

plantuml_output_format = 'png'
os.environ['PLANTUML_LIMIT_SIZE'] = '8192'  # Increase size limit for large diagrams

# Configure temp directory for PlantUML
# os.environ['PLANTUML_TEMP_PATH'] = plantuml_output_dir

graphviz_output_format = 'png'  
if on_windows:
    graphviz_dot = r'C:\Program Files\Graphviz\bin\dot.exe'
