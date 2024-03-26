from typing import List, Dict, Any, Text
from rasa_sdk import Action
from rasa_sdk.events import SlotSet, UserUttered, Restarted
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
import re
import dateparser
from dateparser.search import search_dates
import pandas as pd
from actions.applied_functions import lemmatize, finding_intent, analyze_sentiment

acheter = ["acheter", 'commander', 'billet', 'réserver','aller','ticket','train','avion']
meteo = ["meteo", "temps", "pluie", "pluvieux", "neige", "neigeux", "soleil", 'chaud', 'chaleur', 'température', 'pleuvoir', 'neiger', 'ensoleillé', 'soleil', 'nuageux', 'nuages','fait']
activite = ["information", "info", "choses", "suggestion", "amuser", "divertir", "divertissement", "activités", "explorer", "loisirs", "passe-temps", "à faire"]

type_synonyms = {
    'sport': ['stade', 'gymnase', 'terrain', 'piste', 'parcours', 'sportif', 'sportive'],
    'militaire': ['base', 'caserne', "camp", 'forteresse', 'zone de combat' , 'militaire'],
    'port': ['port maritime', 'quai', 'bassin portuaire', 'jetée', 'anse', 'port'],
    'education': ['école', 'université', 'campus', 'salle de classe', 'bibliothèque', 'education'],
    'administratif': ['bureau', 'mairie', 'préfecture', 'palais de justice', 'bâtiment gouvernemental', 'administratif'],
    'religion': ['temple', 'église', 'mosquée', 'synagogue', 'sanctuaire', 'religion', 'religieux'],
    'histoire': ['musée', 'site archéologique', 'historique', 'monument', 'histoire']
}

#on lemmatise les mots et enlève caractères spéciaux
acheter = list(set(map(lemmatize, acheter)))
meteo = list(set(map(lemmatize, meteo)))
activite = list(set(map(lemmatize, activite)))

sport = list(set(map(lemmatize, type_synonyms['sport'])))
militaire = list(set(map(lemmatize, type_synonyms['militaire'])))
port = list(set(map(lemmatize, type_synonyms['port'])))
education = list(set(map(lemmatize, type_synonyms['education'])))
administratif = list(set(map(lemmatize, type_synonyms['administratif'])))
religion = list(set(map(lemmatize, type_synonyms['religion'])))
histoire = list(set(map(lemmatize, type_synonyms['histoire'])))

lemma_dict = {'acheter':acheter,
              'meteo':meteo,
              'activite':activite}

type_activite_lemma_dict = {'sport': sport,
                            'militaire': militaire,
                            'port': port,
                            'education': education,
                            'administratif': administratif,
                            'religion': religion,
                            'histoire':histoire}


class ValidateEmailAction(Action):
    def name(self):
        return "action_validate_email"

    def run(self, dispatcher, tracker, domain):
        email = next(tracker.get_latest_entity_values("email"), None)

        if email and re.match(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", email):
            dispatcher.utter_message(f"L'e-mail {email} est valide. Merci !")
            return [SlotSet("email", email),SlotSet("type_demande", None), Restarted()]
        else:
            dispatcher.utter_message(f"L'e-mail {email} n'est pas valide. Veuillez le retaper.")

        return []



class ExtractDateIntent(Action):
    def name(self):
        return "action_extract_date"

    def run(self, dispatcher, tracker, domain):
        date_str = ''
        # Récupérer le dernier message de l'utilisateur
        latest_message = str(tracker.latest_message['text'])
        dates = search_dates(latest_message, languages=['fr'])

        # Si des dates sont trouvées, convertir en format de date
        if dates:
            date_str, _ = dates[-1]  # Prendre la première date trouvée
            date_str = str(dateparser.parse(date_str))[:10]
            dispatcher.utter_message(f"D'accord, vous voulez partir le  {date_str}. Quel est votre email pour le billet ?")
            return [SlotSet("date", date_str),SlotSet("type_demande", None)]
        
        else : 
            dispatcher.utter_message(f"Je n'ai pas compris votre date de départ, veuillez reformuler")
        return[]
        # Si aucune date n'est trouvée, ne rien faire
        

class ExtractDemande(Action):
    def name(self):
        return "action_extract_demande"

    def run(self, dispatcher, tracker, domain):

        latest_message = str(tracker.latest_message['text'])
        
        type_demande = finding_intent(latest_message, lemma_dict)

        if type_demande == "acheter" :
            dispatcher.utter_message(f"D'accord achetons un billet ensemble")

        if type_demande == "meteo" :
            dispatcher.utter_message(f"D'accord, regardons la météo ensemble")

        if type_demande == "activite" :
            dispatcher.utter_message(f"D'accord, nous allons vous trouver une activite")


        return [SlotSet("type_demande", type_demande)]


        
class CheckCity(Action):
    def name(self):
        return "action_check_city"

    def run(self, dispatcher, tracker, domain):

        city = tracker.get_slot('city')
        if city == None:
            dispatcher.utter_message('Votre demande concerne quelle ville ?')
        else: 
            dispatcher.utter_message(f"Votre demande concerne {city} ? Si ce n'est pas le cas, quelle ville ?")
        
        # Make sure the first letter is uppercase 
        city = city[0].upper() + city[1:]

        return [SlotSet("city", city)]
    


class ActionFindAttraction(Action):
    def name(self) -> Text:
        return "action_find_attraction"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        # Extract entity values from user input
        commune = tracker.get_slot('city')
        activity_type = next(tracker.get_latest_entity_values("type_activite"), None)

        if activity_type == None:
            dispatcher.utter_message(f"Bien sur ! Y-a-t'il un type d'activité qui vous intéresse à {commune} ?")

        return []
    


class ActionAskAttractionType(Action):
    def name(self) -> Text:
        return "action_ask_activity_type"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        activity_type = next(tracker.get_latest_entity_values("type_activite"), None)
        commune = tracker.get_slot('city')
        data = pd.read_excel("./inventaire-Brest.xlsx")

        if activity_type == None:
            dispatcher.utter_message(f"Bien sur ! Y-a-t'il un type d'activité qui vous intéresse à {commune} ?")
       
        activity_type = finding_intent(activity_type, type_activite_lemma_dict)

        # Filter data based on user input
        filtered_data = data[(data['commune'] == commune) & (data['category'] == activity_type)]

        # # Get relevant information
        result = filtered_data[['titre_courant', 'commentaire_descriptif']].sample().to_dict(orient='records')[0]

        # # Respond to the user
        if not pd.isna(result['commentaire_descriptif']):
            dispatcher.utter_message(f"Voici une attraction {activity_type} à {commune}: {result['titre_courant']}. Ce lieu est ainsi décrit : {result['commentaire_descriptif']}")
        else:
            dispatcher.utter_message(f"Voici une attraction à {commune}: {result['titre_courant']}.")

        return [SlotSet("activity_type", activity_type), Restarted()]
    



class Feebdback(Action):
    def name(self):
        return "action_feedback"

    def run(self, dispatcher, tracker, domain):

        latest_message = str(tracker.latest_message['text'])

        if analyze_sentiment(latest_message) > 0 :
            dispatcher.utter_message("Merci pour votre avis positif !")
            return [Restarted()]
        if analyze_sentiment(latest_message) < 0 :
            dispatcher.utter_message("Merci pour votre avis négatif, nous nous forçons de nous améliorer !")
            return [Restarted()]
        if analyze_sentiment(latest_message) == 0 :
            dispatcher.utter_message("Je n'ai pas compris votre avis, pouvez vous le reformuler ?")
            return []