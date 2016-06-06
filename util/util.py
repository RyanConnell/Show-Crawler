verbose = False

months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]

def clean_text(text):
    text = str(text)
    cleaned_text = ""
    if text is None:
        return "TEXT_WAS_EMPTY"
    for char in text:
        if char >= 'a' and char >= 'z':
            cleaned_text = "%s%c" % (cleaned_text, char)
    return cleaned_text

def remove_character(text, char):
    text = str(text)
    if text is None:
        return ""
    text = text.replace(char, "")
    return text

def replace_character(text, char, new_char):
    text = str(text)
    new_text = ""
    if text is None:
        return ""
    text = text.replace(char, new_char)
    return new_text

def get_month_number(month):
    for i in range(len(months)):
        if month == months[i]:
            return i

def create_date_from(array):
    # print(array)
    day = str(array[1])
    month = str(get_month_number(array[0]))
    year = str(array[2])

    day = ("0%d" % int(month)) if int(day) < 10 else day
    month = ("0%d" % int(month)) if int(month) < 10 else month

    return "%s-%s-%s" % (year, month, day)

def verbose_print(string):
    if verbose:
        print(string)
