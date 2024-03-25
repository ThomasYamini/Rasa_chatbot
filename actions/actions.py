from typing import Any, Dict, Text, List, Union
import pandas as pd
from rasa_sdk import Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk import Action
from rasa_sdk.events import SlotSet, Restarted


class ActionFindAttraction(Action):
    def name(self) -> Text:
        return "action_find_attraction"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        # Load the data
        data = pd.read_excel("./inventaire-Brest.xlsx")

        # Extract entity values from user input
        commune = next(tracker.get_latest_entity_values("commune"), None)
        activity_type = next(tracker.get_latest_entity_values("type_activite"), None)

        if activity_type == None:
            dispatcher.utter_message(f"Bien sur ! Y-a-t'il un type d'activité qui vous intéresse à {commune} ?")

        # # Filter data based on user input
        # filtered_data = data[data['commune'] == commune & data['category'] == activity_type]

        # # # Get relevant information
        # result = filtered_data[['titre_courant', 'commentaire_descriptif']].sample(n=1).to_dict(orient='records')[0]

        # # # Respond to the user
        # if not pd.isna(result['commentaire_descriptif']):
        #     dispatcher.utter_message(f"Voici une attraction à {commune}: {result['titre_courant']}. Ce lieu est ainsi décrit : {result['commentaire_descriptif']}")
        # else:
        #     dispatcher.utter_message(f"Voici une attraction à {commune}: {result['titre_courant']}.")
            
        return [SlotSet("city", commune)]
    


type_synonyms = {
    'sport': ['stade', 'gymnase', 'terrain', 'piste', 'parcours', 'sportif', 'sportive'],
    'militaire': ['base', 'caserne', "camp", 'forteresse', 'zone de combat'],
    'port': ['port maritime', 'quai', 'bassin portuaire', 'jetée', 'anse'],
    'education': ['école', 'université', 'campus', 'salle de classe', 'bibliothèque'],
    'administratif': ['bureau', 'mairie', 'préfecture', 'palais de justice', 'bâtiment gouvernemental'],
    'religion': ['temple', 'église', 'mosquée', 'synagogue', 'sanctuaire'],
    'histoire': ['musée', 'site archéologique', 'historique', 'monument']
}


class ActionAskAttractionType(Action):
    def name(self) -> Text:
        return "action_ask_activity_type"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        activity_type = next(tracker.get_latest_entity_values("type_activite"), None)
        commune = tracker.get_slot('city')
        data = pd.read_excel("./inventaire-Brest.xlsx")

        if activity_type not in type_synonyms.keys():
            for key, synonyms in type_synonyms.items():
                if activity_type in synonyms:
                    activity_type = key
                    break

        # Filter data based on user input
        filtered_data = data[(data['commune'] == commune) & (data['category'] == activity_type)]

        # # Get relevant information
        result = filtered_data[['titre_courant', 'commentaire_descriptif']].sample(n=1).to_dict(orient='records')[0]

        # # Respond to the user
        if not pd.isna(result['commentaire_descriptif']):
            dispatcher.utter_message(f"Voici une attraction {activity_type} à {commune}: {result['titre_courant']}. Ce lieu est ainsi décrit : {result['commentaire_descriptif']}")
        else:
            dispatcher.utter_message(f"Voici une attraction à {commune}: {result['titre_courant']}.")

        return [SlotSet("activity_type", activity_type)]

class ActionGetDescription(Action):
    def name(self) -> Text:
        return "action_get_description"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        # Load the data
        data = pd.read_excel("./inventaire-Brest.xlsx")

        # Extract entity values from user input
        attraction_title = next(tracker.get_latest_entity_values("titre_courant"), None)
        # Filter data based on the attraction title
        attraction_info = data[data['titre_courant'].str.contains(attraction_title)]

        if not attraction_info.empty:
            # Get relevant information
            description = attraction_info['commentaire_descriptif'].iloc[0]

            # Respond to the user with the description
            dispatcher.utter_message(template='utter_get_description',
                                     attraction_title=attraction_title,
                                     description=description)
        else:
            dispatcher.utter_message(text=f"je n'ai pas pu trouver d'informations pour {attraction_title}.")

        return []
