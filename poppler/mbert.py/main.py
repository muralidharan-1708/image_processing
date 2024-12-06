import time
from transformers import pipeline

# Load the pre-trained mBERT model for NER with GPU support
ner_pipeline = pipeline("ner", model="bert-base-multilingual-cased", device=0)

# Example text in multiple languages
text_english = "Barack Obama was born in Hawaii on August 4, 1961."

# Measure the start time
start_time = time.time()

# Perform NER in English
ner_results_english = ner_pipeline(text_english)

# Measure the end time
end_time = time.time()

# Calculate the execution time
execution_time = end_time - start_time

# Mapping of entity labels to desired format
entity_mapping = {
    "PER": "per",
    "LOC": "loc",
    "ORG": "org",
    "MISC": "misc"
}

# Collect entities and their corresponding words in a dictionary
entity_dict = {}
for entity in ner_results_english:
    entity_type = entity_mapping.get(entity['entity'].split('-')[-1], entity['entity'])
    word = entity['word']
    if entity_type not in entity_dict:
        entity_dict[entity_type] = []
    entity_dict[entity_type].append(word)

print("English NER Results:")
print(entity_dict)

print(f"Execution Time: {execution_time} seconds")
