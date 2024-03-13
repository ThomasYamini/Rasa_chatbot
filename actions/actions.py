from typing import Any, Dict, Text, List
import pandas as pd
from rasa_sdk import Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk import Action


class ActionFindAttraction(Action):
    def name(self) -> Text:
        return "utter_find_attraction"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        # Load the data
        data = pd.read_excel("./inventaire-du-patrimoine-breton-couche-simplifiee.xlsx")

        # Extract entity values from user input
        city = tracker.get_slot("commune")

        # Filter data based on user input
        filtered_data = data[data['commune'] == city]

        # Get relevant information
        result = filtered_data[['titre_courant', 'commentaire_descriptif']].head().to_dict(orient='records')
        attraction_types = filtered_data['denomination'].drop_duplicates().head()

        # Respond to the user
        dispatcher.utter_message(template='utter_find_attraction',
                                 attraction_types=attraction_types,
                                 city=city,
                                 result=result)
        return []


class ActionGetDescription(Action):
    def name(self) -> Text:
        return "utter_get_description"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        # Load the data
        data = pd.read_excel("./inventaire-du-patrimoine-breton-couche-simplifiee.xlsx")

        # Extract entity values from user input
        attraction_title = tracker.get_slot("titre_courant")

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
