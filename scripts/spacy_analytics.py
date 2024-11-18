import spacy

nlp = spacy.load("fr_dep_news_trf")

def analyze_syntax(input_file, output_file):
    with open(input_file, 'r', encoding='utf-8') as infile, open(output_file, 'w', encoding='utf-8') as outfile:
        outfile.write(f'token\tlemma\tpos\tdep\tmorph\thead\n')
        for line in infile:
            doc = nlp(line.strip())

            for token in doc:
                outfile.write(f"{token.text}\t{token.lemma_}\t{token.pos_}\t{token.dep_}\t{token.morph}\t{token.head.text}\n")
            
            outfile.write("\n")

# Replace 'input.txt' with the name of your input file and 'output.txt' with the desired output file
analyze_syntax('./input/example_sentences.txt', 'spacy_analytics_out.txt')
