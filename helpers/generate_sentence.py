def join_words(sentence):
    result = ""
    n = len(sentence)

    i = 0
    while i < n:
        result += sentence[i]
        if sentence[i] == "ال" and i < n -1:
            result += sentence[i+1]
            i+=1
        i +=1
        result += " "

    return result
    # return " ".join(sentence)

def generate_sentences(sequence, word_list):
    stack = [(sequence, [], 0)]
    result = []

    while stack:
        sequence, current_sentence, unmatched_chars_count = stack.pop()

        if not sequence:
            num_unmatched_chars = unmatched_chars_count + len(sequence)
            num_words = len(current_sentence)
            joined_sentence = join_words(current_sentence)
            result.append((joined_sentence, num_unmatched_chars, num_words))
            continue

        for word in word_list:
            if sequence.startswith(word):
            # if sequence.endswith(word):
                new_sequence = sequence[len(word):]
                # new_sequence = sequence[:-len(word):]
                stack.append((new_sequence, current_sentence + [word], unmatched_chars_count))
                # stack.insert(0, (new_sequence, current_sentence + [word[::-1]], unmatched_chars_count))

        # Handle the case where the remaining sequence doesn't match any word
        if not any(sequence.startswith(word) for word in word_list):
            current_sentence.append(sequence)
            num_unmatched_chars = unmatched_chars_count + len(sequence)
            num_words = len(current_sentence)
            result.append((" ".join(current_sentence), num_unmatched_chars, num_words))

    return result

# Modified function to handle partial sequences
def generate_best_sentence(partial_sequence, word_list):
    sentences = generate_sentences("".join(partial_sequence), word_list)
    
    print(sentences)

    # Choose the sentence with the lowest number of unmatched characters,
    # and in case of a tie, consider the fewest words.
    best_sentence = min(sentences, key=lambda x: (x[1], x[2]))
    
    return best_sentence[0][::-1]

words = ["لا","ال","باب","دار","تفاحة","فتح","غرفة",]
# partial_sequence = ['m', 'y', 'n', 'a', 'm', 'e', 'i', 's']
# partial_sequence = ['m', 'y', 'n', 'a', 'm', 'e', 'l', 'y', 'i', 's']
# partial_sequence = ['i', 'l', 'o', 'v', 'e', 'y', 'o', 'u']
partial_sequence = [*"فتحالبابغرفة"]
best_sentence = generate_best_sentence("".join(partial_sequence), words)
print(best_sentence)
