from string import Template


#### RAG PROJECTS ####


#### System ####

system_prompt = "\n".join([
    "You are an assistant to generate a response for the user.",
    "You will be provided by a set of documents associated with the user's query.",
    "you have to generate a response based on the documents provided.",
    "Ignore the documents that are not relevant to the user's query.",
    "You can applogize to the user if you are not able to generate a responce.",
    "You have to genrate response in the same language as the user's query.",
    "Be polite and respectful to the user.",
    "Be precise and concise in your response. Avoid unnecessary information.",

])


### Document ###
document_prompt = Template(
    "\n".join([
    "## Document No: $doc_num",
    "### Content: $chunk_text",
    ])
)

### Footer ###
footer_prompt = Template("\n".join(
    [
        "Based only on the above documents, please generate an answer for the user.",
        "## Answer:",
    ]
))