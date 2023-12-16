import csv
import eng_to_ipa as ipa
import jaro
import numpy as np
from playsound import playsound
import math
from scipy import stats

# Define as a global variable the list of words tested
words = ['Blarb', 'Door', 'Bund', 'Lond', 'Fifer', 'Weird', 'Larp', 'Fint', 'Fortry', 'Torp', 'Laugh']

# Calculate similarity index between the ipa transcriptions of the spellings
def calculate_similarity(input_spelling, og_spelling):
    # Retrieve all possible IPA transcriptions
    og_ipa = ipa.convert(og_spelling, retrieve_all=True)
    input_ipa = ipa.convert(input_spelling)
    similarity = 0
    # Give the benefit of the doubt and take the highest matching ipa transcription
    for transcription in og_ipa:
        new_similarity = jaro.jaro_metric(transcription, input_ipa)
        if new_similarity > similarity:
            similarity = new_similarity
    return similarity


# Used for data processing
# Based on data, create a dictionary with words and their average similarity indexes for those who do not spell phonetically
def calculate_non_phonetic_distributions():
    similarities = {}
    with open('non_phonetic_spelling.csv') as file:
        csvFile = csv.reader(file)
        header = next(csvFile)
        # Set up keys of dict
        for word in header:
            similarities[word] = []
        # Go through data to calculate avg similarity index by taking median
        for row in csvFile:
            # Iterate through each word
            for i in range(len(row)):
                og_spelling = header[i]
                input_spelling = row[i]
                similarity_index = calculate_similarity(input_spelling, og_spelling)
                similarities[og_spelling].append(similarity_index)
        # Find mean similarity in each word
        for similarity_index in similarities.keys():
            similarities[similarity_index] = [np.mean(similarities[similarity_index]), np.var(similarities[similarity_index])]
    return similarities

# Used for data processing
# Based on data, create a dictionary with words and their average similarity indexes for those who spell phonetically
def calculate_phonetic_distributions():
    similarities_phonetic = {}
    with open('phonetic_spelling.csv') as file:
        csvFile = csv.reader(file)
        header = next(csvFile)
        # Set up keys of dict
        for word in header:
            similarities_phonetic[word] = []

        # Go through data to calculate avg similarity index by taking mean
        for row in csvFile:
            # Iterate through each word
            for i in range(len(row)):
                og_spelling = header[i]
                input_spelling = row[i]
                similarity_index = calculate_similarity(input_spelling, og_spelling)
                similarities_phonetic[og_spelling].append(similarity_index)
        # Find mean similarity in each word
        for similarity_index in similarities_phonetic.keys():
            similarities_phonetic[similarity_index] = [np.mean(similarities_phonetic[similarity_index]), np.var(similarities_phonetic[similarity_index])]
    return similarities_phonetic

# Get user inputs (spellings) for the list of words
def get_inputs():
    audio_files = ['Blarb.wav', 'Door.wav', 'Bund.wav', 'Lond.wav', 'Fifer.wav', 'Weird.wav' , 'Larp.wav', 'Fint.wav', 'Fortry.wav', 'Torp.wav', 'Laugh.wav']
    inputs = []
    # Ask if ready
    ready = input("Ready? (Y/n): ")
    ready = ready.strip()
    while ready.lower() != "y":
        ready = input("Ready? (Y/n): ")
        ready = ready.strip()

    for audio in audio_files:
        playsound(audio)
        # Get user input
        # If input is repeat, play again
        user_spelling = input("Enter your spelling or 'repeat' to hear the one more time: ")
        user_spelling = user_spelling.strip()
        while user_spelling.lower() == 'repeat':
            playsound(audio)
            user_spelling = input("Enter your spelling or 'repeat' to hear the one more time: ")
            user_spelling = user_spelling.strip()
        inputs.append(user_spelling)
    return inputs

# Based on the similarity indexes for each word, calculate the probability that they spell phonetically
def calculate_phonetic_probability(similarities, phonetic_distributions):
    probability = 1
    for similarity, word in zip(similarities, words):
        # Find probability of phonetic spelling given phonetic distributions
        mean = phonetic_distributions[word][0]
        std_dev = math.sqrt(phonetic_distributions[word][1])
        probability *= stats.norm(mean, std_dev).pdf(similarity)
    return probability

# Based on the similarity indexes for each word, calculate the probability that they spell non-phonetically
def calculate_non_phonetic_probability(similarities, non_phonetic_distributions):
    probability = 1
    for similarity, word in zip(similarities, words):
        # Find probability of phonetic spelling given phonetic distributions
        mean = non_phonetic_distributions[word][0]
        std_dev = math.sqrt(non_phonetic_distributions[word][1])
        probability *= stats.norm(mean, std_dev).pdf(similarity)
    return probability


# Main function
# Get distributions 
phonetic_distributions = calculate_phonetic_distributions()
non_phonetic_distributions = calculate_non_phonetic_distributions()
# Print introduction and instructions
introduction = ['Welcome! Throughout this test, we will try to figure out the method in which you learned to read. While some people learn to read phonetically, spelling based on the sound of each word, others learned to write by pure memorization.',
               'For each word, listen to the audio and input your best guess as to the spelling of the word. Do not worry if some of the words sound odd -- they are not all real English words!',
               'Each audio will play once before you are asked to input a guess on the spelling. If you would like to hear the audio again, simply type "repeat".']
for line in introduction:
    print()
    print(line)
# Get user's spellings
inputs = get_inputs()

# Calculate similarity indexes for each input and corresponding word
similarities = []
for spelling, word in zip(inputs, words):
    similarities.append(calculate_similarity(spelling, word))

# Calculate the probability that these indexes came from a phonetic spelling distribution vs non-phonetic spelling distribution
phonetic_prob = calculate_phonetic_probability(similarities, phonetic_distributions)
non_phonetic_prob = calculate_non_phonetic_probability(similarities, non_phonetic_distributions)

comparitive_probability = phonetic_prob/non_phonetic_prob
if (comparitive_probability >= 1):
    print()
    # Can I do % chance? Does this directly translate to that?
    print('You are', round(comparitive_probability), 'times more likely to have learned to read and write phonetically.')
    print()

else:
    print()
    print('You are', round(1/comparitive_probability), 'times more likely to have learned to read and write non-phonetically.')
    print()