class SentenceResult {
  final List<String> sentence;
  final int numUnmatchedChars;
  final int numWords;

  SentenceResult(this.sentence, this.numUnmatchedChars, this.numWords);
}

String joinSpecialChar(List<String> sentence) {
  List<String> result = [];
  int n = sentence.length;
  int i = 0;

  while (i < n) {
    String word = sentence[i];
    if (word == 'ال'  &&i < n-1) {
      word += sentence[i+1];
      i+=1;
    }
    i += 1;
    word += ' ';
    result.add(word);
  }
  return result;
}

List<SentenceResult> generateSentenceHelper(
    String sequence, List<String> wordList) {
    List<SentenceResult> result = [];
    List<List<dynamic>> stack = [
    [sequence, [], 0]
  ];

  while (stack.isNotEmpty) {
    List<dynamic> current = stack.removeLast();
    String currentSequence = current[0];
    List<String> currentSentence = List.from(current[1]);
    int currentUnmatchedCharsCount = current[2];

    if (currentSequence.isEmpty) {
      int numUnmatchedChars = currentUnmatchedCharsCount + currentSequence.length;
      int numWords = currentSentence.length;
      List<String> joinedSentence = joinSpecialChar(currentSentence);
      
      result.add(SentenceResult(joinedSentence, numUnmatchedChars, numWords));
      continue;
    }

    for (String word in wordList) {
      if (currentSequence.startsWith(word)) {
        String newSequence = currentSequence.substring(word.length);
        stack.add([newSequence, List.from(currentSentence)..add(word), currentUnmatchedCharsCount]);
      }
    }

    // Handle the case where the remaining sequence doesn't match any word
    if (wordList.every((word) => !currentSequence.startsWith(word))) {
      currentSentence.add(currentSequence);

      int numUnmatchedChars = currentUnmatchedCharsCount + currentSequence.length;
      int numWords = currentSentence.length;
      List<String> joinedSentence = joinSpecialChar(currentSentence);

      result.add(SentenceResult(joinedSentence, numUnmatchedChars, numWords));
    }
  }

  return result;
}

String generateBestSentence(String partialSequence, List<String> wordList) {
  List<SentenceResult> sentences = generateSentenceHelper(partialSequence, wordList);

  // Choose the sentence with the lowest number of unmatched characters,
  // and in case of a tie, consider the fewest words.
  SentenceResult bestSentence = sentences.reduce((a, b) =>
      (a.numUnmatchedChars < b.numUnmatchedChars ||
              (a.numUnmatchedChars == b.numUnmatchedChars && a.numWords <= b.numWords))
          ? a
          : b);

  return bestSentence.sentence.reversed.join(' ');
}