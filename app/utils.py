
import spacy
from collections import Counter
from gensim.models.doc2vec import Doc2Vec, TaggedDocument
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
import plotly.express as px

# Initialize spaCy
nlp = spacy.load('el_core_news_md', disable=['tagger', 'parser', 'attribute_ruler', 'lemmatizer'])
nlp.add_pipe('sentencizer')

def process_text_safely(text):
    """Process text with minimal memory usage"""
    entities = {}
    entity_counts = Counter()
    connections = set()
    
    # Only process first 35000 characters
    doc = nlp(text[:35000])
    
    # Process entities
    for ent in doc.ents:
        if ent.label_ in ['PERSON', 'ORG', 'LOC', 'GPE', 'DATE']:
            entities[ent.text] = ent.label_
            entity_counts[ent.label_] += 1
    
    # Find connections
    for sent in doc.sents:
        sent_ents = [ent for ent in sent.ents if ent.label_ in ['PERSON', 'ORG', 'LOC', 'GPE', 'DATE']]
        for i, ent1 in enumerate(sent_ents):
            for ent2 in sent_ents[i+1:]:
                connections.add((ent1.text, ent2.text))
    
    return entities, dict(entity_counts), connections

def process_doc2vec(files, reduction_type='pca'):
    """Process files with Doc2Vec and dimension reduction"""
    documents = []
    filenames = []
    
    for file in files:
        if file and file.filename:
            try:
                text = file.read().decode('utf-8')
                doc = nlp(text[:3000])
                tokens = [token.text for token in doc if not token.is_space]
                documents.append(TaggedDocument(words=tokens, tags=[file.filename]))
                filenames.append(file.filename)
                file.seek(0)
            except Exception as e:
                print(f"Error processing {file.filename} for Doc2Vec: {str(e)}")
                continue

    if not documents:
        return None, None

    model = Doc2Vec(documents, vector_size=20, min_count=1, epochs=10)
    vectors = [model.dv[fname] for fname in filenames]
    
    if reduction_type == 'pca':
        reducer = PCA(n_components=2)
    else:
        reducer = TSNE(n_components=2, perplexity=min(3, len(vectors)-1))
        
    coords = reducer.fit_transform(vectors)
    
    fig = px.scatter(x=coords[:, 0], y=coords[:, 1],
                    text=filenames,
                    title=f"Document Embeddings ({reduction_type.upper()})")
    
    return fig.to_json(), filenames
