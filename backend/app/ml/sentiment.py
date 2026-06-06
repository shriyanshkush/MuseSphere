POSITIVE={'great','excellent','love','amazing','good','helpful','wonderful'}; NEGATIVE={'bad','poor','hate','slow','terrible','confusing','expensive'}
def analyze_sentiment(text:str)->tuple[str,float]:
    words=set(text.lower().split()); score=(len(words & POSITIVE)-len(words & NEGATIVE))/max(len(words),1)
    if score>0.02: return 'positive', round(min(1.0,0.6+score),3)
    if score<-0.02: return 'negative', round(max(0.0,0.4+score),3)
    return 'neutral', 0.5
