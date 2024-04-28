import json
import os

import markdown
from dotenv import load_dotenv
from goose3 import Goose
from langchain import PromptTemplate
from langchain.chat_models import ChatOpenAI
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

chat_model = ChatOpenAI(model="gpt-3.5-turbo", temperature=1.2)

with open("templates/extract_news_template.md", "r") as f:
    extract_news_template = f.read()


class NewsArticleSummary(BaseModel):
    title: str = Field(description="Teaser Headline")
    lede: str = Field(description="Intro line, the lede of the story")
    context: str = Field(description="Why this story matters")
    details: str = Field(
        description="Fuller details of the news story, 2 to 3 short sentences"
    )
    who_benefits: str = Field(description="Who benefits as a result of the news story")
    who_loses: str = Field(description="Who loses as a result of the news story")
    # bias: str = Field(
    #     description="Considering the tone of the writing and the subject, describe potential biases"
    # )
    # jargon: str = Field(description="Pick out potential jargon words and explain them")


parser = PydanticOutputParser(pydantic_object=NewsArticleSummary)

prompt_template = PromptTemplate(
    template=extract_news_template,
    input_variables=["title", "content"],
    partial_variables={"format_instructions": parser.get_format_instructions()},
)


def get_news_explanation(raw_html: str) -> str:
    """Return a summary of a news article on a webpage

    Inputs
    ------
    raw_html: str
        The raw HTML of the webpage to extract the news article from.
        Sanitization is handled internally by goose3.

    Returns
    -------
    str
        A summary of the news article as formatted html.
    """

    g = Goose()
    article = g.extract(raw_html=raw_html)
    title = article.title
    content = article.cleaned_text

    prompt = prompt_template.format(title=title, content=content)
    summary = chat_model.predict(prompt)
    summary = json.loads(summary)

    with open("templates/summary_format.md", "r") as f:
        summary_format = f.read()

    summary_md = summary_format.format(
        title=summary["title"],
        lede=summary["lede"],
        context=summary["context"],
        details=summary["details"],
        who_benefits=summary["who_benefits"],
        who_loses=summary["who_loses"],
        # bias=summary["bias"],
        # jargon=summary["jargon"],
    )

    summary_html = markdown.markdown(summary_md)

    return summary_html
