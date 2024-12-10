# Open app/models/ner_analyzer.py and add this content:
cat > app/models/ner_analyzer.py << 'EOL'
import spacy
from collections import Counter
from typing import Dict, List, Any
import plotly.graph_objects as go
from plotly.subplots import make_subplots

class NERAnalyzer:
   def __init__(self):
       self.entity_types = {
           'PERSON': 'People, including fictional',
           'LOC': 'Locations, countries, cities',
           'ORG': 'Organizations, companies, institutions',
           'GPE': 'Geopolitical entities, countries, cities',
           'DATE': 'Dates or periods',
           'EVENT': 'Named events',
           'WORK_OF_ART': 'Titles of books, songs, etc.'
       }
       self.entities = {}
       
   def analyze_text(self, doc: spacy.tokens.Doc, filename: str) -> Dict[str, List[Dict]]:
       """Analyze a single text document for named entities"""
       text_entities = []
       
       for ent in doc.ents:
           if ent.label_ in self.entity_types:
               text_entities.append({
                   'text': ent.text,
                   'label': ent.label_,
                   'start_char': ent.start_char,
                   'end_char': ent.end_char,
                   'description': self.entity_types[ent.label_]
               })
       
       self.entities[filename] = text_entities
       return self.entities

   def analyze_texts(self, texts: Dict[str, spacy.tokens.Doc]) -> Dict[str, List[Dict]]:
       """Analyze multiple texts for named entities"""
       for filename, doc in texts.items():
           self.analyze_text(doc, filename)
       return self.entities

   def get_entity_counts(self) -> Dict[str, Dict[str, int]]:
       """Get counts of each entity type per document"""
       counts = {}
       for filename, entities in self.entities.items():
           type_counts = Counter(entity['label'] for entity in entities)
           counts[filename] = dict(type_counts)
       return counts

   def get_entity_distribution(self) -> Dict[str, int]:
       """Get overall distribution of entity types"""
       all_types = Counter()
       for entities in self.entities.values():
           all_types.update(entity['label'] for entity in entities)
       return dict(all_types)

   def create_visualization(self) -> str:
       """Create interactive visualization of entity distributions"""
       entity_counts = self.get_entity_counts()
       entity_dist = self.get_entity_distribution()
       
       # Create figure with subplots
       fig = make_subplots(
           rows=2, cols=1,
           subplot_titles=('Entity Distribution Across All Texts', 
                         'Entity Distribution by Document'),
           heights=[0.4, 0.6]
       )
       
       # Add overall distribution bar chart
       fig.add_trace(
           go.Bar(
               x=list(entity_dist.keys()),
               y=list(entity_dist.values()),
               name='Total Entities'
           ),
           row=1, col=1
       )
       
       # Add per-document stacked bar chart
       for ent_type in self.entity_types:
           y_values = [counts.get(ent_type, 0) for counts in entity_counts.values()]
           fig.add_trace(
               go.Bar(
                   name=ent_type,
                   x=list(entity_counts.keys()),
                   y=y_values
               ),
               row=2, col=1
           )
       
       fig.update_layout(
           title_text='Named Entity Analysis',
           barmode='stack',
           height=800,
           showlegend=True
       )
       
       return fig.to_json()

   def get_entity_context(self, entity_type: str = None) -> Dict[str, List[Dict]]:
       """Get contexts for entities, optionally filtered by type"""
       contexts = {}
       for filename, entities in self.entities.items():
           if entity_type:
               filtered = [e for e in entities if e['label'] == entity_type]
           else:
               filtered = entities
               
           contexts[filename] = filtered
           
       return contexts
EOL

git add app/models/ner_analyzer.py
git commit -m "feat: implement ner analyzer"
git push origin main
