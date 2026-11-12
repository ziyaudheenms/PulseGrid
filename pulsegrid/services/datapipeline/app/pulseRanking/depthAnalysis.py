"""
    Depth Analysis is used to indentify the qualiity of the content that is being presented

    The first Depth Analysis which we are going to do is the MATTR analysis

    Moving Average Type-Token Ratio

    Things to note ===> we have to filter out common article words like 'the' , 'a', 'an' and so on
    also have to consider the running , ran ===> run (so that our result will be more accurate of how many
    genuine words  they have.)

    1, the entire content is divided into words, then with a specified window (eg:- 100) no of unique words in that
       window is analysed as N --> N/ windiw size and stored in a array for further application.

    2, then the next window is considered as removing the very first word of the first window and adding the immediate 
       new one on the right

       this goes untill the entire words gets covered.

    3, All the stored words ratio is then divided with the no of windows that was generated to get the nominal
    MATTR score. 

    
    we can use the python spacy library for extracting the words out of the content and also to remove 
    the comman artcile words

"""

import asyncio
import math
from collections import Counter
from concurrent.futures import ProcessPoolExecutor
import spacy
from spacy.tokens import Doc


#global refernnce that which is used so inorder to start only one spacy model per processor core
_WORKER_NLP = None

def _init_worker(model_name: str):
    """Initializer function executed once per worker process when the pool starts."""
    global _WORKER_NLP
    _WORKER_NLP = spacy.load(model_name)


class PulseGridDepthScorer:
    def __init__(
        self,
        model_name: str = "en_core_web_sm",
        window_size: int = 40,
        max_phrase_len: int = 3,
        batch_size: int = 64,
        max_workers: int = 4,
        chunk_size: int = 250,
    ):
        self.model_name = model_name
        self.window_size = window_size
        self.max_phrase_len = max_phrase_len
        self.batch_size = batch_size
        self.max_workers = max_workers
        self.chunk_size = chunk_size

        # Entity labels ignored during compound phrase merging
        self.ignored_entities = {"DATE", "TIME", "ORDINAL"}
        
        # Entity labels tracked for information density bonuses
        self.quantifiable_labels = {"PERCENT", "MONEY", "QUANTITY", "CARDINAL"}


    def _extract_content_and_quantities(self, doc: Doc):

        #first we need to extract the qnantites mentioned in the article, which helps in understanding the depth
        quantity_count = 0
        for token in doc:
            #this loop takes each word from the content 
            if token.like_num and not token.is_stop: #.like_num maps to both the 15 and fiftheen
                quantity_count += 1

        for ent in doc.ents:
            if ent.label_ in self.quantifiable_labels: #if any entity (unique words) belongs to the quantifiable labels we can increase the count
                quantity_count += 1

        #we also have to extract the count of unique entities that which has been displayed in the article
        #set() has been used so that to automatically avoid the duplicate entities get intot the list
        unique_entities = set(
            ent.text.strip().lower()
            for ent in doc.ents
            if ent.label_ not in self.ignored_entities and len(ent.text.strip()) > 1
        )
        unique_entity_count = len(unique_entities)


        #next we have to prepare the tokens(words) for the mattr scoring analysis.
        #for that firt we need to map all the entities count --> (organizations , people , name etc)
        #then we need to collect the multi meaning words liike 'machine learning'---> this has to be treated as one not as two spaerate words


        #entity means simething meanigfull but we are limitng the word length to 3 for satfey purpose.
        entity_span = [
            ent for ent in doc.ents
            if ent.label_ not in self.ignored_entities and len(ent) <= self.max_phrase_len
        ]

        #next we need to map 'machine' 'learning' into one ---> machine_learning

        compound_span = []
        for token in doc:
            if token.dep_ == 'compound' and token.head.i > token.i: #here the token.i represents the current word index token.head represents the word which is beings described by the current word, this only happens when the current word is a compound noun
                #we will check of if the index of the decribed word by the current word is greater than index of current word
                #for example "credit card" card is token.head since credit describes card.
                #if we found such words together we will join them into one , for now we will collect such words.
                span = doc[token.i:token.head.i +1] #-> +1 so that we can include that
                if len(span) <= self.max_phrase_len:
                    compound_span.append(span)  #we will add respective span of text into our array

        #next step we have to reorganize or retokenize the content based on the compound and pure entity

        #doc.retokenize is used since doc is immutable nature but usind this retokenize we can get a memmory safe and temporary access.
        with doc.retokenize() as retokenizer:
            #there will be cases where the entity and compound span both contains same thing like 'New York' is not compound it is a entity but comound csn also have this
            #to solve this overlay issues we can use spacy.util.filter_spans
            for span in spacy.util.filter_spans(entity_span + compound_span):
                combined_word = "_".join(t.lemma_.lower() for t in span if t.is_alpha)  #lemma_ is usd to get the root form word, each sub array of compund words or entity words will be merged into one
                if combined_word:
                    retokenizer.merge(span, attrs={"LEMMA": combined_word})  #this is the core part, which replaces the lemma_ == root form of the span words with the combined word
                    #for eg -> credit(3) cards(4) --> combined credit_card --> replaces the word 3 and 4 ---> credit_card will be added as root elemtnt there.
            
        
        #Now all our cleaning has perfomred so we can extract all thw words and sent it for the mattr scroing

        concepts = [
            t.lemma_.lower() for t in doc #for effective mattr analysis we will be using the root form of the word
            if not t.is_stop and not t.is_punct and (t.is_alpha or "_" in t.lemma_) #we will be cleaning out the full stop and punctuation marks
        ]
        
        return concepts, quantity_count, unique_entity_count