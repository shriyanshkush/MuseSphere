class KnowledgeBase:
    def chunk(self, text:str, size:int=800)->list[str]: return [text[i:i+size] for i in range(0,len(text),size)] or ['']
    def retrieve(self, documents:list, query:str)->str:
        terms=set(query.lower().split()); ranked=sorted(documents, key=lambda d: len(terms.intersection(d.content.lower().split())), reverse=True)
        return ranked[0].content[:1200] if ranked else 'No knowledge documents have been uploaded yet.'
