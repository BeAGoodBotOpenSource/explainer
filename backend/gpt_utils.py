import config
import logging, openai

def get_news_jargon(sanitized_string):
    try:
        print(f"Clean_string: {sanitized_string}")
        query_1 = (
            f"Given this sanitized string from an html page: {sanitized_string}"
            ", Return a list of 5 miximum key jargon words and it's definition to understand this news text."
            " Avoid including any potential button text or Privacy Policy related text in the analysis."
        )

        print('Starting GPT API call via model')
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-16k",
            messages=[{"role": "user", "content": query_1}]
        )
        result = response.choices[0].message['content']

        print("Result of get_news_jargon:") 
        print(result)
        return result
    except Exception as e:
        return "Unable to find jargon."

def get_news_big_picture(sanitized_string):
    try:
        query_1 = (
            f"Given this sanitized string from an html page: {sanitized_string}"
            ", Return a one or two sentences of the main news paragraph describing the big picture in easy to read wording"
            " Avoid including any potential button text or Privacy Policy related text in the analysis."
        )

        print('Starting GPT API call via model')
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-16k",
            messages=[{"role": "user", "content": query_1}]
        )
        result = response.choices[0].message['content']

        print("Result of get_news_big_picture.") 
        print(result)
        return result
    except Exception as e:
        return "Unable to find big picture."

def get_news_beneficiary(sanitized_string):
    try:
        query_1 = (
            f"Given this sanitized string from an html page: {sanitized_string}"
            ", Return in one sentence who is or are the beneficiaries from the news."
            " If there is no clear beneficiary, say: There is no clear beneficiary from this text."
        )

        print('Starting GPT API call via model')
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-16k",
            messages=[{"role": "user", "content": query_1}]
        )
        result = response.choices[0].message['content']

        print("Result of get_news_beneficiary.") 
        print(result)
        return result
    except Exception as e:
        return "Unable to find beneficiary."

def get_news_tone(sanitized_string):
    try:
        query_1 = (
            f"Given this sanitized string from an html page: {sanitized_string}"
            ", Return in one sentence if the tone of the text favorites any person in particular."
            " The expectation is that the news is unbiased. If there is no big bias in the text return: No bias in text tone found."
        )

        print('Starting GPT API call via model')
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-16k",
            messages=[{"role": "user", "content": query_1}]
        )
        result = response.choices[0].message['content']

        print("Result of get_news_tone.") 
        print(result)
        return result
    except Exception as e:
        return "Unable to find tone."

def get_news_explanation_full(jargon_and_definitions, big_picture, beneficiary, tone):
    try:
        query_1 = (
            f"Given this sanitized jargon string from an html page: {jargon_and_definitions}."
            f", And this sanitized big_picture string from an html page: {big_picture}."
            f", And this sanitized beneficiary string from an html page: {beneficiary}."
            f", And this sanitized tone string from an html page: {tone}."
            ", Return the these values in html syntax to be displayed in a Chrome Extension result page."
            " Keep in mind that this is the result of a Chrome extension that explains news so the result should display in the same order and with titles of the 4 inputs."
        )

        print('Starting GPT API call via model')
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-16k",
            messages=[{"role": "user", "content": query_1}]
        )
        result = response.choices[0].message['content']

        print("Result of get_news_tone.") 
        print(result)
        return result
    except Exception as e:
        return "Unable to find tone."

def get_news_explanation(sanitized_string):
    try:
        jargon_and_definitions = get_news_jargon(sanitized_string)
        big_picture = get_news_big_picture(sanitized_string)
        beneficiary = get_news_beneficiary(sanitized_string)
        tone = get_news_tone(sanitized_string)
        explanation = get_news_explanation_full(jargon_and_definitions, big_picture, beneficiary, tone)
        return explanation
    except Exception as e:
        return "Unable to find jargon."

def autofill_gpt(form_fields, clean_pdf_text, clean_html):
    query_1 = (
        f"Given these html form fields: {form_fields} and cleaned PDF text: {clean_pdf_text}"
        ", return a dictionary with the id as key and generated value from clean pdf text"
    )

    print('Starting GPT API call 2 via model')
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-16k",
        messages=[{"role": "user", "content": query_1}]
    )
    autofilled_dict = response.choices[0].message['content']

    print("Result of 2nd query. autofilled_dict:")
    print(autofilled_dict) 
    return autofilled_dict

def gpt_filled_dic(gpt_response_with_text):
    query_1 = (
        f"Given this combination of text and a dictionary: {gpt_response_with_text}. only return a string of dictionary"
    )

    print('Starting GPT API call 3 via model')
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-16k",
        messages=[{"role": "user", "content": query_1}]
    )
    cleaned_dict = response.choices[0].message['content']

    print("Result of 3rd query. cleaned_dict:")
    print(cleaned_dict) 
    return cleaned_dict
