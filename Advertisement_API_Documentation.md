# API Documentation - Gestion des Publicités

## Vue d'ensemble

L'API de gestion des publicités permet aux administrateurs de créer, modifier, supprimer et gérer les publicités affichées dans l'application mobile. Un maximum de 3 publicités actives est autorisé simultanément.

## Endpoints

### 1. Liste des publicités (Admin seulement)

**GET** `/advertisement/`

Récupère toutes les publicités (actives et inactives).

**Headers requis:**
```
Authorization: Bearer <jwt_token>
```

**Réponse:**
```json
{
  "count": 2,
  "advertisements": [
    {
      "id": 1,
      "title": "Promotion spéciale",
      "description": "Découvrez nos offres exceptionnelles",
      "image_url": "https://example.com/image.jpg",
      "country": "France",
      "is_active": true,
      "created_at": "2024-01-15T10:30:00",
      "updated_at": "2024-01-15T10:30:00",
      "created_by": 1
    }
  ]
}
```

### 2. Créer une publicité (Admin seulement)

**POST** `/advertisement/`

Crée une nouvelle publicité.

**Headers requis:**
```
Authorization: Bearer <jwt_token>
Content-Type: application/json
```

**Body:**
```json
{
  "title": "Nouvelle promotion",
  "description": "Description de la promotion",
  "image_url": "https://example.com/image.jpg",
  "country": "France",
  "is_active": true
}
```

**Champs:**
- `title` (requis): Titre de la publicité
- `description` (requis): Description de la publicité
- `image_url` (requis): URL de l'image
- `country` (optionnel): Pays cible (null pour tous les pays)
- `is_active` (optionnel): Statut actif (défaut: true)

**Réponse:**
```json
{
  "id": 2,
  "title": "Nouvelle promotion",
  "description": "Description de la promotion",
  "image_url": "https://example.com/image.jpg",
  "country": "France",
  "is_active": true,
  "created_at": "2024-01-15T11:00:00",
  "updated_at": "2024-01-15T11:00:00",
  "created_by": 1
}
```

### 3. Récupérer une publicité (Admin seulement)

**GET** `/advertisement/{id}`

Récupère une publicité spécifique.

**Headers requis:**
```
Authorization: Bearer <jwt_token>
```

**Réponse:**
```json
{
  "id": 1,
  "title": "Promotion spéciale",
  "description": "Découvrez nos offres exceptionnelles",
  "image_url": "https://example.com/image.jpg",
  "country": "France",
  "is_active": true,
  "created_at": "2024-01-15T10:30:00",
  "updated_at": "2024-01-15T10:30:00",
  "created_by": 1
}
```

### 4. Modifier une publicité (Admin seulement)

**PUT** `/advertisement/{id}`

Modifie une publicité existante.

**Headers requis:**
```
Authorization: Bearer <jwt_token>
Content-Type: application/json
```

**Body:**
```json
{
  "title": "Titre modifié",
  "description": "Description modifiée",
  "is_active": false
}
```

**Réponse:**
```json
{
  "id": 1,
  "title": "Titre modifié",
  "description": "Description modifiée",
  "image_url": "https://example.com/image.jpg",
  "country": "France",
  "is_active": false,
  "created_at": "2024-01-15T10:30:00",
  "updated_at": "2024-01-15T12:00:00",
  "created_by": 1
}
```

### 5. Supprimer une publicité (Admin seulement)

**DELETE** `/advertisement/{id}`

Supprime une publicité.

**Headers requis:**
```
Authorization: Bearer <jwt_token>
```

**Réponse:**
```json
{
  "message": "Publicité supprimée avec succès"
}
```

### 6. Activer/Désactiver une publicité (Admin seulement)

**POST** `/advertisement/toggle/{id}`

Bascule le statut actif/inactif d'une publicité.

**Headers requis:**
```
Authorization: Bearer <jwt_token>
```

**Réponse:**
```json
{
  "id": 1,
  "title": "Promotion spéciale",
  "description": "Découvrez nos offres exceptionnelles",
  "image_url": "https://example.com/image.jpg",
  "country": "France",
  "is_active": false,
  "created_at": "2024-01-15T10:30:00",
  "updated_at": "2024-01-15T12:30:00",
  "created_by": 1
}
```

### 7. Publicités actives (Application mobile)

**GET** `/advertisement/active`

Récupère les publicités actives pour l'application mobile (maximum 3).

**Réponse:**
```json
[
  {
    "id": 1,
    "title": "Promotion spéciale",
    "description": "Découvrez nos offres exceptionnelles",
    "image_url": "https://example.com/image.jpg",
    "country": "France",
    "is_active": true,
    "created_at": "2024-01-15T10:30:00",
    "updated_at": "2024-01-15T10:30:00",
    "created_by": 1
  }
]
```

### 8. Publicités actives par pays (Application mobile)

**GET** `/advertisement/active/{country}`

Récupère les publicités actives pour un pays spécifique.

**Réponse:**
```json
[
  {
    "id": 1,
    "title": "Promotion spéciale",
    "description": "Découvrez nos offres exceptionnelles",
    "image_url": "https://example.com/image.jpg",
    "country": "France",
    "is_active": true,
    "created_at": "2024-01-15T10:30:00",
    "updated_at": "2024-01-15T10:30:00",
    "created_by": 1
  }
]
```

## Codes d'erreur

- `400`: Données invalides ou limite de 3 publicités actives dépassée
- `401`: Token JWT manquant ou invalide
- `403`: Droits administrateur requis
- `404`: Publicité non trouvée
- `500`: Erreur interne du serveur

## Règles métier

1. **Limite de publicités actives**: Maximum 3 publicités actives simultanément
2. **Droits d'accès**: Seuls les administrateurs peuvent gérer les publicités
3. **Pays cible**: Si `country` est null, la publicité s'affiche pour tous les pays
4. **Ordre d'affichage**: Les publicités sont triées par date de création (plus récentes en premier)

## Exemples d'utilisation

### Créer une publicité globale
```bash
curl -X POST http://localhost:5000/advertisement/ \
  -H "Authorization: Bearer <jwt_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Promotion mondiale",
    "description": "Offre valable dans tous les pays",
    "image_url": "https://example.com/global.jpg",
    "is_active": true
  }'
```

### Récupérer les publicités actives
```bash
curl -X GET http://localhost:5000/advertisement/active
```

### Récupérer les publicités pour un pays spécifique
```bash
curl -X GET http://localhost:5000/advertisement/active/France
``` 