import time

from huggingface_hub import ModelFilter, HfApi
from sentence_transformers import SentenceTransformer, util


def get_top10_models(task='sentence-similarity'):
    api = HfApi()
    models = api.list_models(sort='downloads', direction=-1,
                             filter=ModelFilter(
                                 task=task
                             )
                             )

    return [model.modelId for model in models]


def run_sentence_transformer(model, src_sentence, compare_sentences):
    bef = time.time()

    # Load pre-trained sentence embeddings model
    model = SentenceTransformer(model, cache_folder='models')

    sentences = [src_sentence] + compare_sentences

    # Compute sentence embeddings
    sentence_embeddings = model.encode(sentences, convert_to_tensor=True)

    dict = { "similarity": [], "elapsed_time": 0 }
    print(type(dict))

    # Calculate similarity score for each pair of sentences
    for i in range(1, len(sentences)):
        similarity_score = util.pytorch_cos_sim(sentence_embeddings[0], sentence_embeddings[i])
        dict['similarity'].append(f"Similarity between sentence {1} and sentence {i + 1}: {similarity_score.item():.4f}")

    aft = time.time()
    dict['elapsed_time'] = aft-bef
    return dict