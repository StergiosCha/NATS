def process_text_safely(text):
    """Process text with minimal memory usage"""
    entities = {}
    entity_counts = Counter()
    connections = set()
    sentence_context = {}  # Store contexts for connections
    
    doc = nlp(text[:35000])
    
    # Track entity frequencies
    entity_frequency = Counter()
    
    # Process entities
    for ent in doc.ents:
        if ent.label_ in ['PERSON', 'ORG', 'LOC', 'GPE', 'DATE']:
            entities[ent.text] = ent.label_
            entity_counts[ent.label_] += 1
            entity_frequency[ent.text] += 1
    
    # Find connections with context
    for sent in doc.sents:
        sent_ents = [ent for ent in sent.ents if ent.label_ in ['PERSON', 'ORG', 'LOC', 'GPE', 'DATE']]
        for i, ent1 in enumerate(sent_ents):
            for ent2 in sent_ents[i+1:]:
                connection = (ent1.text, ent2.text)
                connections.add(connection)
                # Store sentence context for this connection
                sentence_context[connection] = sent.text
    
    return entities, dict(entity_counts), connections, sentence_context, entity_frequency

@app.route('/upload', methods=['POST'])
def upload_files():
    try:
        # ... (keep existing file handling code)
        
        for file in files:
            if file and file.filename:
                try:
                    text = file.read().decode('utf-8')
                    
                    # Process text
                    entities, entity_counts, connections, sentence_context, entity_frequency = process_text_safely(text)
                    
                    # Create network with physics settings
                    net = Network(height='500px', width='100%', bgcolor='#222222', font_color='white')
                    
                    # Configure physics for better layout
                    net.set_options("""
                    {
                      "physics": {
                        "barnesHut": {
                          "gravitationalConstant": -2000,
                          "centralGravity": 0.3,
                          "springLength": 200,
                          "springConstant": 0.04
                        },
                        "minVelocity": 0.75
                      }
                    }
                    """)
                    
                    # Calculate node sizes based on frequency
                    max_freq = max(entity_frequency.values()) if entity_frequency else 1
                    min_size = 20
                    max_size = 50
                    
                    # Add nodes with dynamic sizes
                    for entity, label in entities.items():
                        # Calculate node size
                        freq = entity_frequency[entity]
                        size = min_size + (max_size - min_size) * (freq / max_freq)
                        
                        color = '#ffffff'  # default white
                        if label == 'PERSON':
                            color = '#ffff44'  # yellow
                        elif label == 'ORG':
                            color = '#4444ff'  # blue
                        elif label in ['LOC', 'GPE']:
                            color = '#44ff44'  # green
                        elif label == 'DATE':
                            color = '#ff44ff'  # purple
                            
                        net.add_node(entity, 
                                   label=entity,
                                   color=color,
                                   size=size,
                                   title=f"Type: {label}\nFrequency: {freq}")
                    
                    # Add edges with context tooltips
                    for (ent1, ent2) in connections:
                        context = sentence_context.get((ent1, ent2), "")
                        net.add_edge(ent1, ent2, title=context[:100] + "...")
                    
                    # Save network
                    network_filename = f'networks/network_{len(texts)}.html'
                    net.save_graph(f'static/{network_filename}')
                    
                    texts[file.filename] = {
                        'preview': text[:200],
                        'entities': entities,
                        'network_path': network_filename,
                        'entity_counts': entity_counts
                    }
                    
                except Exception as e:
                    print(f"Error processing {file.filename}: {str(e)}")
                    continue
                    
        return render_template('results.html', files=texts)
        
    except Exception as e:
        print(f"Upload error: {str(e)}")
        return jsonify({'error': f'Upload failed: {str(e)}'}), 500
