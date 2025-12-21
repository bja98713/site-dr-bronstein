# Site du Dr. Jean-Ariel Bronstein (Django)

Reconstruction orientée patient du site docteur-bronstein-gastro.fr avec Django 6.0 : accueil patient, consultations/endoscopies, fiches pathologies, guides PDF, FAQ, index de symptômes et actualités.

## Prérequis
- Python 3.13

## Installation rapide
```sh
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Lancer en local
```sh
python manage.py runserver
```
Ouvrez http://127.0.0.1:8000/.

## Pages incluses
- Accueil patient avec parcours (Prendre RDV, Préparer examen, Conseils digestifs).
- Consultations & endoscopies (adresses, horaires, plans).
- Pathologies + fiches détaillées par symptômes.
- Guides pratiques avec liens PDF (placeholders à remplacer dans `static/docs/`).
- FAQ, index par symptômes, prise de rendez-vous dédiée.
- Actualités / blog statiques.

## Personnalisation rapide
- Mettre vos numéros / emails dans `CONTACT` (fichier `core/views.py`).
- Remplacer les PDFs dans `static/docs/` par vos documents officiels.
- Éditer/ajouter des fiches dans `PATHOLOGIES`, des guides dans `GUIDES`, des FAQs dans `FAQS`.
- Ajouter des articles dans `BLOG_POSTS`.

## Déploiement
- Définir `DJANGO_SECRET_KEY` et mettre `DEBUG=0`.
- `python manage.py collectstatic` puis servir via un serveur WSGI derrière un proxy (Nginx, Caddy, ...).
