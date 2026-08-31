import argparse
import base64
import io
import json
import re
from pathlib import Path

from openai import OpenAI
from PIL import Image


def encode_image_to_base64(image_path):
    with open(image_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode("utf-8")
        ext = Path(image_path).suffix.lower()
        if ext in [".jpg", ".jpeg"]:
            mime_type = "image/jpeg"
        elif ext == ".png":
            mime_type = "image/png"
        else:
            mime_type = "image/jpeg"
        return f"data:{mime_type};base64,{encoded_string}"


def encode_image_bytes_to_base64(image_bytes: bytes) -> str:
    return base64.b64encode(image_bytes).decode("utf-8")


def build_history_images(history_images: list) -> list:
    if len(history_images) == 0:
        return []

    shrunked_images = []
    for img_bytes in history_images[-4:]:
        image = Image.open(io.BytesIO(img_bytes))
        original_width, original_height = image.size
        target_width, target_height = original_width // 2, original_height // 2
        shrunked_image = image.resize((target_width, target_height))
        output_buffer = io.BytesIO()
        shrunked_image.save(output_buffer, format="PNG")
        image_url = f"data:image/png;base64,{encode_image_bytes_to_base64(output_buffer.getvalue())}"
        shrunked_images.append(image_url)

    return shrunked_images


def load_history_images_from_paths(history_image_paths: list) -> list:
    history_images = []
    for img_path in history_image_paths:
        try:
            with open(img_path, "rb") as f:
                history_images.append(f.read())
        except Exception as e:
            print(f"Error loading image {img_path}: {e}")
    return history_images


def get_mobile_prompt(task, history):
    app_names = [
        "Google Chrome",
        "Settings",
        "Camera",
        "Audio Recorder",
        "Clock",
        "Contacts",
        "Files",
        "Markor",
        "Simple SMS Messenger",
        "Simple Calendar Pro",
        "Simple Gallery Pro",
        "Simple Draw Pro",
        "Pro Expense",
        "Broccoli",
        "OsmAnd",
        "Tasks",
        "Open Tracks Sports Tracker",
        "Joplin",
        "VLC",
        "Retro Music",
    ]

    prompt = f"""You are a GUI Agent, and your primary task is to respond accurately to user requests or questions. In addition to directly answering the user's queries, you can also use tools or perform GUI operations directly until you fulfill the user's request or provide a correct answer. You should carefully read and understand the images and questions provided by the user, and engage in thinking and reflection when appropriate. The coordinates involved are all represented in thousandths (0-999).

# Task:
{task}

# Task Platform
Mobile

# Action Space
### status

Calling rule: `{{"action_type": "status", "goal_status": "<complete|infeasible>"}}`
{{
    "name": "status",
    "description": "Finish the task by using the status action with complete or infeasible as goal_status.",
    "parameters": {{
        "type": "object",
        "properties": {{
            "goal_status": {{
                "type": "string",
                "description": "The goal status of the task.",
                "enum": ["complete", "infeasible"]
            }}
        }},
        "required": [
            "goal_status"
        ]
    }}
}}

### answer

Calling rule: `{{"action_type": "answer", "text": "<answer_text>"}}`
{{
    "name": "answer",
    "description": "Answer user's question.",
    "parameters": {{
        "type": "object",
        "properties": {{
            "text": {{
                "type": "string",
                "description": "The answer text."
            }}
        }},
        "required": [
            "text"
        ]
    }}
}}

### click

Calling rule: `{{"action_type": "click", "box_2d": [[xmin,ymin,xmax,ymax]]}}`
{{
    "name": "click",
    "description": "Click/tap on an element on the screen. Use the box_2d to indicate which element you want to click.",
    "parameters": {{
        "type": "object",
        "properties": {{
            "box_2d": {{
                "type": "array",
                "description": "The box_2d should be [[xmin,ymin,xmax,ymax]] normalized to 0-999, indicating the position of the element."
            }}
        }},
        "required": [
            "box_2d"
        ]
    }}
}}

### long_press

Calling rule: `{{"action_type": "long_press", "box_2d": [[xmin,ymin,xmax,ymax]]}}`
{{
    "name": "long_press",
    "description": "Long press on an element on the screen, similar with the click action above, use the box_2d to indicate which element you want to long press.",
    "parameters": {{
        "type": "object",
        "properties": {{
            "box_2d": {{
                "type": "array",
                "description": "The box_2d should be [[xmin,ymin,xmax,ymax]] normalized to 0-999, indicating the position of the element."
            }}
        }},
        "required": [
            "box_2d"
        ]
    }}
}}

### input_text

Calling rule: `{{"action_type": "input_text", "text": "<text_input>", "box_2d": [[xmin,ymin,xmax,ymax]], "override": true/false}}`
{{
    "name": "input_text",
    "description": "Type text into a text field (this action contains clicking the text field, typing in the text and pressing the enter). Use the box_2d to indicate the target text field.",
    "parameters": {{
        "type": "object",
        "properties": {{
            "text": {{
                "description": "The text to be input. Can be from the command, the memory, or the current screen."
            }},
            "box_2d": {{
                "description": "The box_2d should be [[xmin,ymin,xmax,ymax]] normalized to 0-999, indicating the position of the element."
            }},
            "override": {{
                "description": "If true, the text field will be cleared before typing. If false, the text will be appended."
            }}
        }},
        "required": [
            "text",
            "box_2d",
            "override"
        ]
    }}
}}

### keyboard_enter

Calling rule: `{{"action_type": "keyboard_enter"}}`
{{
    "name": "keyboard_enter",
    "description": "Press the Enter key.",
    "parameters": {{
        "type": "object",
        "properties": {{}},
        "required": []
    }}
}}

### navigate_home

Calling rule: `{{"action_type": "navigate_home"}}`
{{
    "name": "navigate_home",
    "description": "Navigate to the home screen.",
    "parameters": {{
        "type": "object",
        "properties": {{}},
        "required": []
    }}
}}

### navigate_back

Calling rule: `{{"action_type": "navigate_back"}}`
{{
    "name": "navigate_back",
    "description": "Navigate back.",
    "parameters": {{
        "type": "object",
        "properties": {{}},
        "required": []
    }}
}}

### swipe

Calling rule: `{{"action_type": "swipe", "direction": "<up|down|left|right>", "box_2d": [[xmin,ymin,xmax,ymax]](optional)}}`
{{
    "name": "swipe",
    "description": "Swipe the screen or a scrollable UI element in one of the four directions.",
    "parameters": {{
        "type": "object",
        "properties": {{
            "direction": {{
                "type": "string",
                "description": "The direction to swipe.",
                "enum": ["up", "down", "left", "right"]
            }},
            "box_2d": {{
                "type": "array",
                "description": "The box_2d to swipe a specific UI element, leave it empty when swiping the whole screen."
            }}
        }},
        "required": [
            "direction"
        ]
    }}
}}

### open_app

Calling rule: `{{"action_type": "open_app", "app_name": "<name>"}}`
{{
    "name": "open_app",
    "description": "Open an app (nothing will happen if the app is not installed).",
    "parameters": {{
        "type": "object",
        "properties": {{
            "app_name": {{
                "type": "string",
                "description": "The name of the app to open. Supported apps: {",".join(app_names)}"
            }}
        }},
        "required": [
            "app_name"
        ]
    }}
}}

### wait

Calling rule: `{{"action_type": "wait"}}`
{{
    "name": "wait",
    "description": "Wait for the screen to update.",
    "parameters": {{
        "type": "object",
        "properties": {{}},
        "required": []
    }}
}}

# Historical Actions and Current Memory
"""

    history_str = ""
    if len(history) == 0:
        history_str = "You just started, no action has been performed yet."
    else:
        for idx, h in enumerate(history):
            history_str += f"Step {idx}:\n{h}\n\n"

    prompt += history_str + "\n"

    prompt += """# Output Format
1. Memory: important information you want to remember for the future actions. The memory should be only contents on the screen that will be used in the future actions. It should satisfy that: you cannnot determine one or more future actions without this memory. 
2. Reason: the reason for the action and the memory. Your reason should include, but not limited to:- the content of the GUI, especially elements that are tightly related to the user goal- the step-by-step thinking process of how you come up with the new action. 
3. Action: the action you want to take, in the correct JSON format. The action should be one of the above list.

Your answer should look like:
Memory: ...
Reason: ...
Action: {"action_type":...}

# Some Additional Notes
General:
- Usually there will be multiple ways to complete a task, pick the easiest one. Also when something does not work as expected (due to various reasons), sometimes a simple retry can solve the problem, but if it doesn't (you can see that from the history), SWITCH to other solutions.
- Sometimes you may need to navigate the phone to gather information needed to complete the task, for example if user asks "what is my schedule tomorrow", then you may want to open the calendar app (using the `open_app` action), look up information there, answer user's question (using the `answer` action) and finish (using the `status` action with complete as goal_status).
- For requests that are questions (or chat messages), remember to use the `answer` action to reply to user explicitly before finish! Merely displaying the answer on the screen is NOT sufficient (unless the goal is something like "show me ...").
- If the desired state is already achieved (e.g., enabling Wi-Fi when it's already on), you can just complete the task.
- If we say that two items are duplicated, in most cases we require that all of their attributes are exactly the same, not just the name.
Text Related Operations:
- Normally to select certain text on the screen: <i> Enter text selection mode by long pressing the area where the text is, then some of the words near the long press point will be selected (highlighted with two pointers indicating the range) and usually a text selection bar will also appear with options like `copy`, `paste`, `select all`, etc. <ii> Select the exact text you need. Usually the text selected from the previous step is NOT the one you want, you need to adjust the range by dragging the two pointers. If you want to select all text in the text field, simply click the `select all` button in the bar.
- To delete some text: first select the text you want to delete (if you want to delete all texts, just long press the text field and click the `clear all` button in the text selection bar), then click the backspace button in the keyboard.
- To copy some text: first select the exact text you want to copy, which usually also brings up the text selection bar, then click the `copy` button in bar.
- To paste text into a text box, first long press the text box, then usually the text selection bar will appear with a `paste` button in it.
- When typing into a text field, sometimes an auto-complete dropdown list will appear. This usually indicating this is a enum field and you should try to select the best match by clicking the corresponding one in the list.
Action Related:
- Use the `input_text` action whenever you want to type something (including password) instead of clicking characters on the keyboard one by one. Sometimes there is some default text in the text field you want to type in, remember to delete them before typing.
- Consider exploring the screen by using the `swipe` action with different directions to reveal additional content.
- The direction parameter for the `swipe` action can be confusing sometimes as it's opposite to swipe, for example, to view content at the bottom, the `swipe` direction should be set to "up". It has been observed that you have difficulties in choosing the correct direction, so if one does not work, try the opposite as well.
- To open an app if you can not find its icon, you can first press home (if necessary) and swipe up to the app drawer.
- Swipe up means swiping from bottom to top, swipe down means swiping from top to bottom, swipe left means swiping from right to left, swipe right means swiping from left to right.
- Use the `navigate_back` action to close/hide the soft keyboard.
App Related:
- In the Files app, the grid view may cause file names to be displayed incompletely. You can try switching to a different view type or use the search function directly.
- In the Markor app, the save button is located in the top toolbar and is represented by a floppy disk icon.
- If there are no additional requirements, when you need to add a recipe, you should include as much known information as possible, rather than only adding a small portion of the information.
- When you open the Markor app for the first time, there may be a welcome screen. You should tap the "right arrow" in the bottom right corner and the "DONE" button to skip the related information.
- To transfer data between different pages and different applications, you can try storing the needed information in "Memory" instead of using the "Share" function.
- You can make full use of the search function to find your target files within a folder/directory or your target text in a long document.
- You may scroll down or up to visit the full content of a document or a list. The important infomation in the current list should be stored in the "Memory" before scrolling; otherwise you will forget it.
-- If a blank area appears at the bottom, or if the content does not change after scrolling down, it means you have reached the end.
- When continuously scrolling through a list to find a specific item, you can briefly record the elements currently displayed on the screen in "Memory" to avoid endlessly scrolling even after reaching the bottom of the list.
- To rename a note in Markor, you should first return to the note list, long press the item to be renamed, and then click the "A" button on the right top corner.
- To delete a note in Markor, you should first return to the note list, long press the item to be deleted, and then click the "trash bin" button on the right top corner.
- To set up a timer, you should input the digits from left to right. For example, you want to set a timer for 1 minute and 23 seconds. When you input the first "1", the time changes from 00h00m00s to 00h00m01s. Then, you input the second "2", the time changes from 00h00m01s to 00h00m12s. Finally, you input the third "3", the time changes from 00h00m12s to 00h01m23s. Do be confused by the intermediate results.
- When adding a bill in Pro Expense, the bill category is a scrollable list. You can scroll through this list to discover more categories.
- The calendar app does not automatically set the duration of an event. You need to manually adjust the interval between the start time and end time to control the event's duration.
- In certain views (such as the month view), the calendar app may not display the full event title. To see the complete title, you need to switch to the day view or open the event details.
"""

    return prompt


def get_pc_prompt(task, history, memory, history_images=None):
    action_space = """
### {left,right,middle}_click

Call rule: `{left,right,middle}_click(start_box='[x,y]', element_info='')`
{
    'name': ['left_click', 'right_click', 'middle_click'],
    'description': 'Perform a left/right/middle mouse click at the specified coordinates on the screen.',
    'parameters': {
        'type': 'object',
        'properties': {
            'start_box': {
                'type': 'array',
                'items': {
                    'type': 'integer'
                },
                'description': 'Coordinates [x,y] where to perform the click, normalized to 0-999 range.'
            },
            'element_info': {
                'type': 'string',
                'description': 'Optional text description of the UI element being clicked.'
            }
        },
        'required': ['start_box']
    }
}

### hover

Call rule: `hover(start_box='[x,y]', element_info='')`
{
    'name': 'hover',
    'description': 'Move the mouse pointer to the specified coordinates without performing any click action.',
    'parameters': {
        'type': 'object',
        'properties': {
            'start_box': {
                'type': 'array',
                'items': {
                    'type': 'integer'
                },
                'description': 'Coordinates [x,y] where to move the mouse pointer, normalized to 0-999 range.'
            },
            'element_info': {
                'type': 'string',
                'description': 'Optional text description of the UI element being hovered over.'
            }
        },
        'required': ['start_box']
    }
}

### left_double_click

Call rule: `left_double_click(start_box='[x,y]', element_info='')`
{
    'name': 'left_double_click',
    'description': 'Perform a left mouse double-click at the specified coordinates on the screen.',
    'parameters': {
        'type': 'object',
        'properties': {
            'start_box': {
                'type': 'array',
                'items': {
                    'type': 'integer'
                },
                'description': 'Coordinates [x,y] where to perform the double-click, normalized to 0-999 range.'
            },
            'element_info': {
                'type': 'string',
                'description': 'Optional text description of the UI element being double-clicked.'
            }
        },
        'required': ['start_box']
    }
}

### left_drag

Call rule: `left_drag(start_box='[x1,y1]', end_box='[x2,y2]', element_info='')`
{
    'name': 'left_drag',
    'description': 'Drag the mouse from starting coordinates to ending coordinates while holding the left mouse button.',
    'parameters': {
        'type': 'object',
        'properties': {
            'start_box': {
                'type': 'array',
                'items': {
                    'type': 'integer'
                },
                'description': 'Starting coordinates [x1,y1] for the drag operation, normalized to 0-999 range.'
            },
            'end_box': {
                'type': 'array',
                'items': {
                    'type': 'integer'
                },
                'description': 'Ending coordinates [x2,y2] for the drag operation, normalized to 0-999 range.'
            },
            'element_info': {
                'type': 'string',
                'description': 'Optional text description of the UI element being dragged.'
            }
        },
        'required': ['start_box', 'end_box']
    }
}

### key

Call rule: `key(keys='')`
{
    'name': 'key',
    'description': 'Simulate pressing a single key or combination of keys on the keyboard.',
    'parameters': {
        'type': 'object',
        'properties': {
            'keys': {
                'type': 'string',
                'description': 'The key or key combination to press. Use '+' to separate keys in combinations (e.g., 'ctrl+c', 'alt+tab').'
            }
        },
        'required': ['keys']
    }
}

### type

Call rule: `type(content='')`
{
    'name': 'type',
    'description': 'Type text content into the currently focused text input field. This action only performs typing and does not handle field activation or clearing.',
    'parameters': {
        'type': 'object',
        'properties': {
            'content': {
                'type': 'string',
                'description': 'The text content to be typed into the active text field.'
            }
        },
        'required': ['content']
    }
}

### scroll

Call rule: `scroll(start_box='[x,y]', direction='', step=5, element_info='')`
{
    'name': 'scroll',
    'description': 'Scroll an element at the specified coordinates in the specified direction by a given number of wheel steps.',
    'parameters': {
        'type': 'object',
        'properties': {
            'start_box': {
                'type': 'array',
                'items': {
                    'type': 'integer'
                },
                'description': 'Coordinates [x,y] of the element or area to scroll, normalized to 0-999 range.'
            },
            'direction': {
                'type': 'string',
                'enum': ['down', 'up'],
                'description': 'The direction to scroll: 'down' or 'up'.'
            },
            'step': {
                'type': 'integer',
                'default': 5,
                'description': 'Number of wheel steps to scroll, default is 5.'
            },
            'element_info': {
                'type': 'string',
                'description': 'Optional text description of the UI element being scrolled.'
            }
        },
        'required': ['start_box', 'direction']
    }
}

### WAIT

Call rule: `WAIT()`
{
    'name': 'WAIT',
    'description': 'Wait for 5 seconds before proceeding to the next action.',
    'parameters': {
        'type': 'object',
        'properties': {},
        'required': []
    }
}

### DONE

Call rule: `DONE()`
{
    'name': 'DONE',
    'description': 'Indicate that the current task has been completed successfully and no further actions are needed.',
    'parameters': {
        'type': 'object',
        'properties': {},
        'required': []
    }
}

### FAIL

Call rule: `FAIL()`
{
    'name': 'FAIL',
    'description': 'Indicate that the current task cannot be completed or is impossible to accomplish.',
    'parameters': {
        'type': 'object',
        'properties': {},
        'required': []
    }
}"""

    USER_TEMPLATE_HEAD = """You are a GUI Agent, and your primary task is to respond accurately to user requests or questions. In addition to directly answering the user's queries, you can also use tools or perform GUI operations directly until you fulfill the user's request or provide a correct answer. You should carefully read and understand the images and questions provided by the user, and engage in thinking and reflection when appropriate. The coordinates involved are all represented in thousandths (0-999).

# Task:
{task}

# Task Platform
Ubuntu

# Action Space
{action_space}

# Historical Actions and Current Memory
History:"""

    USER_TEMPLATE_TAIL = """
Memory:
{memory}
# Output Format
Plain text explanation with action(param='...')
Memory:
[{{"key": "value"}}, ...]

# Some Additional Notes
- I'll give you the most recent 4 history screenshots(shrunked to 50%*50%) along with the historical action steps.
- You should put the key information you *have to remember* in a seperated memory part and I'll give it to you in the next round. The content in this part should be a dict list. If you no longer need some given information, you should remove it from the memory. Even if you don't need to remember anything, you should also output an empty list.
- My computer's password is "password", feel free to use it when you need sudo rights.
- For the thunderbird account "anonym-x2024@outlook.com", the password is "gTCI";=@y7|QJ0nDa_kN3Sb&>".

Current Screenshot:
"""

    head_text = USER_TEMPLATE_HEAD.format(task=task, action_space=action_space)

    total_history_steps = len(history)
    history_image_count = len(history_images) if history_images else 0
    content = []
    current_text = head_text

    for step_idx in range(total_history_steps):
        step_num = step_idx + 1
        history_response = history[step_idx]
        parsed = parse_pc_response(history_response)
        action_text = parsed.get("action", "")
        thought_text = parsed.get("action_text", "")
        bot_thought = (
            thought_text.replace(action_text, "").strip()
            if thought_text and action_text
            else ""
        )
        if step_idx < total_history_steps - history_image_count:
            # For steps beyond the last 4, use text placeholder
            current_text += f"\nstep {step_num}: Screenshot:(Omitted in context.) Thought: {bot_thought}\nAction: {action_text}"
        else:
            # For the last 4 steps, insert images
            current_text += f"\nstep {step_num}: Screenshot:"
            content.append({"type": "text", "text": current_text})
            img_idx = step_idx - (total_history_steps - history_image_count)
            if img_idx < len(history_images):
                content.append(
                    {"type": "image_url", "image_url": {"url": history_images[img_idx]}}
                )
            current_text = f" Thought: {bot_thought}\nAction: {action_text}"
    tail_text = USER_TEMPLATE_TAIL.format(memory=memory)
    current_text += tail_text
    content.append({"type": "text", "text": current_text})
    return content


def parse_mobile_response(response):
    pattern = r"Memory:(.*?)Reason:(.*?)Action:(.*)"
    match = re.search(pattern, response, re.DOTALL)
    if not match:
        return None

    memory = match.group(1).strip()
    reason = match.group(2).strip()
    action = match.group(3).strip()

    if "<|begin_of_box|>" in action:
        action = action[
            action.index("<|begin_of_box|>") + len("<|begin_of_box|>") : action.rindex(
                "<|end_of_box|>"
            )
        ]

    parsed_action = None
    if action.startswith("{"):
        parsed_action = json.loads(action)

    return {
        "memory": memory,
        "reason": reason,
        "action": action,
        "parsed_action": parsed_action,
    }


def parse_pc_response(response):
    pattern = r"<\|begin_of_box\|>(.*?)<\|end_of_box\|>"
    match = re.search(pattern, response)
    if match:
        action = match.group(1).strip()
    else:
        downgraded_box_pattern = r"[\w_]+\([^)]*\)"
        matched = re.findall(downgraded_box_pattern, response)
        action = matched[0] if len(matched) > 0 else None
    if "</think>" in response:
        answer_pattern = r"</think>(.*?)Memory:"
    else:
        answer_pattern = r"^(.*?)Memory:"
    answer_match = re.search(answer_pattern, response, re.DOTALL)
    action_text = answer_match.group(1).strip() if answer_match else None
    if action_text:
        action_text = (
            action_text.replace(" <|begin_of_box|> ", "")
            .replace(" <|end_of_box|> ", "")
            .replace("<|begin_of_box|>", "")
            .replace("<|end_of_box|>", "")
        )

    memory_pattern = r"Memory:(.*?)$"
    memory_match = re.search(memory_pattern, response, re.DOTALL)
    memory = memory_match.group(1).strip() if memory_match else "[]"

    return {"action": action, "action_text": action_text, "memory": memory}


def get_web_prompt(task, web_url, web_elements, memory, history):
    from datetime import datetime, timedelta

    USER_PROMPT = """
You are a GUI Agent, and your primary task is to respond accurately to user requests or questions. In addition to directly answering the user's queries, you can also use tools or perform GUI operations directly until you fulfill the user's request or provide a correct answer. You should carefully read and understand the images and questions provided by the user, and engage in thinking and reflection when appropriate. The coordinates involved are all represented in thousandths (0-999).

# Task:
{TASK}, Please interact with {Web} and get the answer. The current time in Beijing is {Time}.

# Task Platform
Web

# Action Space
Action should STRICTLY follow the format:
    - Click [Numerical_Label]. For example the Action \"Click [1]\" means clicking on the web element with a Numerical_Label of \"1\".
    - Type [Numerical_Label]; [The input content]. For example the Action \"Type [2]; [5$]\" means typing \"5$\" in the web element with a Numerical_Label of \"2\".
    - Scroll [Numerical_Label or WINDOW]; [up or down]. For example the Action \"Scroll [6]; [up]\" means scrolling up in the web element with a Numerical_Label of \"6\".
    - Wait. For example the Action \"Wait\" means waiting for 5 seconds.
    - GoBack. For example the Action \"GoBack\" means going back to the previous webpage.
    - Bing. For example the Action \"Bing\" means jumping to the Bing search page.
    - ANSWER; <content>The content of the answer</content>. For example the Action \"ANSWER; <content>Guatemala</content>\" means answering the task with \"Guatemala\".
    - Key; [The key name]. For example the Action \"Key; [Return]\" means pressing the Enter key

# Historical Actions and Current Memory
You have **already performed the following actions** (format: Thought,Action,The Observation after the Action):
{PREVIOUS_ACTIONS}

The \"Memory\" in the current step as follow:
Memory:{Memory}

# Output Format
Your reply should strictly follow the format:
Thought: {Your brief thoughts (briefly summarize the info that will help ANSWER)}
Action: {One Action format you choose}
Memory_Updated: {The latest version of memory generated by modifying or supplementing the original memory content based on the visual information in the current screenshot.}

# Some Additional Notes
A. The provided image is a screenshot of the webpage you are viewing at this step. This screenshot will feature Numerical Labels placed in the TOP LEFT corner of each Web Element. Carefully analyze the visual information to identify the Numerical Label corresponding to the Web Element that requires interaction, then follow the guidelines and choose one of the following actions:
    1. Click a Web Element.
    2. Delete existing content in a textbox and then type content. 
    3. Scroll up or down. Multiple scrolls are allowed to browse the webpage. Pay attention!! The default scroll is the whole window. If the scroll widget is located in a certain area of the webpage, then you have to specify a Web Element in that area. I would hover the mouse there and then scroll.
    4. Wait. Typically used to wait for unfinished webpage processes, with a duration of 5 seconds.
    5. Go back, returning to the previous webpage.
    6. Bing, directly jump to the Bing search page. When you can't find information in some websites, try starting over with Bing.
    7. Key, press the key, only the 'Return' key can be pressed.
    8. Answer. This action should only be chosen when all questions in the task have been solved.
B. I've provided the tag name of each element and the text it contains (if text exists). Note that <textarea> or <input> may be textbox, but not exactly. Please focus more on the screenshot and then refer to the textual information.
{web_text}
C. The \"Memory\" only stores the information obtained from the web page that is relevant to the task,  and the \"Memory\" is strictly in JSON format. For example: {\"user_email_address\": \"test@163.com\", \"user_email_password\": \"123456\", \"jack_email_address\": \"jack@163.com\"}. The \"Memory\" does not include future plans, descriptions of current actions, or other reflective content; it only records visual information that is relevant to the task obtained from the screenshot.
D. Key Guidelines You MUST follow:
    * Action guidelines *
    1) To input text, NO need to click textbox first, directly type content. After typing, the system automatically hits `ENTER` key. Sometimes you should click the search button to apply search filters. Try to use simple language when searching.  
    2) You must Distinguish between textbox and search button, don't type content into the button! If no textbox is found, you may need to click the search button first before the textbox is displayed. 
    3) Execute only one action per iteration. 
    4) STRICTLY Avoid repeating the same action if the webpage remains unchanged. You may have selected the wrong web element or numerical label. Continuous use of the Wait is also NOT allowed.
    5) When a complex Task involves multiple questions or steps, select \"ANSWER\" only at the very end, after addressing all of these questions (steps). Flexibly combine your own abilities with the information in the web page. Double check the formatting requirements in the task when ANSWER. 
    6) You can only interact with web elements in the screenshot that have s numerical label.Before giving the action, double-check that the numerical label appears on the screen.
    7) If any web elements with numerical labels in the screenshot have not finished loading, you need to wait for them to load completely.
    * Web Browsing Guidelines *
    1) Don't interact with useless web elements like Login, Sign-in, donation that appear in Webpages. Pay attention to Key Web Elements like search textbox and menu.
    2) Vsit video websites like YouTube is allowed BUT you can't play videos. Clicking to download PDF is allowed and will be analyzed by the Assistant API.
    3) Focus on the numerical labels in the TOP LEFT corner of each rectangle (element). Ensure you don't mix them up with other numbers (e.g. Calendar) on the page.
    4) Focus on the date in task, you must look for results that match the date. It may be necessary to find the correct year, month and day at calendar.
    5）During the process of browsing web page content, to ensure the complete acquisition of the target content, it may be necessary to scroll down the page until confirming the appearance of the end marker for the target content. For example, when new webpage information appears, or the webpage scroll bar has reached the bottom, etc.
    6) When you work on the github website, use \"Key; [Return]\" to start a search.
    7) Try your best to find the answer that best fits the task, if any situations that do not meet the task requirements occur during the task, correct the mistakes promptly.
"""
    history_text = ""
    if history:
        for idx, h in enumerate(history[-15:]):
            history_text += f"{idx}.{h}\n"
    USER_PROMPT = USER_PROMPT.strip()
    prompt = (
        USER_PROMPT.replace("{TASK}", task)
        .replace("{Web}", web_url)
        .replace("{web_text}", web_elements)
        .replace("{PREVIOUS_ACTIONS}", history_text)
        .replace("{Memory}", memory)
    )
    beijing_time = datetime.now()
    time = beijing_time.strftime("%Y-%m-%d, %I:00 %p")
    prompt = prompt.replace("{Time}", time)  # Placeholder for Beijing time
    return prompt


def parse_web_response(response):
    pattern = r"Thought:|Action:|Memory_Updated:"
    answer = re.findall(r"<answer>(.*?)</answer>", response, re.DOTALL)
    if not answer:
        return None

    response_split = re.split(pattern, answer[0])
    if len(response_split) < 4:
        return None

    thought = response_split[1].strip()
    action = response_split[2].strip()
    memory_str = response_split[3].strip()

    memory = {}
    if memory_str:
        memory = json.loads(memory_str)

    return {"thought": thought, "action": action, "memory": memory}


def call_openai_api(messages, client, model="GLM-4.1V-Thinking-FlashX"):
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        max_tokens=8192,
        temperature=0.001,
        extra_body={
            "skip_special_tokens": False,
        },
    )
    return response.choices[0].message.content


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--mode",
        choices=["mobile", "pc", "web"],
        required=True,
        help="Choose mode: mobile, pc, or web",
    )
    parser.add_argument(
        "--api-url",
        default="https://open.bigmodel.cn/api/paas/v4",
        help="OpenAI compatible API endpoint (without /chat/completions)",
    )
    parser.add_argument(
        "--api-key", default="dummy", help="API key (use 'dummy' for local vLLM)"
    )
    parser.add_argument("--model", default="GLM-4.5V", help="Model name")
    parser.add_argument("--image-path", required=True, help="Path to screenshot image")
    parser.add_argument("--task", required=True, help="Task description")
    parser.add_argument("--history", default="[]", help="JSON string of history")
    parser.add_argument("--memory", default="[]", help="Memory for pc/web mode")
    parser.add_argument("--web-url", default="", help="Web URL for web mode")
    parser.add_argument(
        "--web-elements", default="", help="Web elements text for web mode"
    )
    parser.add_argument(
        "--history-images", default="[]", help="JSON string of history image paths"
    )

    args = parser.parse_args()

    history = json.loads(args.history) if args.history != "[]" else []
    image_base64 = encode_image_to_base64(args.image_path)

    history_image_paths = (
        json.loads(args.history_images) if args.history_images != "[]" else []
    )
    history_images_bytes = load_history_images_from_paths(history_image_paths)
    history_images_urls = build_history_images(history_images_bytes)

    client = OpenAI(base_url=args.api_url, api_key=args.api_key)

    messages = []
    if args.mode == "mobile":
        prompt = get_mobile_prompt(args.task, history)
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "image_url", "image_url": {"url": image_base64}},
                    {"type": "text", "text": prompt},
                ],
            }
        ]

    elif args.mode == "pc":
        content = get_pc_prompt(args.task, history, args.memory, history_images_urls)
        # Add current screenshot
        content.append({"type": "image_url", "image_url": {"url": image_base64}})
        messages = [{"role": "user", "content": content}]

    elif args.mode == "web":
        prompt = get_web_prompt(
            args.task, args.web_url, args.web_elements, args.memory, history
        )
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "image_url", "image_url": {"url": image_base64}},
                    {"type": "text", "text": prompt},
                ],
            }
        ]

    response = call_openai_api(messages, client, args.model)
    if response:
        if args.mode == "mobile":
            parsed = parse_mobile_response(response)
        elif args.mode == "pc":
            parsed = parse_pc_response(response)
        elif args.mode == "web":
            parsed = parse_web_response(response)

        print("\n\n ======= Original response ======= \n")
        print(response)

        print("\n\n ======= Parsed response ======= \n")
        print(parsed)

        if history_images_urls:
            print(f"\n\n ======= History Images Info ======= \n")
            print(f"Number of history images processed: {len(history_images_urls)}")


if __name__ == "__main__":
    main()
