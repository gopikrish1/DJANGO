import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from rest_framework.test import APIClient
from documents.models import Document
import json

doc = Document.objects.get(id=6)
user = doc.user

client = APIClient()
client.force_authenticate(user=user)

print('--- Ingesting Document ---')
res1 = client.post('/api/documents/ingest-doc/', {'document_id': 6}, format='json')
print(json.dumps(res1.json(), indent=2))

print('\n--- Querying RAG ---')
res2 = client.post('/api/rag-query/', {'question': 'Who are the main characters in the stories?'}, format='json')
print(json.dumps(res2.json(), indent=2))
