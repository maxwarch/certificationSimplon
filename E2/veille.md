## Rapport de Veille Technologique : Catégorisation d'Événements Touristiques

**Objectif :** Catégoriser automatiquement des événements touristiques à partir de données tabulaires (titre, description, date)  en utilisant un service d'IA.

**Données Source :**  Données tabulaires existantes contenant la description, le titre et la date de chaque événement.

**Agrégateurs et Moteurs de Recherche:**

* **Google Search:** Recherche générale sur les services de NLP et de classification de texte. Requêtes  telles que "comparatif openai azure gcp nlp 2024", "classification de texte automatique", "meilleure plateforme NLP pour classification texte ecommerce".
* **Daily.dev:** Suivi de blogs et sites d'actualité sur l'IA, le Machine Learning et le NLP.

**Sites Web et Documentation Officielle:**

* **OpenAI:** [https://openai.com/](https://openai.com/) - Documentation, exemples de code, tarification.  Recherche spécifique sur les modèles de NLP et l'API OpenAI.
* **Microsoft Azure:** [https://azure.microsoft.com/fr-fr/services/cognitive-services/](https://azure.microsoft.com/fr-fr/services/cognitive-services/) - Documentation sur Azure Cognitive Services,  spécifiquement  Text Analytics et  Custom Text Classification.  Comparaison des différents services et  tarification.
* **Google Cloud:** [https://cloud.google.com/ai-platform/](https://cloud.google.com/ai-platform/) -  Documentation sur Google Cloud AI Platform, notamment Natural Language et AutoML Natural Language.  Exemples d'utilisation et  tarification.
* **Amazon Web Services:** [https://aws.amazon.com/fr/comprehend/](https://aws.amazon.com/fr/comprehend/) - Documentation sur Amazon Comprehend, en particulier les fonctionnalités de classification de texte.  Tutoriels, exemples et tarification.

**Sites:**

*  **Towards Data Science (Medium)**: https://towardsdatascience.com/ - Publication Medium avec de nombreux articles sur la Data Science, le Machine Learning et l'IA, souvent écrits par des experts du domaine. Rechercher des articles comparatifs sur les services de NLP.
*  **VentureBeat**: https://venturebeat.com/ - Site d'actualité tech avec une section dédiée à l'IA. Publie régulièrement des articles sur les nouveaux services et les tendances du marché.

**Communautés et Forums:**

* **Stack Overflow:** Recherche de discussions et questions sur l'utilisation des différents services d'IA pour la classification de texte.
* **Reddit (subreddits dédiés à l'IA et au Machine Learning):**  Suivi des discussions et des actualités sur les différents services.
* **LinkedIn** Par exemple, ce [post](https://www.linkedin.com/advice/1/what-best-natural-language-processing-tools-text-classification-ja3ue?lang=fr&originalSubdomain=fr)

**Services d'IA Évalués :**

* **OpenAI:** Offre des modèles de traitement du langage naturel (NLP) performants,  facilement intégrables via API,  avec des options de fine-tuning.  Documentation complète et communauté active.
* **Azure Cognitive Services (Microsoft) :**  Propose une gamme complète de services d'IA, dont la classification de texte et l'analyse de sentiment. Intégration aisée avec d'autres services Azure.  Bonne documentation et support.
* **Google Cloud AI Platform :**  Offre des solutions de Machine Learning  et de NLP,  incluant AutoML pour la classification de texte sans expertise en code. Scalable et performant.  Documentation exhaustive.
* **Amazon Comprehend (AWS) :**  Service de NLP  permettant l'extraction d'entités, l'analyse de sentiment et la classification de texte.  Intégration facile avec d'autres services AWS.  Documentation détaillée.

**Critères d'Évaluation :**

* **Performance de la catégorisation :** Précision et fiabilité de la classification des événements.
* **Facilité d'intégration :** Simplicité d'utilisation des API et intégration avec l'infrastructure existante.
* **Coût :** Tarification des services d'IA et coût global de l'implémentation.
* **Scalabilité :** Capacité du service à gérer un volume croissant de données.
* **Support et documentation :** Qualité de la documentation et disponibilité du support technique.
* **Confidentialité des données :**  Conformité aux réglementations sur la protection des données. Nous n'avons pas de donnée personnelle, ce sont des évènements publics que nous catégorisons.



**Évaluation des Services :**


| Service        | Performance | Intégration | Coût | Scalabilité | Support/Doc | Confidentialité |
|----------------|-------------|------------|------|------------|-------------|-----------------|
| OpenAI        | Excellent    | Facile      | Moyen | Excellent    | Excellent    | Bon            |
| Azure          | Bon         | Facile      | Moyen | Excellent    | Bon         | Excellent            |
| Google Cloud   | Bon         | Moyen      | Moyen | Excellent    | Bon         | Excellent            |
| Amazon Comprehend | Bon         | Facile      | Moyen | Excellent    | Bon         | Excellent            |


**Choix Recommandé : OpenAI**

OpenAI offre un bon équilibre entre performance,  facilité d'intégration, et coût. Ses modèles de NLP sont réputés pour leur précision, et l'API est simple à utiliser. Le fine-tuning permet d'adapter les modèles aux données spécifiques des événements touristiques.

**Exemple de Développement avec OpenAI :**

```python
import openai
import os

openai.api_key = os.getenv("OPENAI_API_KEY")


def categorize_event(description):
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=f"Catégorise l'événement touristique suivant:\n\n{description}\n\nCatégorie:",
        max_tokens=64,
        n=1,
        stop=None,
        temperature=0.5, # Ajuster la température pour contrôler la créativité
    )
    categorie = response.choices[0].text.strip()
    return categorie



description = "Festival de musique avec des artistes internationaux, des stands de nourriture et des activités pour les enfants. Se déroule en plein air pendant trois jours."

categorie = categorize_event(description)
print(f"Catégorie: {categorie}") # Exemple: Festival, Musique, Famille
```

Une fois le modèle créé, l'idée sera de scraper les sites web listant les évènements touristiques afin de les passer dans le modèle.

**Intégration et Fonctionnalités :**

1. **Prétraitement des données :** Nettoyage et normalisation des données textuelles (titre, description).
2. **Appel API OpenAI :** Envoi de la description de l'événement à l'API OpenAI pour la catégorisation.
3. **Traitement de la réponse :** Récupération de la catégorie prédite par OpenAI.
4. **Stockage des résultats :**  Enregistrement de l'évènement catégorisé dans une base de données.
5. **Interface utilisateur :**  Affichage des événements catégorisés dans une interface utilisateur conviviale.

**Monitorage:**

* Suivi des performances de l'API OpenAI (temps de réponse, erreurs).
* Surveillance de la qualité de la catégorisation (évaluation manuelle périodique).
* Mise en place d'alertes en cas de problèmes.


**Conclusion:**

L'utilisation d'OpenAI offre une solution efficace pour la catégorisation automatique des événements touristiques. L'API est facile à intégrer, et les modèles de NLP offrent une bonne performance. Le monitorage régulier et l'adaptation du modèle  permettront d'optimiser la qualité de la catégorisation au fil du temps.
