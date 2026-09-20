AUTHOR = "L'Équipe"
SITENAME = "Outils IA Radar"
SITESUBTITLE = "Les meilleurs outils d'Intelligence Artificielle"
SITELOGO = "https://cdn-icons-png.flaticon.com/512/2814/2814666.png" # Icône IA libre de droits
SITEURL = ''

PATH = 'content'

TIMEZONE = 'Europe/Paris'

DEFAULT_LANG = 'fr'

# Theme settings
THEME = 'themes/Flex'

# Feed generation is usually not desired when developing
FEED_ALL_ATOM = None
CATEGORY_FEED_ATOM = None
TRANSLATION_FEED_ATOM = None
AUTHOR_FEED_ATOM = None
AUTHOR_FEED_RSS = None

# Blogroll (Liens de la barre latérale)
LINKS = (('Outils Business', 'https://M0ebius0ne.github.io/outils-business/'),)

# Social widget
SOCIAL = ()

# SEO Clean URLs
ARTICLE_URL = '{slug}/'
ARTICLE_SAVE_AS = '{slug}/index.html'
PAGE_URL = 'pages/{slug}/'
PAGE_SAVE_AS = 'pages/{slug}/index.html'
CATEGORY_URL = 'category/{slug}/'
CATEGORY_SAVE_AS = 'category/{slug}/index.html'
TAG_URL = 'tag/{slug}/'
TAG_SAVE_AS = 'tag/{slug}/index.html'

DEFAULT_PAGINATION = 10

# Uncomment following line if you want document-relative URLs when developing
#RELATIVE_URLS = True

# Compteur de visites (GoatCounter, gratuit). Laisser vide tant que le compte n'existe pas.
# Exemple : GOATCOUNTER_SITE = "outils-ia"
GOATCOUNTER_SITE = "moebiusone"
