# Ask a question in the voice command and the model will answer it.
model ask <user.text>$:
    result = user.gpt_answer_question(text)
    user.paste(result)

# Runs a model prompt on the selected text; inserts with paste by default
#   Example: `model fix grammar below`
#   Example: `model explain this`
model <user.modelPrompt> [this] [{user.modelInsertionMethod}]$:
    text = edit.selected_text()
    result = user.gpt_apply_prompt(modelPrompt, text)
    user.gpt_insert_response(result, modelInsertionMethod or "")

# Runs an arbitrary prompt on the selected text; inserts with paste by default
#   Example: `model please translate this into English`
#   Example: `model please reformat this code in a more imperative style clipped`
model please <user.text> [{user.modelInsertionMethod}]$:
    prompt = user.text
    txt = edit.selected_text()
    result = user.gpt_apply_prompt(prompt, txt)
    user.gpt_insert_response(result, modelInsertionMethod or "")

# Applies an arbitrary prompt from the clipboard to selected text and pastes the result.
# Useful for applying complex/custom prompts that need to be drafted in a text editor.
model apply [from] clip$:
    prompt = clip.text()
    text = edit.selected_text()
    result = user.gpt_apply_prompt(prompt, text)
    user.paste(result)

# Shows the list of available prompts
model help$: user.gpt_help()

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