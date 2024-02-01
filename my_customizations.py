from talon import Module, actions, Context

mod = Module()

@mod.action_class
class Actions:
    def select_left_and_check(search_term: str):
        """sdf"""

ctx=Context()

@ctx.action_class("user")
class UserActions:
    def select_left_and_check(search_term: str):
        actions.edit.extend_left()
        # Get the selected character
        selected_text = actions.edit.selected_text()
        # Check if the selected character is `search_term` and perform an action
        if selected_text == search_term:
            #actions.sleep("3000ms")
            actions.edit.delete()