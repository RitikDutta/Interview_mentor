import openai
import random
import time
from dotenv import load_dotenv
import os
from database.user_manager import UserManager

# Load the OpenAI API key from .env file
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

class DataScienceInterviewAssistant:
    def __init__(self, instruction, current_user):
            self.current_user = current_user
            self.client = openai.OpenAI()
            # self.assistant = self.client.beta.assistants.create(
            #     name="Data Science Interview Assistant",
            #     instructions=instruction,
            #     model="gpt-3.5-turbo-1106",
            # )
            # self.thread = self.client.beta.threads.create()
            # print(f"Thread created with ID: {self.thread_id}")
            self.usermanager = UserManager()
            print("ASSISTANT id = " ,self.usermanager.get_assistant_id(str(current_user)))
            print("CURRENT USER = ", str(current_user))
            
            # print_thread_conversation(self.thread_id)
            if self.usermanager.get_assistant_id(str(current_user)) and self.usermanager.get_thread_id(str(current_user)) != None:
                print("TRUE")
                self.assistant_id = self.usermanager.get_assistant_id(str(current_user))
                self.thread_id = self.usermanager.get_thread_id(str(current_user))


            else:
                self.assistant = self.client.beta.assistants.create(
                    name="Data Science Interview Assistant",
                    instructions=instruction,
                    model="gpt-3.5-turbo-1106",
                )
                self.thread = self.client.beta.threads.create()
                
                self.assistant_id = self.assistant.id
                self.thread_id = self.thread.id
                self.usermanager.add_assistant_id(str(current_user), str(self.assistant.id))
                self.usermanager.add_thread_id(str(current_user), str(self.thread_id))


    def conduct_interview(self, question):
        thread_id = self.thread_id
        print(f"Thread created with ID: {thread_id}")  # Print the thread ID
        
        # init user 
        # self.client.beta.threads.messages.create(
        #     thread_id=thread_id,thread_id
        #     role="user",
        #     content="Hey"
        # )

        # user
        self.client.beta.threads.messages.create(
            thread_id=thread_id,
            role="user",
            content=question,
        )
        instruction2 = """
            Initial Interaction and Domain Inquiry

            Begin the interaction with a friendly greeting.
            Ask the user about their target domain for the mock interview. Example: "Hello! I'm your Mock Interview Mentor. What domain are you preparing for? Tech, Finance, Healthcare?"
            CV Submission Request

            Suggest that the user provide their CV to enhance the interview process. Example: "If you'd like, you can share your CV with me. This will help me tailor the questions specifically to your background and experience."
            Tailoring Questions Based on Domain and CV

            Analyze the user's domain and the details provided in the CV.
            Prepare and ask questions relevant to the domain and the information in the CV. This includes role-specific questions, experience-based scenarios, and competency inquiries.
            One-Question-at-a-Time Approach

            Pose one question at a time, allowing the user to respond without feeling rushed.
            Ensure that the questions are clear and understandable.
            Providing Ratings and Feedback

            After each response from the user, offer a rating and constructive feedback. This could be based on the content, clarity, relevance, and confidence in the response.
            Feedback should be specific, actionable, and supportive. Example: "Your answer was well-structured, but you might want to include more specific examples related to project management."
            Ensuring a Thorough Interview Experience

            The interview should cover various aspects, including technical skills, soft skills, and situational responses.
            Maintain a respectful and encouraging tone throughout the interview.
            Conclusion and Overall Feedback

            At the end of the interview, provide a summary of the user’s performance, highlighting strengths and areas for improvement.
            Thank the user for participating and encourage them for their upcoming real interviews.

            you are a fucction that only respond as json and only return 3 variable in json, u cannot say anything else, u cannot chat with user directly, don't say anything other that the json text requested
            make that text in structured json format exactly like this
            {'feedback': 'feedback in the text', 'score': 'score given by assistant(if u havent asked any question keep the score empty)', 'next_question' : 'next question in the text'}
"""
        
        run = self.client.beta.threads.runs.create(
            thread_id=thread_id,
            assistant_id=self.assistant_id,
            instructions=instruction2
        )

        while True:
            time.sleep(5)
            run_status = self.client.beta.threads.runs.retrieve(
                thread_id=thread_id,
                run_id=run.id
            )

            if run_status.status == 'completed':
                messages = self.client.beta.threads.messages.list(
                    thread_id=thread_id
                )
                # print(messages.data)
                interview_responses = []
                for msg in messages.data:
                    role = msg.role
                    content = msg.content[0].text.value
                    interview_responses.append({"role": role, "content": content})
                break
            elif run_status.status == 'requires_action':
                # Handle any required actions if needed
                pass
            else:
                continue

        # Assign a random score for simplicity
        score = random.randint(1, 10)
        return interview_responses, score

    def get_thread_messages(self, thread_id):
        # Retrieve messages from a specific thread
        messages = self.client.beta.threads.messages.list(thread_id=thread_id)
        return messages.data

    def print_thread_conversation(self, thread_id):
        # Print the conversation of a specific thread
        messages = self.get_thread_messages(thread_id)
        for msg in messages:
            print(f"{msg.role.capitalize()}: {msg.content[0].text.value}")

    def get_thread_id(self):
        return self.thread_id

    def get_messages(self, custom_name):
        thread_id = self.usermanager.get_thread_id(str(self.current_user))
        # Retrieve messages from a specific thread
        # message stored in thread here
        messages = self.client.beta.threads.messages.list(thread_id=thread_id)
        formatted_messages = []
        for msg in messages.data:
            role = msg.role.capitalize()
            if role == "User":
                role = custom_name  # Replace "User" with the custom name
            content = msg.content[0].text.value
            formatted_message = f"{role}: {content}"
            formatted_messages.append(formatted_message)
            # formatted_messages = ['Assistant: hello', 'Random Guy: hihi']
        return formatted_messages

