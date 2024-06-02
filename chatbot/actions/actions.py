# This files contains your custom actions which can be used to run
# custom Python code.
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
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import make_pipeline
from fuzzywuzzy import process


class ActionAnswerQuestion(Action):
    def name(self) -> Text:
        return "action_answer_question"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        question = tracker.latest_message.get("text")
        with open("data/faq.json", "r") as file:
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


class ActionSearchPrograms(Action):
    def name(self) -> Text:
        return "action_search_programs"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        country = tracker.get_slot("country")
        timeline = tracker.get_slot("timeline")
        interests = tracker.get_slot("interests")
        benefits = tracker.get_slot("benefits")
        skills = tracker.get_slot("skills")
        accommodation = tracker.get_slot("accommodation")
        meal = tracker.get_slot("meal")

        # Split the timeline into start and end dates
        start_date, end_date = None, None
        if timeline:
            parts = timeline.split(" to ")
            if len(parts) == 2:
                start_date, end_date = parts

        # Debug prints
        print(f"Country: {country}")
        print(f"Timeline: {timeline}")
        print(f"Interests: {interests}")
        print(f"Benefits: {benefits}")
        print(f"Skills: {skills}")
        print(f"Accommodation: {accommodation}")
        print(f"Meal: {meal}")

        with open("data/global_volunteer.json", "r") as file:
            program_data = json.load(file)

        filtered_programs = [
            program for program in program_data
            if program_matches_preferences(program, country, timeline, interests, benefits, skills, accommodation, meal)
        ]

        if filtered_programs:
            program_list = "\n".join([program["Name"] for program in filtered_programs])
            dispatcher.utter_message(text=f"Based on your preferences, here are some suitable programs:\n{program_list}")
        else:
            dispatcher.utter_message(text="I couldn't find any programs matching your preferences.")

        return []

def program_matches_preferences(program, country, timeline, interests, benefits, skills, accommodation, meal):
    match = True
    if country and program["Country"].lower() != country.lower():
        match = False
    if timeline and timeline not in program["Timeline"]:
        match = False
    if interests and interests not in program["Interests"]:
        match = False
    if benefits and benefits not in program["Benefits"]:
        match = False
    if skills and skills not in program["Skills"]:
        match = False
    if accommodation and accommodation not in program["Accommodation"]:
        match = False
    if meal and meal not in program["Meal"]:
        match = False
    return match


class ActionAskCountry(Action):
    def name(self) -> Text:
        return "action_ask_country"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        dispatcher.utter_message(text="In which country would you like to volunteer?")
        return []


class ActionAskTimeline(Action):
    def name(self) -> Text:
        return "action_ask_timeline"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        dispatcher.utter_message(text="When are you available to volunteer?")
        return []