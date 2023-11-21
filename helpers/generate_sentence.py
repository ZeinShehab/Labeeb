def generate_sentences(sequence, word_list):
    stack = [(sequence, [], 0)]
    result = []

    while stack:
        sequence, current_sentence, unmatched_chars_count = stack.pop()

        if not sequence:
            num_unmatched_chars = unmatched_chars_count + len(sequence)
            num_words = len(current_sentence)
            result.append((" ".join(current_sentence), num_unmatched_chars, num_words))
            continue

        for word in word_list:
            if sequence.startswith(word):
                new_sequence = sequence[len(word):]
                stack.append((new_sequence, current_sentence + [word], unmatched_chars_count))

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
    
    return best_sentence[0]

words = ["name", "namely", "my", "is", "mine", "hello", "hell", 'this', 'open', 'shell', 'p' ,'en', 'i', 'love', 'you']
# partial_sequence = ['m', 'y', 'n', 'a', 'm', 'e', 'i', 's']
# partial_sequence = ['m', 'y', 'n', 'a', 'm', 'e', 'l', 'y', 'i', 's']
# partial_sequence = ['i', 'l', 'o', 'v', 'e', 'y', 'o', 'u']
partial_sequence = [*"thisishellopen"]
best_sentence = generate_best_sentence("".join(partial_sequence), words)
print(best_sentence)
