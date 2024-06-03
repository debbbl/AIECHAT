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
import re
from rasa_sdk.events import SlotSet
from datetime import datetime


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
        start_month = tracker.get_slot("start_month")
        end_month = tracker.get_slot("end_month")

        # Initialize start and end dates
        start_date, end_date = None, None

        # Convert month names to their corresponding numerical values
        user_start_month_lower = None
        user_end_month_lower = None
        if start_month:
            user_start_month_lower = start_month.lower()
            start_date = datetime.strptime(start_month, "%B").month
        if end_month:
            user_end_month_lower = end_month.lower()
            end_date = datetime.strptime(end_month, "%B").month

            # Debug prints
            print(f"Country: {country}")
            print(f"Start month: {start_month}")
            print(f"End month: {end_month}")

        with open("data/global_volunteer.json", "r") as file:
            program_data = json.load(file)

        filtered_programs = [
            program for program in program_data
            if program_matches_preferences(program, country, user_start_month_lower, user_end_month_lower)
        ]

        if filtered_programs:
            program_list = "\n".join([program["Name"] for program in filtered_programs])
            dispatcher.utter_message(
                text=f"Based on your preferences, here are some suitable programs:\n{program_list}")
        else:
            dispatcher.utter_message(text="I couldn't find any programs matching your preferences.")

        return []

class ActionShowProgramDetails(Action):
    def name(self) -> Text:
        return "action_show_program_details"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        suggested_program = tracker.get_slot("suggested_program")

        if suggested_program:
            response = f"Program Name: {suggested_program['Name']}\n\nKey Activities:\n{', '.join(suggested_program['Key Activities'])}\n\nObjectives: {suggested_program['Objectives']}\n\nInterests: {suggested_program['Interests']}\n\nTimeline: {suggested_program['Timeline']}\n\nBenefits: {suggested_program['Benefits']}\n\nSkills: {suggested_program['Skills']}\n\nAccommodation: {suggested_program['Accommodation']}\n\nMeal: {suggested_program['Meal']}"
            dispatcher.utter_message(text=response)
        else:
            dispatcher.utter_message(text="No suggested program available.")

        return []

# def parse_month(month_str):
#     return datetime.strptime(month_str, "%B").month

def program_matches_preferences(program, country, start_month, end_month):
    match = True
    if country and program["Country"].lower() != country.lower():
        match = False
    if start_month and end_month:
        program_timeline = program.get("Timeline", "").lower()
        if " to " in program_timeline:
            program_start_month, program_end_month = map(lambda x: x.lower(), program_timeline.split(" to "))
            if start_month > program_end_month or end_month < program_start_month:
                match = False
        else:
            # Handle cases where timeline data doesn't match expected format
            match = False
    return match


class ActionAskMeal(Action):
    def name(self) -> Text:
        return "action_ask_meal"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        suggested_program = tracker.get_slot("suggested_program")
        country = tracker.get_slot("country")

        with open("data/global_volunteer.json", "r") as file:
            program_data = json.load(file)

        for program in program_data:
            if program["Name"] == suggested_program:
                meal = program.get("Meal", "Details not available")
                dispatcher.utter_message(text=f"Meal for {suggested_program} in {country} is {meal}")
                break
        else:
            dispatcher.utter_message(text="Program details not found.")

        return []

class ActionAskAccommodation(Action):
    def name(self) -> Text:
        return "action_ask_accommodation"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        suggested_program = tracker.get_slot("suggested_program")
        country = tracker.get_slot("country")

        with open("data/global_volunteer.json", "r") as file:
            program_data = json.load(file)

        for program in program_data:
            if program["Name"] == suggested_program:
                accommodation = program.get("Accommodation", "Details not available")
                dispatcher.utter_message(text=f"Accommodation for {suggested_program} in {country} is {accommodation}")
                break
        else:
            dispatcher.utter_message(text="Program details not found.")

        return []
class ActionAskCountry(Action):
    def name(self) -> Text:
        return "action_ask_country"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        dispatcher.utter_message(text="In which country would you like to volunteer?")
        return []

class ActionAskInterests(Action):
    def name(self) -> Text:
        return "action_ask_interests"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        dispatcher.utter_message(text="What are your interests?")
        return []


class ActionAskTimeline(Action):
    def name(self) -> Text:
        return "action_ask_timeline"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        dispatcher.utter_message(text="When are you available to volunteer?")
        return []