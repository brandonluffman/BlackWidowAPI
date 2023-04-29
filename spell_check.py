from spellchecker import SpellChecker

# create an instance of the spell checker
spell = SpellChecker()

# check a string for misspelled words
text = "Ths is a sentnce with misspeled words."
misspelled = spell.unknown(text.split())
print("MISSSPELLED", list(misspelled))

# print suggested corrections for misspelled words
for word in misspelled:
    print(f"Suggestion for {word}: {spell.correction(word)}")
