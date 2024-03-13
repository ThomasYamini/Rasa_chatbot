from typing import Any, Dict, Text, List
import pandas as pd
from rasa_sdk import Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk import Action
from rasa_sdk.events import SlotSet

class ActionFindAttraction(Action):
    def name(self) -> Text:
        return "utter_find_attraction"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        # Load the data
        data = pd.read_excel("./inventaire-Brest.xlsx")

        # Extract entity values from user input
        commune = next(tracker.get_latest_entity_values("commune"), 'Cacaboudin')
        

        # Filter data based on user input
        filtered_data = data[data['commune'] == commune]

        # Get relevant information
        result = filtered_data[['titre_courant', 'commentaire_descriptif']].head(1).to_dict(orient='records')
        attraction_types = filtered_data['denomination'].drop_duplicates().head(1).tolist()

        # Respond to the user
        dispatcher.utter_message(f'Voici quelque {attraction_types} à {commune}: {result}')
        
        return [SlotSet(("city", commune))]


class ActionGetDescription(Action):
    def name(self) -> Text:
        return "utter_get_description"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        # Load the data
        data = pd.read_excel("./inventaire-du-patrimoine-breton-couche-simplifiee.xlsx")

        # Extract entity values from user input
        attraction_title = next(tracker.get_latest_entity_values("titre_courant"), "Mega prout")
        # Filter data based on the attraction title
        attraction_info = data[data['titre_courant'] == attraction_title]

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
