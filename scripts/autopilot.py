import os
import datetime
import re
import json
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure Gemini
api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    print("Error: GEMINI_API_KEY environment variable is not set. Please set it in a .env file or environment.")
    exit(1)

genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-3.6-flash')

def get_existing_articles():
    content_dir = os.path.join(os.path.dirname(__file__), '..', 'website', 'content')
    existing = []
    if os.path.exists(content_dir):
        for filename in os.listdir(content_dir):
            if filename.endswith(".md"):
                existing.append(filename.replace(".md", "").lower())
    return existing

def load_affiliate_links():
    links_file = os.path.join(os.path.dirname(__file__), 'affiliate_links.json')
    if os.path.exists(links_file):
        with open(links_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def generate_article_idea(existing_articles):
    prompt = f"""
Tu es un expert en outils d'intelligence artificielle et en stratégie de référencement SEO "Longue Traîne" (Long-Tail).
Je veux écrire un article de blog SEO qui présente un outil IA très utile mais DE NICHE ou TRÈS RÉCENT.
L'outil doit être réel, mais ne choisis SURTOUT PAS d'outils grand public comme ChatGPT, Midjourney, Notion ou Canva.
Trouve un outil très spécifique (ex: une IA pour les architectes, un générateur de voix pour podcasters, une IA d'analyse juridique, etc) qui a probablement un programme d'affiliation public.
Voici les articles déjà publiés (n'utilise PAS ces outils) : {', '.join(existing_articles) if existing_articles else 'Aucun'}.

Renvoie UNIQUEMENT un objet JSON valide avec les clés suivantes :
- "name": le nom de l'outil
- "slug": un identifiant url-friendly (ex: "nom-outil-ia-architectes")
- "url": l'url officielle de l'outil
- "description": une brève description de ce que fait l'outil
- "long_tail_keyword": un mot clé de longue traîne très spécifique pour lequel on veut ranker (ex: "Meilleure IA pour générer des plans d'architecture")
"""
    response = model.generate_content(prompt)
    try:
        # Extract json block if wrapped in markdown
        text = response.text
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0]
        elif "```" in text:
            text = text.split("```")[1].split("```")[0]
        data = json.loads(text.strip())
        return data
    except Exception as e:
        print(f"Failed to parse JSON idea: {e}\nResponse was: {response.text}")
        exit(1)

def write_article(tool_data, affiliate_links):
    # On vérifie si on a un lien d'affiliation pour cet outil précis, sinon on utilise l'URL officielle
    target_url = affiliate_links.get(tool_data['slug'], tool_data['url'])
    is_affiliate = target_url != tool_data['url']
    
    prompt = f"""
Tu es un rédacteur web expert en SEO. Rédige un article complet et détaillé en français sur l'outil IA "{tool_data['name']}".
Le but est d'informer le lecteur, de donner un avis objectif et de l'inciter à cliquer sur le lien vers l'outil.
URL cible de l'outil à utiliser pour les boutons/liens : {target_url}

Format attendu : Markdown compatible avec Pelican.
Tu DOIS inclure le frontmatter (l'en-tête metadata) suivant au tout début du fichier :

Title: Avis complet sur {tool_data['name']} : {tool_data['long_tail_keyword']}
Date: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}
Category: Outils IA
Tags: ia, saas, {tool_data['slug']}
Slug: {tool_data['slug']}
Author: IA
Summary: Découvrez notre avis complet sur {tool_data['name']}. Est-ce vraiment la {tool_data['long_tail_keyword'].lower()} ? Avantages, inconvénients, et tarifs.

Ensuite, rédige l'article avec la structure suivante :
- Une introduction accrocheuse qui cible le mot-clé "{tool_data['long_tail_keyword']}"
- Ce qu'est {tool_data['name']} et à qui ça s'adresse
- Les fonctionnalités principales
- Les avantages et inconvénients (sois honnête et objectif)
- Les tarifs
- Notre avis final
- Un bouton d'appel à l'action clair (lien Markdown) : "Tester {tool_data['name']}" pointant vers {target_url}

Sois professionnel, naturel, et optimise pour le mot-clé "{tool_data['long_tail_keyword']}".
"""
    response = model.generate_content(prompt)
    return response.text

def main():
    print("Démarrage de l'autopilote...")
    existing = get_existing_articles()
    print(f"Articles existants : {len(existing)}")
    
    affiliate_links = load_affiliate_links()
    
    idea = generate_article_idea(existing)
    print(f"Outil choisi : {idea['name']}")
    
    article_content = write_article(idea, affiliate_links)
    
    # Save the file
    content_dir = os.path.join(os.path.dirname(__file__), '..', 'website', 'content')
    os.makedirs(content_dir, exist_ok=True)
    
    file_path = os.path.join(content_dir, f"{idea['slug']}.md")
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(article_content)
        
    print(f"Article généré et sauvegardé dans {file_path}")

if __name__ == "__main__":
    main()
