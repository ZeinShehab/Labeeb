List<String> mapCombinations(
    List<String> charSequence, Map<String, String> combinations) {
  List<String> result = charSequence;
  int n = charSequence.length;

  String doubleCombination = "";
  String tripleCombination = "";

  if (n <= 1) {
    return result;
  }

  doubleCombination = charSequence.sublist(n - 2).join("");
  if (n >= 3) {
    tripleCombination = charSequence.sublist(n - 3).join("");
  }

  if (combinations.containsKey(tripleCombination)) {
    result = charSequence.sublist(0, n - 3);
    result.add(combinations[tripleCombination]!);
  } else if (combinations.containsKey(doubleCombination)) {
    result = charSequence.sublist(0, n - 2);
    result.add(combinations[doubleCombination]!);
  }

  return result;
}
