import g4f
import re
from selenium import webdriver
import time
from selenium.webdriver.common.by import By

GOOGLE_FORM = "https://docs.google.com/forms/d/1htqr34RNbuSUrn25p7IiZ0ESLnHAnKjAa3iSy77hkQU/viewform?ts=63417cdc&edit_requested=true"


def filter_strings_by_number(strings):
    pattern = re.compile(r'^\d+.')

    filtered_strings = [s for s in strings if pattern.match(s)]

    return filtered_strings


def filter_questions_by_format(questions):
    result = []

    for question in questions:
        if question.strip().startswith(('1.', '2.', '3.', '4.', '5.', '6.', '7.', '8.', '9.', '10.')):
            result.append(question)

    return result



def chat_gpt(message):
    response = g4f.ChatCompletion.create(
        model='gpt-4',
        messages=[{"role": "user",
               "content": message + "\n\n Give me an answer in 1 letter"}],
        stream=False)

    return response

def group_elements_by_letter(elements):
    result = []
    current_group = []

    for element in elements:
        letter = re.split(r'\.|\)|\s', element.text)[0].strip()

        if letter == 'A':
            # Start a new group
            if current_group:
                result.append(current_group)
            current_group = [element]
        else:
            # Add to the current group
            current_group.append(element)

    # Add the last group
    if current_group:
        result.append(current_group)

    return result

def get_all_text_from_element(element):
    text = element.find_element(By.XPATH, "//div/div[1]/span[1]/p").text
    return text

def group_elements_by_starting_letter(lst):
    result = []
    current_group = []

    for item in lst:
        print(item.text)
        first_letter = item['text'].strip()[0].upper()

        if first_letter == 'A' and current_group:
            result.append(current_group)
            current_group = []

        current_group.append(item)

    if current_group:
        result.append(current_group)

    return result


if __name__ == "__main__":
    driver = webdriver.Chrome()

    driver.get(GOOGLE_FORM)
    driver.implicitly_wait(10)


    answer_container = driver.find_element(By.XPATH, "/html/body/div/div[3]/form/div[2]/div/div[2]")

    questions_elements = answer_container.find_elements(By.XPATH, "div[@role='listitem']")


    text_elems = driver.find_elements(By.XPATH, "//div/div[1]/span[1]")

    answer_inputs = driver.find_elements(By.XPATH, "//label/div/div[2]/div/span")

    text = []

    for text_elem in text_elems:
        text.append(text_elem.text)

    questions_only = filter_strings_by_number(text)

    inputs_text = group_elements_by_letter(answer_inputs)


    print(len(inputs_text))

    sum_questions = ""
    for i in range(0, len(inputs_text)):

        options = ' '.join(map(lambda input_text: input_text.text, inputs_text[i]))
        print(str)

        sum_questions += questions_only[i] + options + '\n'

    print(sum_questions)
    response = chat_gpt(sum_questions)
    print(response)
    right_answers = re.findall(r'\b\d+\.\s*([A-Z])\b', response)
    print(right_answers)

    for i in range(0, len(inputs_text)):
        for answer_input in inputs_text[i]:
            if right_answers[i] in answer_input.text:
                print("Cool!")
                answer_input.click()

    time.sleep(7200)
