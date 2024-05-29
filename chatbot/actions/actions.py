# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"

# from typing import Any, Text, Dict, List
#
# from rasa_sdk import Action, Tracker
# from rasa_sdk.executor import CollectingDispatcher
#
#
# class ActionHelloWorld(Action):
#
#     def name(self) -> Text:
#         return "action_hello_world"
#
#     def run(self, dispatcher: CollectingDispatcher,
#             tracker: Tracker,
#             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
#
#         dispatcher.utter_message(text="Hello World!")
#
#         return []
from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import UserUtteranceReverted, SessionStarted, ActionExecuted, EventType
import json

class ActionAnswerQuestion(Action):
    def name(self) -> Text:
        return "action_answer_question"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        question = tracker.latest_message.get("text")
        with open("global_volunteer.json", "r") as file:
            data = json.load(file)
            # Search for FAQs
            for faq in data["faqs"]:
                if faq["question"].lower() in question.lower():
                    dispatcher.utter_message(text=faq["answer"])
                    return []

            # Search for program details
            for program in data["programs"]:
                if program["program_name"].lower() in question.lower():
                    response = f"The {program['program_name']} program is a {program['duration_weeks']}-week program in {program['country']} from {program['timeline']}. It provides {'accommodation and covers meals on weekdays' if program['accommodation'] else 'no accommodation'}."
                    dispatcher.utter_message(text=response)
                    return []

        dispatcher.utter_message(text="I'm sorry, I don't have the answer to that question.")
        return []

class ActionWelcome(Action):
    def name(self):
        return "action_welcome"

    async def run(self, dispatcher, tracker, domain):
        dispatcher.utter_message(text="Hello! Welcome to our chatbot. How can I assist you today?")
        return [UserUtteranceReverted()]

class ActionSessionStart(Action):

    def name(self) -> str:
        return "action_session_start"

    async def run(self, dispatcher: CollectingDispatcher, tracker, domain) -> List[EventType]:
        # Start a new session
        events = [SessionStarted()]

        # Define any slots you want to reset here
        # events.append(SlotSet("slot_name", None))

        # Display welcome message
        dispatcher.utter_message(response="utter_welcome")

        # Any additional events like `ActionExecuted` can be appended here
        events.append(ActionExecuted("action_listen"))

        return events

