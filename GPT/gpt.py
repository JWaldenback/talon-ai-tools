import json
import os
from typing import Any, ClassVar, Literal

import requests
from talon import Module, actions, clip, imgui, settings

from ..lib.HTMLBuilder import Builder
from ..lib.modelHelpers import generate_payload, notify
from ..lib.pureHelpers import strip_markdown

mod = Module()


class GuiState:
    text_to_confirm: ClassVar[str] = ""


@imgui.open()
def confirmation_gui(gui: imgui.GUI):
    gui.text("Confirm model output before pasting")
    gui.line()
    gui.spacer()
    gui.text(GuiState.text_to_confirm)

    gui.spacer()
    if gui.button("Paste model output"):
        actions.user.paste_model_confirmation_gui()

    gui.spacer()
    if gui.button("Copy model output"):
        actions.user.copy_model_confirmation_gui()

    gui.spacer()
    if gui.button("Deny model output"):
        actions.user.close_model_confirmation_gui()


def gpt_query(prompt: str, content: str) -> str:
    url = settings.get("user.model_endpoint")

    headers, data = generate_payload(prompt, content)
    response = requests.post(url, headers=headers, data=json.dumps(data))

    match response.status_code:
        case 200:
            notify("GPT Task Completed")
            resp = response.json()["choices"][0]["message"]["content"].strip()
            formatted_resp = strip_markdown(resp)
            return formatted_resp

        case _:
            notify("GPT Failure: Check the Talon Log")
            raise Exception(response.json())


@mod.action_class
class UserActions:
    def gpt_answer_question(text_to_process: str) -> str:
        """Answer an arbitrary question"""
        prompt = """
        Generate text that satisfies the question or request given in the input.
        """
        return gpt_query(prompt, text_to_process)

    def gpt_blend(source_text: str, destination_text: str):
        """Blend all the source text and send it to the destination"""
        prompt = f"""
        Act as a text transformer. I'm going to give you some source text and destination text, and I want you to modify the destination text based on the contents of the source text in a way that combines both of them together. Use the structure of the destination text, reordering and renaming as necessary to ensure a natural and coherent flow. Please return only the final text with no decoration for insertion into a document in the specified language.

        Here is the destination text:
        ```
        {destination_text}
        ```

        Please return only the final text. What follows is all of the source texts separated by '---'.
        """
        return gpt_query(prompt, source_text)

    def gpt_blend_list(source_text: list[str], destination_text: str):
        """Blend all the source text as a list and send it to the destination"""

        return actions.user.gpt_blend("\n---\n".join(source_text), destination_text)

    def gpt_generate_shell(text_to_process: str) -> str:
        """Generate a shell command from a spoken instruction"""
        shell_name = settings.get("user.model_shell_default")
        if shell_name is None:
            raise Exception("GPT Error: Shell name is not set. Set it in the settings.")

        prompt = f"""
        Generate a {shell_name} shell command that will perform the given task.
        Only include the code. Do not include any comments, backticks, or natural language explanations. Do not output the shell name, only the code that is valid {shell_name}.
        Condense the code into a single line such that it can be ran in the terminal.
        """

        result = gpt_query(prompt, text_to_process)
        return result

    def gpt_generate_sql(text_to_process: str) -> str:
        """Generate a SQL query from a spoken instruction"""

        prompt = """
       Generate SQL to complete a given request.
       Output only the SQL in one line without newlines.
       Do not output comments, backticks, or natural language explanations.
       Prioritize SQL queries that are database agnostic.
        """
        return gpt_query(prompt, text_to_process)

    def add_to_confirmation_gui(model_output: str):
        """Add text to the confirmation gui"""
        GuiState.text_to_confirm = model_output
        confirmation_gui.show()

    def close_model_confirmation_gui():
        """Close the model output without pasting it"""
        GuiState.text_to_confirm = ""
        confirmation_gui.hide()

    def copy_model_confirmation_gui():
        """Copy the model output to the clipboard"""
        clip.set_text(GuiState.text_to_confirm)
        GuiState.text_to_confirm = ""

        confirmation_gui.hide()

    def paste_model_confirmation_gui():
        """Paste the model output"""
        actions.user.paste(GuiState.text_to_confirm)
        GuiState.text_to_confirm = ""
        confirmation_gui.hide()

    def paste_and_select(result: str):
        """Paste and select the pasted text"""

        actions.user.paste(result)

        for _ in result:
            actions.edit.extend_left()

    def gpt_apply_prompt(prompt: str, text_to_process: str | list[str]) -> str:
        """Apply an arbitrary prompt to arbitrary text"""
        text_to_process = (
            " ".join(text_to_process)
            if isinstance(text_to_process, list)
            else text_to_process
        )
        return gpt_query(prompt, text_to_process)

    def gpt_help():
        """Open the GPT help file in the web browser"""
        # get the text from the file and open it in the web browser
        current_dir = os.path.dirname(__file__)
        file_path = os.path.join(current_dir, "staticPrompt.talon-list")
        with open(file_path, "r") as f:
            lines = f.readlines()[2:]

        builder = Builder()
        builder.h1("Talon GPT Prompt List")
        for line in lines:
            if "##" in line:
                builder.h2(line)
            else:
                builder.p(line)

        builder.render()

    def gpt_reformat_last(how_to_reformat: str):
        """Reformat the last model output"""
        PROMPT = f"""The last phrase was written using voice dictation. It has an error with spelling, grammar, or just general misrecognition due to a lack of context. Please reformat the following text to correct the error with the context that it was {how_to_reformat}."""
        last_output = actions.user.get_last_phrase()
        if last_output:
            actions.user.clear_last_phrase()
            return gpt_query(PROMPT, last_output)
        else:
            notify("No text to reformat")
            raise Exception("No text to reformat")

    def gpt_insert_response(result: str, method: str = ""):
        """Insert a GPT result in a specified way"""

        match method:
            case "above":
                actions.key("left")
                actions.edit.line_insert_up()
                actions.user.paste(result)
            case "below":
                actions.key("right")
                actions.edit.line_insert_down()
                actions.user.paste(result)
            case "clipped":
                clip.set_text(result)
            case "selected":
                actions.user.paste_and_select(result)
            case "browser":
                builder = Builder()
                builder.h1("Talon GPT Result")
                builder.p(result)
                builder.render()
            case _:
                actions.user.paste(result)

    def cursorless_or_paste_helper(
        cursorless_destination: Any | Literal[0], text: str
    ) -> None:
        """If a destination is specified, use cursorless to insert text. Otherwise, paste the text."""
        if cursorless_destination == 0:
            actions.user.paste(text)
        else:
            actions.user.cursorless_insert(cursorless_destination, text)
