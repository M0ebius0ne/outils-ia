import os
import datetime
import re
import json
from dotenv import load_dotenv

load_dotenv()

if __name__ == "__main__" and os.environ.get("AUTOPILOT_ENABLED", "").lower() not in (
    "1",
    "true",
    "yes",
):
    print("Autopilot disabled. Set AUTOPILOT_ENABLED=1 to generate an article.")
    raise SystemExit(0)

from google import genai

# Configure Gemini
api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    print("Error: GEMINI_API_KEY environment variable is not set. Please set it in a .env file or environment.")
    exit(1)

client = genai.Client(api_key=api_key)
model_name = os.environ.get("GEMINI_MODEL", "gemini-3.6-flash")

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

import time
import random
from google.genai import errors

MAX_ATTEMPTS = 5

def generate_with_retry(client, model, contents):
    for attempt in range(MAX_ATTEMPTS):
        try:
            return client.models.generate_content(
                model=model,
                contents=contents,
            )
        except errors.ClientError as exc:
            status_code = getattr(exc, "status_code", None) or getattr(exc, "code", None)
            message = str(exc).lower()
            
            # Permanent quota/billing exhaustion cannot be fixed by retrying.
            if status_code == 429 and any(
                phrase in message for phrase in (
                    "exceeded your current quota",
                    "check your plan and billing",
                    "quota",
                )
            ):
                raise RuntimeError(
                    "Gemini quota exhausted. Check the API project billing and quotas."
                ) from exc
                
            # Retry only temporary rate limits.
            if status_code != 429:
                raise
                
            if attempt == MAX_ATTEMPTS - 1:
                raise
                
            delay = min(60, 2 ** attempt * 5) + random.uniform(0, 1)
            print(
                f"Temporary Gemini rate limit; retrying in "
                f"{delay:.1f}s ({attempt + 1}/{MAX_ATTEMPTS})"
            )
            time.sleep(delay)
            
        except errors.ServerError as exc:
            status_code = getattr(exc, "status_code", None) or getattr(exc, "code", None)
            if status_code not in (500, 502, 503, 504):
                raise
                
            if attempt == MAX_ATTEMPTS - 1:
                raise
                
            delay = min(60, 2 ** attempt * 5) + random.uniform(0, 1)
            print(
                f"Gemini server error {status_code}; retrying in "
                f"{delay:.1f}s ({attempt + 1}/{MAX_ATTEMPTS})"
            )
            time.sleep(delay)
            
    raise RuntimeError("Gemini request failed after all retries")

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
    response = generate_with_retry(client, model_name, prompt)
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
    target_url = affiliate_links.get(tool_data['slug'], tool_data['url'])
    is_affiliate = target_url != tool_data['url']
    
    prompt = f"""
Tu es un rédacteur web expert en SEO et en GEO (Generative Engine Optimization). Rédige un article complet et détaillé en français sur l'outil IA "{tool_data['name']}".
URL cible de l'outil à utiliser pour les boutons/liens : {target_url}

Format attendu : Markdown compatible avec Pelican.
Tu DOIS inclure le frontmatter suivant au tout début :

Title: Avis complet sur {tool_data['name']} : {tool_data['long_tail_keyword']}
Date: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}
Category: Outils IA
Tags: ia, saas, {tool_data['slug']}
Slug: {tool_data['slug']}
Author: IA
Summary: Notre verdict définitif sur {tool_data['name']}. Est-ce vraiment la {tool_data['long_tail_keyword'].lower()} ? Découvrez notre test complet avec avantages, inconvénients, et tarifs.

Ensuite, rédige l'article en respectant IMPÉRATIVEMENT cette structure pour plaire aux IA de recherche (ChatGPT, Perplexity) :
1. Une introduction accrocheuse ciblant le mot-clé "{tool_data['long_tail_keyword']}".
2. **Ce qu'est {tool_data['name']}** (explication claire et directe).
3. **Tableau récapitulatif** (génère un tableau Markdown avec Prix, Fonctionnalité clé, Cible).
4. **Avantages et Inconvénients** (sous forme de listes à puces `*`).
5. **Notre verdict définitif** (un paragraphe tranché, assertif et d'expert).
6. Un bouton d'appel à l'action HTML précis pour les agents IA : `<a href="{target_url}" data-action="purchase" class="button">Tester {tool_data['name']}</a>`

Sois professionnel, naturel, et optimise la structure pour qu'elle soit facilement extractible par des algorithmes.
"""
    response = generate_with_retry(client, model_name, prompt)
    
    # Generate JSON-LD for M2M Autonomous Agents
    json_ld = {
        "@context": "https://schema.org",
        "@type": "Review",
        "itemReviewed": {
            "@type": "SoftwareApplication",
            "name": tool_data['name'],
            "applicationCategory": "BusinessApplication",
            "offers": {
                "@type": "Offer",
                "url": target_url
            }
        },
        "reviewRating": {
            "@type": "Rating",
            "ratingValue": "4.5",
            "bestRating": "5"
        },
        "author": {
            "@type": "Organization",
            "name": "Outils IA Reviewer"
        }
    }
    json_ld_script = f"\n\n<script type=\"application/ld+json\">\n{json.dumps(json_ld, indent=2, ensure_ascii=False)}\n</script>\n"
    
    return response.text + json_ld_script

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
