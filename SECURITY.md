# Politique de sécurité

## Signaler une vulnérabilité

Si vous découvrez une vulnérabilité de sécurité, merci de nous la signaler par email plutôt que d'ouvrir une issue publique.

**Ne commitez pas** de clés API, mots de passe ou secrets dans le dépôt. Utilisez `.env` (voir `.env.example`) pour la configuration locale — ce fichier est ignoré par Git.

## Bonnes pratiques

- Ne jamais exposer `GROQ_API_KEY` ou autres clés dans le code
- En production : restreindre `CORS_ORIGINS`, désactiver `DEBUG`, utiliser HTTPS
