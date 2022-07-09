def notion_richtext_to_markdown(block):
    md = ""
    prev_text = False
    for subblock in block:
        prefix = ""
        suffix = ""
        text = subblock["text"]["content"]
        if subblock["annotations"]["code"]:
            prefix = "`" + prefix
            suffix = suffix + "`"
        if subblock["annotations"]["strikethrough"]:
            prefix = "~~" + prefix
            suffix = suffix + "~~"
        if subblock["annotations"]["italic"]:
            prefix = "_" + prefix
            suffix = suffix + "_"
        if subblock["annotations"]["bold"]:
            prefix = "**" + prefix
            suffix = suffix + "**"
        if subblock["href"]:
            prefix = "[" + prefix
            suffix = suffix + "](" + subblock["href"] + ")"
        if prefix == "" and suffix == "":
            # There's no annotations, so this is just content.
            # If the previous one was just content, then it's a new paragraph, so start a new paragraph
            if prev_text:
                prefix = "\n\n"
            else:
                # This is just content so set prev_text
                prev_text = True
        else:
            # This is't just content, so unset prev_text
            prev_text = False
        md += f"{prefix}{text.strip()}{suffix} "
    return md
