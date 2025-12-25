import os
from pypdf import PdfReader
from django.conf import settings
from functools import lru_cache

@lru_cache(maxsize=1)
def load_pdf_content():
    """
    Charge le contenu des fichiers PDF situés dans le dossier rag_documents.
    Retourne une liste de dictionnaires formatés pour le chatbot.
    Utilise un cache pour ne pas relire les fichiers à chaque requête.
    """
    rag_dir = os.path.join(settings.BASE_DIR, 'static', 'rag_documents')
    documents = []

    if not os.path.exists(rag_dir):
        # Create directory if it doesn't exist (useful for dev)
        os.makedirs(rag_dir, exist_ok=True)
        return documents

    for filename in os.listdir(rag_dir):
        if filename.lower().endswith('.pdf'):
            file_path = os.path.join(rag_dir, filename)
            try:
                reader = PdfReader(file_path)
                text = ""
                for page in reader.pages:
                    text += page.extract_text() + "\n"
                
                # On combine le titre et le contenu pour la recherche
                searchable_text = f"{filename.replace('_', ' ').replace('.pdf', '')} {text}"

                documents.append({
                    'type': 'document_pdf',
                    'title': filename,
                    'url': f"{settings.STATIC_URL}rag_documents/{filename}", 
                    'content': text, # Gardé pour affichage éventuel
                    'keywords': searchable_text # Utilisé par views.py pour la recherche
                })
            except Exception as e:
                print(f"Erreur lors de la lecture de {filename}: {e}")

    return documents
