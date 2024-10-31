import os
import pytz
from datetime import datetime
from supabase import create_client
from dotenv import load_dotenv
from fasthtml.common import *

# Load env variables
load_dotenv()

# Initialise Supabase client
supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))

app, rt = fast_app(
    hdrs=(Link(rel="icon", type="assets/x-icon", href="/assets/favicon.png"),),
)

MAX_NAME_CHAR = 15
MAX_MESSAGE_CHAR = 50
TMSTMP_FMT = "%Y-%m-%d %I:%M:%S %p CET"

def get_cet_time():
    cet_tz = pytz.timezone('CET')
    return datetime.now(cet_tz)

def add_message(name, message):
    timestamp = get_cet_time().strftime(TMSTMP_FMT)
    supabase.table("message").insert(
        {"Name" : name, "Message" : message, "Timestamp" : timestamp},
    ).execute()

def get_messages():
    # Sort by ids in descending order
    response = (
        supabase.table("message").select("*").order("id", desc=True).execute()
    )
    return response.data

def render_message(entry):
    # Article(
    #     Header(f"Name: name"),
    #     P("message"),
    #     Footer(Small(Em(f"Posted: time"))),
    # )
    return (
        Article(
            Header(f"Name: {entry['Name']}"),
            P(entry["Message"]),
            Footer(Small(Em(f"Posted: {entry['Timestamp']}"))),
        )
    )

def render_message_list():
    # messages=[
    #     {"name" : "Bob", "message" : "Test", "timestamp" : "today"},
    #     {"name" : "Bob", "message" : "Test", "timestamp" : "today"},
    # ]
    messages = get_messages()

    return Div(
        *[render_message(entry) for entry in messages],
        id="message_list",
    )

def render_content():
    form = Form(
        Fieldset(
            Input(
                type="text",
                name="name",
                placeholder="Name",
                required=True,
                maxlength=MAX_NAME_CHAR,
            ),
            Input(
                type="text",
                name="message",
                placeholder="Message",
                required=True,
                maxlength=MAX_MESSAGE_CHAR,
            ),
            Button("Submit", type="submit"),
            role="group",
        ),
        method = "post",
        hx_post = "/submit-message", # send a post request to the /submit-message endpoint 
        hx_target = "#message_list", # only swap the message list
        hx_swap = "outerHTML", # Replace the entire content of the target element with the response
        hx_on__after_request = "this.reset()", # reset the form after submission
    )

    return Div(
        P(Em("Something nice")),
        form,
        Div(
            "Made by ",
            A("Alex", href="", target="_blank")
        ),
        Hr(),
        render_message_list(),
    )

@rt('/', methods=["GET"])
#def get(): return Titled(Div(P('Hello World!'), hx_get="/change"))
def get(): return Titled('My app', render_content())

@rt('/change')
def get(): return Titled(Div(P('Nice to be here!')), P(A("Back home", href="/")))

@rt('/submit-message', methods=["POST"])
def post(name: str, message: str):
    add_message(name, message)
    return render_message_list()

serve()