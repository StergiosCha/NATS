def process_ner(files):
    texts = {}
    # Create both directories if they don't exist
    os.makedirs('static', exist_ok=True)
    os.makedirs('static/networks', exist_ok=True)
    
    for file in files:
        if file and file.filename:
            try:
                text = file.read().decode('utf-8')
                doc = nlp(text[:5000])
                
                # Create network
                net = Network(height='500px', width='100%', bgcolor='#222222', font_color='white')
                
                entities = {}
                for ent in doc.ents:
                    if ent.label_ in ['PERSON', 'ORG', 'LOC', 'GPE', 'DATE']:
                        entities[ent.text] = ent.label_
                
                # Add nodes with colors
                for entity, type_ in entities.items():
                    color = '#ffffff'
                    if type_ == 'PERSON':
                        color = '#ffff44'
                    elif type_ == 'ORG':
                        color = '#4444ff'
                    elif type_ in ['LOC', 'GPE']:
                        color = '#44ff44'
                    elif type_ == 'DATE':
                        color = '#ff44ff'
                        
                    net.add_node(entity, 
                               label=entity,
                               color=color,
                               title=f"Type: {type_}")
                
                # Add edges
                for sent in doc.sents:
                    sent_ents = [ent for ent in sent.ents if ent.text in entities]
                    for i, ent1 in enumerate(sent_ents):
                        for ent2 in sent_ents[i+1:]:
                            net.add_edge(ent1.text, ent2.text)
                
                # Save network with correct path
                network_filename = f'networks/network_{len(texts)}.html'
                full_path = os.path.join('static', network_filename)
                net.save_graph(full_path)
                
                texts[file.filename] = {
                    'network_path': network_filename
                }
                
            except Exception as e:
                print(f"Error processing {file.filename}: {str(e)}")
                continue
