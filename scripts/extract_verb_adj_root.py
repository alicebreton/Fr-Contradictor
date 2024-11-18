import spacy

nlp = spacy.load("fr_dep_news_trf")

def extract_adj_and_root(input_file):
    adj_root_list = []

    with open(input_file, 'r', encoding='utf-8') as file:
        for line in file:

            doc = nlp(line.strip())
            
            for token in doc:
                if token.pos_ == "ADJ" and token.dep_ == "ROOT":
                    adj_root_list.append(token.lemma_)
    
    return adj_root_list

def extract_verb_and_root(input_file):
    verb_root_list = []
    
    with open(input_file, 'r', encoding='utf-8') as file:
        for line in file:
            doc = nlp(line.strip())
            
            for token in doc:
                if token.pos_ == "VERB" and token.dep_ == "ROOT":
                    verb_root_list.append(token.lemma_)
    
    return verb_root_list

def main():
    input_file = "./input/example_sentences.txt"  # Replace with your input file path
    adj_root_list = extract_adj_and_root(input_file)
    verb_root_list = extract_verb_and_root(input_file)
    
    print("List of ADJ and ROOT tokens:")
    print(adj_root_list)

    print("List of VERB and ROOT tokens:")
    print(verb_root_list)

if __name__ == "__main__":
    main()
