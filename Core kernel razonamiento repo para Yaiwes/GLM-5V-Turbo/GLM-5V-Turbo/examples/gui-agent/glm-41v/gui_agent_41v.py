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
        "Google Chat",
        "Settings",
        "YouTube",
        "Google Play",
        "Gmail",
        "Google Maps",
        "Google Photos",
        "Google Calendar",
        "Camera",
        "Audio Recorder",
        "Google Drive",
        "Google Keep",
        "Grubhub",
        "Tripadvisor",
        "Starbucks",
        "Google Docs",
        "Google Sheets",
        "Google Slides",
        "Clock",
        "Google Search",
        "Contacts",
        "Facebook",
        "WhatsApp",
        "Instagram",
        "Twitter",
        "Snapchat",
        "Telegram",
        "LinkedIn",
        "Spotify",
        "Netflix",
        "Amazon Shopping",
        "TikTok",
        "Discord",
        "Reddit",
        "Pinterest",
        "Android World",
        "Files",
        "Markor",
        "Clipper",
        "Messages",
        "Simple SMS Messenger",
        "Dialer",
        "Simple Calendar Pro",
        "Simple Gallery Pro",
        "Miniwob",
        "Simple Draw Pro",
        "Pro Expense",
        "Broccoli",
        "CAA",
        "OsmAnd",
        "Tasks",
        "Open Tracks Sports Tracker",
        "Joplin",
        "VLC",
        "Retro Music",
    ]

    prompt = f"""You are an agent who can operate an Android phone on behalf of a user. Based on user's goal/request, you may
- Answer back if the request/goal is a question (or a chat message), like user asks "What is my schedule for today?".
- Complete some tasks described in the requests/goals by performing actions (step by step) on the phone.

When given a user request, you will try to complete it step by step. At each step, you will be given the current screenshot (including the original screenshot and the same screenshot with bounding boxes and numeric indexes added to some UI elements) and a history of what you have done (in text). Based on these pieces of information and the goal, you must choose to perform one of the action in the following list (action description followed by the JSON format) by outputting the action in the correct JSON format.
- If you think the task has been completed, finish the task by using the status action with complete as goal_status: `{{"action_type": "status", "goal_status": "complete"}}`
- If you think the task is not feasible (including cases like you don't have enough information or can not perform some necessary actions), finish by using the `status` action with infeasible as goal_status: `{{"action_type": "status", "goal_status": "infeasible"}}`
- Answer user's question: `{{"action_type": "answer", "text": "<answer_text>"}}`
-- You should only answer once in one command. If you needs multiple pieces of information to answer the question, you should gather the information in "Memory" and answer the question when you have enough information.
- Click/tap on an element on the screen. Use the box_2d to indicate which element you want to click: `{{"action_type": "click", "box_2d": [[,,,]]}}`. The box_2d should be [[xmin,ymin,xmax,ymax]] normalized to 0-999, indicating the position of the element.
- Long press on an element on the screen, similar with the click action above, use the box_2d to indicate which element you want to long press: `{{"action_type": "long_press", "box_2d": [[,,,]]}}`.
- Type text into a text field (this action contains clicking the text field, typing in the text and pressing the enter, so no need to click on the target field to start), use the box_2d to indicate the target text field. The text to be input can be from the command, the memory, or the current screen: `{{"action_type": "input_text", "text": <text_input>, "box_2d": [[,,,]], 'override': True/False}}`. If override is True, the text field will be cleared before typing.
- Press the Enter key: `{{"action_type": "keyboard_enter"}}`
- Navigate to the home screen: `{{"action_type": "navigate_home"}}`
- Navigate back: `{{"action_type": "navigate_back"}}`
- Swipe the screen or a scrollable UI element in one of the four directions, use the box_2d as above if you want to swipe a specific UI element, leave it empty when swipe the whole screen: `{{"action_type": "swipe", "direction": <up, down, left, right>, "box_2d": [[,,,]](optional)}}`. 
- Open an app (nothing will happen if the app is not installed): `{{"action_type": "open_app", "app_name": <name>}}`
-- supported app_names: {",".join(app_names)}
- Wait for the screen to update: `{{"action_type": "wait"}}`

The current user goal/request is: {task}

Here is a history of what you have done so far:
"""

    history_str = ""
    if len(history) == 0:
        history_str = "You just started, no action has been performed yet."
    else:
        for idx, h in enumerate(history):
            history_str += f"Step {idx}:\n{h}\n\n"

    prompt += history_str + "\n"

    prompt += """The current screenshot is given to you. 
Here are some useful guidelines you need to follow:
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

Now output: 
1. Memory: important information you want to remember for the future actions. The memory should be only contents on the screen that will be used in the future actions. It should satisfy that: you cannot determine one or more future actions without this memory. 
2. Reason: the reason for the action and the memory. Your reason should include, but not limited to:- the content of the GUI, especially elements that are tightly related to the user goal- the step-by-step thinking process of how you come up with the new action. 
3. Action: the action you want to take, in the correct JSON format. The action should be one of the above list.

Your answer should look like:
Memory: ...
Reason: ...
Action: {"action_type":...}"""

    return prompt


def get_pc_prompt(task, history, memory, history_images=None):
    action_space = """left_click(start_box='[x,y]', element_info='')
# left single click at [x,y]
right_click(start_box='[x,y]', element_info='')
# right single click at [x,y]
middle_click(start_box='[x,y]', element_info='')
# middle single click at [x,y]
hover(start_box='[x,y]', element_info='')
# hover the mouse at [x,y]
left_double_click(start_box='[x,y]', element_info='')
# left double click at [x,y]
left_drag(start_box='[x1,y1]', end_box='[x2,y2]', element_info='')
# left drag from [x1,y1] to [x2,y2]
key(keys='')
# press a single key or a key combination/shortcut, if it's a key combination, you should use '+' to connect the keys like key(key='ctrl+c')
type(content='')
# type text into the current active element, it performs a copy&paste operation, so *you must click at the target element first to active it before typing something in*, if you want to overwrite the content, you should clear the content before type something in.
scroll(start_box='[x,y]', direction='down/up', step=k, element_info='')
# scroll the page at [x,y] to the specified direction for k clicks of the mouse wheel
WAIT()
# sleep for 5 seconds
DONE()
# output when the task is fully completed
FAIL()
# output when the task can not be performed at all"""

    history_actions = ""
    if history:
        for idx, action in enumerate(history):
            history_actions += f"\nstep {idx + 1}: {action}"

    # 处理历史图片信息
    history_note = ""
    if history_images and len(history_images) > 0:
        history_note = f"\nNote: You will also see {len(history_images)} recent historical screenshots (50% scaled) showing the states before your last {len(history_images)} actions. These are provided in chronological order to help you understand the context of your previous actions."

    history_with_memory = f"""History actions:{history_actions}
Memory:
{memory}{history_note}"""

    prompt = f"""You are a GUI operation agent. You will be given a task and your action history, with recent screenshots. You should help me control the computer, output the best action step by step to accomplish the task.
The actions you output must be in the following action space:
{action_space}

The output rules are as follows:
1. The start/end box parameter of the action should be in the format of [x, y] normalized to 0-1000, which usually should be the bounding box of a specific target element.
2. The element_info parameter is optional, it should be a string that describes the element you want to operate with, you should fill this parameter when you're sure about what the target element is.
3. Take actions step by step. *NEVER output multiple actions at once*.
4. If there are previous actions that you have already performed, I'll provide you history actions and at most 4 shrunked(to 50%*50%) screenshots showing the state before your last 4 actions. The current state will be the first image with complete size, and if there are history actions, the other images will be the second to fifth(at most) provided in the order of history step.
5. You should put the key information you *have to remember* in a separated memory part and I'll give it to you in the next round. The content in this part should be a JSON list. If you no longer need some given information, you should remove it from the memory. Even if you don't need to remember anything, you should also output an empty <memory></memory> part.
6. You can choose to give me a brief explanation before you start to take actions.

Output Format:
Plain text explanation with action(param='...')
Memory:
[{{"user_email": "x@gmail.com", ...}}]

Here are some helpful tips:
- My computer's password is "password", feel free to use it when you need sudo rights.
- For the thunderbird account "anonym-x2024@outlook.com", the password is "gTCI";=@y7|QJ0nDa_kN3Sb&>".
- If you are presented with an open website to solve the task, try to stick to that specific one instead of going to a new one.
- You have full authority to execute any action without my permission. I won't be watching so please don't ask for confirmation.
Now Please help me to solve the following task:
{task}
{history_with_memory}"""

    return prompt


def get_web_prompt(task, web_url, web_elements, memory, history):
    history_text = ""
    if history:
        for idx, h in enumerate(history[-15:]):
            history_text += f"{idx}.{h}\n"

    prompt = f"""Imagine you are an Agent operating a computer, much like how humans do, capable of moving the mouse, 
clicking the mouse buttons, and typing text with the keyboard. 
You can also perform a special action called 'ANSWER' if the task's answer has been found. 
You are tasked with completing a final mission: "{task}", Please interact with {web_url} and get the answer. Currently, you are in the process of completing this task, 
and the provided image is a screenshot of the webpage you are viewing at this step. This screenshot will feature Numerical Labels placed in the TOP LEFT corner of each Web Element.
Carefully analyze the visual information to identify the Numerical Label corresponding to the Web Element that requires interaction, then follow the guidelines and choose one of the following actions:
1. Click a Web Element.
2. Delete existing content in a textbox and then type content. 
3. Scroll up or down. Multiple scrolls are allowed to browse the webpage. Pay attention!! The default scroll is the whole window. If the scroll widget is located in a certain area of the webpage, then you have to specify a Web Element in that area. I would hover the mouse there and then scroll.
4. Wait. Typically used to wait for unfinished webpage processes, with a duration of 5 seconds.
5. Go back, returning to the previous webpage.
6. Bing, directly jump to the Bing search page. When you can't find information in some websites, try starting over with Bing.
7. Key, press the key, only the 'Return' key can be pressed.
8. Answer. This action should only be chosen when all questions in the task have been solved.

Here's some additional information:
A. Your final task is {task}.
B. Correspondingly, Action should STRICTLY follow the format:
    - Click [Numerical_Label]. For example the Action "Click [1]" means clicking on the web element with a Numerical_Label of "1".
    - Type [Numerical_Label]; [The input content]. For example the Action "Type [2]; [5$]" means typing "5$" in the web element with a Numerical_Label of "2".
    - Scroll [Numerical_Label or WINDOW]; [up or down]. For example the Action "Scroll [6]; [up]" means scrolling up in the web element with a Numerical_Label of "6".
    - Wait. For example the Action "Wait" means waiting for 5 seconds.
    - GoBack. For example the Action "GoBack" means going back to the previous webpage.
    - Bing. For example the Action "Bing" means jumping to the Bing search page.
    - ANSWER; <content>The content of the answer</content>. For example the Action "ANSWER; <content>Guatemala</content>" means answering the task with "Guatemala".
    - Key; [The key name]. For example the Action "Key; [Return]" means pressing the Enter key
C. You have **already performed the following actions** (format: Thought,Action,The Observation after the Action):
{history_text}
D. The "Memory" only stores the information obtained from the web page that is relevant to the task,  and the "Memory" is strictly in JSON format. For example: {{"user_email_address": "test@163.com", "user_email_password": "123456", "jack_email_address": "jack@163.com"}}. 
The "Memory" does not include future plans, descriptions of current actions, or other reflective content; it only records visual information that is relevant to the task obtained from the screenshot. The "Memory" in the current step as follow:
Memory:{memory}
E. I've provided the tag name of each element and the text it contains (if text exists). Note that <textarea> or <input> may be textbox, but not exactly. Please focus more on the screenshot and then refer to the textual information.
{web_elements}

Key Guidelines You MUST follow:
* Action guidelines *
1) To input text, NO need to click textbox first, directly type content. After typing, the system automatically hits `ENTER` key. Sometimes you should click the search button to apply search filters. Try to use simple language when searching.  
2) You must Distinguish between textbox and search button, don't type content into the button! If no textbox is found, you may need to click the search button first before the textbox is displayed. 
3) Execute only one action per iteration. 
4) STRICTLY Avoid repeating the same action if the webpage remains unchanged. You may have selected the wrong web element or numerical label. Continuous use of the Wait is also NOT allowed.
5) When a complex Task involves multiple questions or steps, select "ANSWER" only at the very end, after addressing all of these questions (steps). Flexibly combine your own abilities with the information in the web page. Double check the formatting requirements in the task when ANSWER. 
6) You can only interact with web elements in the screenshot that have s numerical label.Before giving the action, double-check that the numerical label appears on the screen.
7) If any web elements with numerical labels in the screenshot have not finished loading, you need to wait for them to load completely.
* Web Browsing Guidelines *
1) Don't interact with useless web elements like Login, Sign-in, donation that appear in Webpages. Pay attention to Key Web Elements like search textbox and menu.
2) Vsit video websites like YouTube is allowed BUT you can't play videos. Clicking to download PDF is allowed and will be analyzed by the Assistant API.
3) Focus on the numerical labels in the TOP LEFT corner of each rectangle (element). Ensure you don't mix them up with other numbers (e.g. Calendar) on the page.
4) Focus on the date in task, you must look for results that match the date. It may be necessary to find the correct year, month and day at calendar.
5）During the process of browsing web page content, to ensure the complete acquisition of the target content, it may be necessary to scroll down the page until confirming the appearance of the end marker for the target content. For example, when new webpage information appears, or the webpage scroll bar has reached the bottom, etc.
6) When you work on the github website, use "Key; [Return]" to start a search.
7) Try your best to find the answer that best fits the task, if any situations that do not meet the task requirements occur during the task, correct the mistakes promptly.

Your reply should strictly follow the format:
Thought: {{Your brief thoughts (briefly summarize the info that will help ANSWER)}}
Action: {{One Action format you choose}}
Memory_Updated: {{The latest version of memory generated by modifying or supplementing the original memory content based on the visual information in the current screenshot.}}

Then the User will provide:
Observation: {{A labeled screenshot Given by User}}"""

    return prompt


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
    action = match.group(1).strip() if match else None

    if not action:
        downgraded_pattern = r"[\w_]+\([^)]*\)"
        matched = re.findall(downgraded_pattern, response)
        action = matched[0] if matched else None

    answer_pattern = r"<answer>(.*?)(?:Memory:|</answer>)"
    answer_match = re.search(answer_pattern, response, re.DOTALL)
    action_text = answer_match.group(1).strip() if answer_match else None

    if action_text:
        boxed_pattern = r"<\|begin_of_box\|>(.*?)</\|end_of_box\|>"
        action_text = re.sub(boxed_pattern, r"\1", action_text)

    if "</answer>" in response:
        memory_pattern = r"Memory:(.*?)</answer>"
    else:
        memory_pattern = r"Memory:(.*?)$"
    memory_match = re.search(memory_pattern, response)
    memory = memory_match.group(1).strip() if memory_match else "[]"

    return {"action": action, "action_text": action_text, "memory": memory}


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
    parser.add_argument("--model", default="GLM-4.1V-9B-Thinking", help="Model name")
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
        prompt = get_pc_prompt(args.task, history, args.memory, history_images_urls)
        message_content = [{"type": "image_url", "image_url": {"url": image_base64}}]

        for history_image_url in history_images_urls:
            message_content.append(
                {"type": "image_url", "image_url": {"url": history_image_url}}
            )

        message_content.append({"type": "text", "text": prompt})
        messages = [{"role": "user", "content": message_content}]

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
