import spacy
import re
import os
from openai import OpenAI
from mlconjug3 import Conjugator

nlp = spacy.load("fr_dep_news_trf")

conjugator = Conjugator(language="fr")

tense_mood_map = {
    ("Ind", "Pres"): ("Indicatif", "Présent"),
    ("Ind", "Past"): ("Indicatif", "Passé composé"),
    ("Ind", "Fut"): ("Indicatif", "Futur"),
    ("Cond", "Pres"): ("Conditionnel", "Présent")
}
person_number_map = {
    ("1", "Sing"): "je",
    ("2", "Sing"): "tu",
    ("3", "Sing"): "il (elle, on)",
    ("1", "Plur"): "nous",
    ("2", "Plur"): "vous",
    ("3", "Plur"): "ils (elles)"
}

def generate_gpt_contradiction(sentence):
    try:
        from openai import OpenAI 

        client = OpenAI(
            api_key="YOUR_API_KEY"
        )
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an expert in French linguistics. Provide a contradiction of the given sentence without using negation."},
                {"role": "user", "content": sentence}
            ]
        )
        return response.choices[0].message.content.strip()
    except Exception:
        return "Error: OpenAI API not available, and no antonyms found in dictionaries."

def load_antonyms(file_path):
    antonyms = {}
    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            line = line.strip()
            if line:
                word, antonym = line.split(':')
                antonyms[word.strip()] = antonym.strip()
    return antonyms

def get_antonym(word, antonyms):
    return antonyms.get(word, None)

def conjugate_antonym(original_token, antonym):
    verb_conjugation = conjugator.conjugate(antonym)

    verb_form = original_token.morph.get("VerbForm")
    if verb_form and "Part" in verb_form:
        mood_tense = ("Participe", "Participe Passé")

        gender = original_token.morph.get("Gender")[0] if original_token.morph.get("Gender") else "Masc"
        number = original_token.morph.get("Number")[0] if original_token.morph.get("Number") else "Sing"

        gender_number_key = {
            ("Masc", "Sing"): "masculin singulier",
            ("Masc", "Plur"): "masculin pluriel",
            ("Fem", "Sing"): "feminin singulier",
            ("Fem", "Plur"): "feminin pluriel"
        }.get((gender, number), "masculin singulier") 

        conjugated_form = verb_conjugation.conjug_info.get(mood_tense[0], {}).get(mood_tense[1], {}).get(gender_number_key, antonym)
    else:
        mood = original_token.morph.get("Mood")[0][:3] if original_token.morph.get("Mood") else "Ind"
        tense = original_token.morph.get("Tense")[0][:4] if original_token.morph.get("Tense") else "Pres"
        mood_tense = tense_mood_map.get((mood, tense), ("Indicatif", "Présent"))

        person = original_token.morph.get("Person")[0] if original_token.morph.get("Person") else "3"
        number = "Plur" if original_token.morph.get("Number") == ["Plur"] else "Sing"
        person_key = person_number_map.get((person, number), "il (elle, on)")

        conjugated_form = verb_conjugation.conjug_info.get(mood_tense[0], {}).get(mood_tense[1], {}).get(person_key, antonym)

    return conjugated_form

def transform_adjective_antonym(sentence, adj_antonyms):
    doc = nlp(sentence)
    transformed_sentence = sentence

    for token in doc:
        if token.dep_ == "ROOT" and token.pos_ == "ADJ":
            antonym_lemma = get_antonym(token.lemma_, adj_antonyms)
            if antonym_lemma:
                antonym_token = nlp(antonym_lemma)[0]
                antonym = antonym_token.text

                if token.morph.get("Gender") == ["Fem"]:
                    antonym += "e"
                if token.morph.get("Number") == ["Plur"]:
                    antonym += "s"

                transformed_sentence = re.sub(rf"\b{token.text}\b", antonym, sentence)
            break

    return transformed_sentence

def negate_sentence(sentence):
    doc = nlp(sentence)
    positive_sentence = sentence 
    for token in doc:
        if token.dep_ == "ROOT":
            # Case 1: The sentence is negative
            negation_tokens = [child for child in token.children if child.dep_ == "neg"]
            if negation_tokens:
                
                for negation in negation_tokens:

                    if negation.text in {"ne", "n'"}:
                        positive_sentence = re.sub(
                            rf"\b{negation.text}\b\s*{re.escape(token.text)}\s*\b(pas|jamais|plus|rien|aucun|nulle part|guère|point|que)?\b",
                            token.text,
                            positive_sentence
                        )
                    elif negation.text in {"pas", "jamais", "plus", "rien", "aucun", "nulle part", "guère", "point", "que"}:
                        positive_sentence = re.sub(
                            rf"\b{negation.text}\b",
                            "",
                            positive_sentence
                        )
                return positive_sentence.strip()

            # Case 2: The sentence is not negative; negate the main verb
            else:
                ne_form = "n'" if token.text[0] in "aeiouéèê" else "ne"
                reflexive_pronoun = None

                for child in token.children:
                    if child.dep_ == "obj" and child.text in {"se", "s'"}:
                        reflexive_pronoun = child.text
                        break

                if reflexive_pronoun:
                    positive_sentence = re.sub(
                        rf"\b{reflexive_pronoun} {token.text}\b",
                        f"{ne_form}{reflexive_pronoun} {token.text} pas" if ne_form == "n'" else f"{ne_form} {reflexive_pronoun} {token.text} pas",
                        sentence
                    )
                else:
                    positive_sentence = re.sub(
                        rf"\b{token.text}\b",
                        f"{ne_form}{token.text} pas" if ne_form == "n'" else f"{ne_form} {token.text} pas",
                        sentence
                    )

                return positive_sentence.strip().replace("ne ne", "").replace("pas pas", "").replace("se ne", "ne se")

    return positive_sentence



def antonym_sentence(sentence, verb_antonyms, adj_antonyms):
    doc = nlp(sentence)
    antonym_sentence = sentence

    antonym_found = False

    # Check for ROOT verb antonyms
    for token in doc:
        if token.dep_ == "ROOT" and token.pos_ == "VERB":
            antonym_lemma = get_antonym(token.lemma_, verb_antonyms)
            if antonym_lemma:
                conjugated_antonym = conjugate_antonym(token, antonym_lemma)
                antonym_sentence = re.sub(rf"\b{token.text}\b", conjugated_antonym, sentence)
                antonym_found = True
            else:
                for child in token.children:
                    # Check for xcomp verb antonyms
                    if child.dep_ == "xcomp" and child.pos_ == "VERB":
                        xcomp_antonym_lemma = get_antonym(child.lemma_, verb_antonyms)
                        if xcomp_antonym_lemma:
                            conjugated_xcomp_antonym = conjugate_antonym(child, xcomp_antonym_lemma)
                            antonym_sentence = re.sub(rf"\b{child.text}\b", conjugated_xcomp_antonym, sentence)
                            antonym_found = True
                            break
            break

    # Check for ROOT adjective antonyms if no verb antonyms were found
    if not antonym_found:
        for token in doc:
            if token.dep_ == "ROOT" and token.pos_ == "ADJ":
                antonym_sentence = transform_adjective_antonym(sentence, adj_antonyms)
                antonym_found = antonym_sentence != sentence
                break

    # Check for xcomp adjectives if no ROOT adjective antonyms were found
    if not antonym_found:
        for token in doc:
            if token.dep_ == "xcomp" and token.pos_ == "ADJ" and token.head.dep_ == "ROOT" and token.head.pos_ == "VERB":
                xcomp_antonym_lemma = get_antonym(token.lemma_, adj_antonyms)
                if xcomp_antonym_lemma:
                    antonym_token = nlp(xcomp_antonym_lemma)[0]
                    antonym = antonym_token.text

                    if token.morph.get("Gender") == ["Fem"]:
                        antonym += "e"
                    if token.morph.get("Number") == ["Plur"]:
                        antonym += "s"

                    antonym_sentence = re.sub(rf"\b{token.text}\b", antonym, sentence)
                    antonym_found = True
                    break

    # Fallback mechanism: Use GPT model for a contradiction proposal
    if not antonym_found:
        gpt_contradiction = generate_gpt_contradiction(sentence)
        antonym_sentence = f"Here is what GPT would propose: {gpt_contradiction}"

    return antonym_sentence



def process_sentences(input_file, output_file, verb_antonym_file, adj_antonym_file):
    
    output_dir = os.path.dirname(output_file)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)

    verb_antonyms = load_antonyms(verb_antonym_file)
    adj_antonyms = load_antonyms(adj_antonym_file)

    with open(input_file, 'r', encoding='utf-8') as infile, open(output_file, 'w', encoding='utf-8') as outfile:
        for line in infile:
            sentence = line.strip()
            if sentence:
                negated = negate_sentence(sentence)
                antonym = antonym_sentence(sentence, verb_antonyms, adj_antonyms)
                
                outfile.write(f"Original: {sentence}\n")
                outfile.write(f"Negation/Positive: {negated}\n")
                outfile.write(f"Antonym: {antonym}\n\n")

input_file = "./input/example_sentences.txt"  
output_file = "./output/contradicted_sentences.txt"  
verb_antonym_file = "./dictionaries/verbe_antonyme.txt"
adj_antonym_file = "./dictionaries/adj_antonyme.txt"

process_sentences(input_file, output_file, verb_antonym_file, adj_antonym_file)
