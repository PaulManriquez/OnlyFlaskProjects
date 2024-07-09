#Standardize the separation of each word in a string 
def standardize_length(text, length):
    words = text.split() #Get each word and save it in a list
    formatted_words = [f'{word:<{length}}' for word in words] #Get each word and give the given separation
    formated = ''.join(formatted_words) # get the new string formated
    return formated + '\n' #Add the new line chacarcter 