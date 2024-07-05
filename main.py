import ollama

from kivy.app import App

from kivy.uix.label import Label
from kivy.uix.widget import Widget

from kivy.properties import ObjectProperty
from kivy.properties import StringProperty

from kivy.clock import Clock

from kivy.core.window import Window

# Represents an empty string
EMPTY_STRING = ''

# The amount of padding to be applied to text, so it is not touching the window
CHAT_PADDING = 20

# The text the user has to enter to clear the chat
CLEAR_STRING = 'clear'

# The keycode for the enter key
ENTER_KEY_CODE = 13

# The name of the model being used
MODEL_NAME = 'llama3'


class MyApp(App):
    """The primary class of the program"""

    def build(self):
        """Initializes the program and its root widget """
        # Initialize the name of the window and its ability to read keyboard input
        self.title = 'Kivama'
        Window.bind(on_key_down=self.on_key_down)

        # Returns the root grid layout widget
        return RootWidget()

    def on_key_down(self, keyboard, keycode, text, modifiers, foo):
        """Checks the keyboard for input"""
        # Enter the message when the Enter key is pressed
        if keycode == ENTER_KEY_CODE:
            self.root.enter()


class RootWidget(Widget):
    """The root widget of the program"""
    # Stores the grid layout for the chat and the input field
    chat_layout = ObjectProperty(None)
    text_input = ObjectProperty(None)

    # Represents if the program is currently responding to the user
    is_responding = False

    # Stores information relevant to the current response
    curr_response_label: Label = None
    curr_response_chunk_idx = 0
    curr_response_it = None

    # Stores all messages and responses in the form of an ollama response
    all_messages = []
    all_responses_text = []

    def __init__(self, **kwargs):
        """Initializes the root widget"""
        # Run any general Widget initialization
        super(RootWidget, self).__init__(**kwargs)

        '''Init is called after properties are instantiated and matched with data from my.kv
        Dynamically adjusts the size of the GridLayout called chat_layout as more elements are added
        As the minimum height increases, the height of the layout must also increase'''
        self.chat_layout.bind(minimum_height=self.chat_layout.setter('height'))

        # Begins the custom update loop
        Clock.schedule_interval(self.update, 0)

    def update(self, dt):
        """Custom update code"""
        # Progressively reveals the response of a prompt if the program is responding
        if self.is_responding:

            # Gets the next item from the response
            next_item = next(self.curr_response_it, None)

            # Finishes or prints part of the current response
            if next_item is None:
                self.is_responding = False
            else:
                self.curr_response_label.text = self.curr_response_label.text + next_item['message']['content']
                self.curr_response_chunk_idx += 1

    def enter(self):
        """Enters the current message as a prompt"""

        # Gets the current message and clears the text prompt
        msg = self.text_input.text
        self.text_input.text = EMPTY_STRING

        # Cancels the prompt if there is no prompt or the chat is supposed to be cleared
        if msg is EMPTY_STRING or self.is_responding:
            return
        elif msg.lower().strip() == CLEAR_STRING:
            self.reset()
            return

        # Creates and adds a new label to the chat grid layout
        new_label = Label(text=msg, size_hint_y=None, halign="right", text_size=(self.width - CHAT_PADDING, None))
        self.chat_layout.add_widget(new_label)

        # Responds to the prompt
        self.respond(msg)

    def respond(self, msg):
        """Responds to the prompt"""
        # Creates a new message in the form of an ollama response and adds it to the list of responses
        self.all_messages.append(
            {
                'role': 'user',
                'content': msg,
            })
        self.all_responses_text.append(StringProperty(EMPTY_STRING))

        # Creates a new empty label for the response text and adds it to the chat grid layout
        self.curr_response_label = Label(size_hint_y=None, halign="left", text_size=(self.width - CHAT_PADDING, None))
        self.curr_response_label.bind(texture_size=self.curr_response_label.setter('size'))
        self.chat_layout.add_widget(self.curr_response_label)

        # Generates a new response using the large language model and begins printing the response
        self.curr_response_it = ollama.chat(MODEL_NAME, messages=self.all_messages, stream=True)
        self.is_responding = True

    def reset(self):
        """Resets the chat"""
        # Clears all messages and responses
        self.all_messages = []
        self.all_responses_text = []

        # Clears all the widgets in the chat grid layout
        self.chat_layout.clear_widgets()


# Runs the application
if __name__ == '__main__':
    MyApp().run()
