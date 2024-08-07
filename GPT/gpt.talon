# Shows the list of available prompts
model help$: user.gpt_help()

# Runs a model prompt on the selected text; inserts with paste by default
#   Example: `model fix grammar below` -> Fixes the grammar of the selected text and pastes below
#   Example: `model explain this` -> Explains the selected text and pastes in place
#   Example: `model fix grammar clip to browser` -> Fixes the grammar of the text on the clipboard and opens in browser`
model <user.modelPrompt> [{user.modelSource}] [{user.modelDestination}]:
    text = user.gpt_get_source_text(modelSource or "")
    result = user.gpt_apply_prompt(modelPrompt, text)
    user.gpt_insert_response(result, modelDestination or "")

# Select the last GPT response so you can edit it further
model take response: user.gpt_select_last()

# Applies an arbitrary prompt from the clipboard to selected text and pastes the result.
# Useful for applying complex/custom prompts that need to be drafted in a text editor.
model apply [from] clip$:
    prompt = clip.text()
    text = edit.selected_text()
    result = user.gpt_apply_prompt(prompt, text)
    user.paste(result)

# Reformat the last dictation with additional context or formatting instructions
model [nope] that was <user.text>$:
    result = user.gpt_reformat_last(text)
    user.paste(result)
    
# Selects all text and runs a model prompt on the selected text and pastes the result.
model fix message$:
    edit.select_all()
    text = edit.selected_text()
    result = user.gpt_apply_prompt("Fix any mistakes or irregularities in grammar, spelling, or formatting. Keep the language the text currently is written in. The text was created used voice dictation. Thus, there is likely to be issues regarding homophones and other misrecognitions. Do not change the tone. Do not change the original structure of the text.", text)
    user.paste(result)
    user.select_left_and_check(".")