import re
import dateparser
from dateparser.search import search_dates
import spacy
from unidecode import unidecode

nlp = spacy.load("fr_core_news_sm")

positive_words = [
            "satisfait","super","aimé","aimer", "heureux", "content", "ravi", "enthousiaste", "merveilleux", "excellent", "génial",
            "fantastique", "super", "formidable", "impressionnant", "admirable", "agréable", "extraordinaire",
            "bien", "plaisant", "bon", "idéal", "exceptionnel", "parfait", "charmé", "séduit", "positif",  "top",
            "encourageant", "réjouissant", "agrémenté", "exalté", "enthousiasmant", "adéquat", "approprié", "confortable",
            "chaleureux", "accueillant", "convivial", "sympathique", "intéressant", "captivant", "attrayant",
            "pittoresque", "bucolique", "splendide", "pittoresque", "magique", "envoûtant", "inoubliable", "mémorable", "redire"
        ]

negative_words = [
            "insatisfait", "mécontent", "déçu", "contrarié", "désappointé", "frustré", "mauvais", "nul", "horrible",
            "déplorable", "décevant", "insatisfaisant", "inadéquat", "inapproprié", "inconfortable", "désagréable",
            "fâché", "irrité", "énervé", "triste", "malheureux", "déprimé", "déprimant", "négatif", "découragé",
            "ennuyeux", "dépourvu", "déplaisant", "repoussant", "inquiétant", "ennuyant",
            "fatigant", "lassant", "déprimant", "stressant", "anxiogène", "perturbant", "ennui", "ennuyé", "trouble",
            "perturbé", "revoir", "retravailler", "améliorer", "marge", "manque", "peu", "horrible", "affreux"
        ]

def lemmatize(mot) :
    return nlp(unidecode(mot))[0].lemma_

def lemmatize2(mot) :
    return nlp(unidecode(mot.lower()))[0].lemma_

positive_words = list(set(map(lemmatize2, positive_words)))
negative_words = list(set(map(lemmatize2, negative_words)))

def analyze_sentiment(sentence):

    doc = nlp(sentence)
    sentiment_score = 0

    # Liste de tokens modifiés par une négation
    negated_tokens = set()

    #on récupere tous les tokens affectés par une négation
    for token in doc:
        if token.text == 'n' or token.text == 'ne' or token.text == 'pas':
            negated_tokens.add(token.head.text)

    for token in doc:
        # Lemmatizer le token
        lemma = lemmatize2(token.text)
        
        # Examiner les adjectifs, adverbes et verbes
        if token.pos_ in ["ADJ", "ADV", "VERB"]:
            if lemma in positive_words:
                sentiment_score += 1 if token.text not in negated_tokens else -1
            elif lemma in negative_words:
                sentiment_score -= 1 if token not in negated_tokens else 1

    # Classification en fonction du score de sentiment
    # if score >0, positif, sinon négatif
    return(sentiment_score)



def finding_intent(phrase, lemmas):
    fields = lemmas.keys()
    scores = {field: 0 for field in fields}

    doc = nlp(unidecode(phrase))

    for token in doc:
        token = token.lemma_
        for field in fields:
            if any(lemma in token for lemma in lemmas[field]):
                scores[field] += 1

    return max(scores, key=scores.get)

