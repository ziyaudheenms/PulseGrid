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
import spacy


from typing import Any
from bson import ObjectId
from spacy.tokens import Doc
from pymongo import UpdateOne
from collections import Counter
from pymongo.errors import BulkWriteError
from concurrent.futures import ProcessPoolExecutor
from pymongo.asynchronous.database import AsyncDatabase


#global refernnce that which is used so inorder to start only one spacy model per processor core
_WORKER_NLP = None

def _init_worker(model_name: str):
    """Initializer function executed once per worker process when the pool starts."""
    global _WORKER_NLP
    _WORKER_NLP = spacy.load(model_name)


class PulseGridDepthScorer:
    def __init__(
        self,
        db: AsyncDatabase,
        model_name: str = "en_core_web_sm",
        window_size: int = 40,
        max_phrase_len: int = 3,
        batch_size: int = 64,
        max_workers: int = 4,
        chunk_size: int = 250,
    ):
        self.db = db
        self.model_name = model_name
        self.window_size = window_size
        self.max_phrase_len = max_phrase_len
        self.batch_size = batch_size
        self.max_workers = max_workers
        self.chunk_size = chunk_size
        self.collection = self.db["articleMetaData"]

        # Entity labels ignored during compound phrase merging
        self.ignored_entities = {"DATE", "TIME", "ORDINAL"}
        
        # Entity labels tracked for information density bonuses
        self.quantifiable_labels = {"PERCENT", "MONEY", "QUANTITY", "CARDINAL"}


    async def save_scores_to_database(self, records : list[dict[str, Any]]):
        """"
        We have to update the DB , here we want to implement the bulk addititon is order ti reduce the time complexity else it will be og O(n+1).
        here since for each article the data to be appended gets changing, we cant use the update_many. therefore
        we combine the update_one and collect all the update command for the incoming records and finally using rhe 
        bulk write we will fire up all the update operations together.
        """
        if not records:
            return

        operations = []

        for rec in records:
            doc_id = rec["doc_id"]

            #we are collecting all the updation commands for the DB operation
            operations.append(
                UpdateOne(
                    {"_id": ObjectId(doc_id)},
                    {
                        "$set": {
                            "ranking_depth_score": rec["ranking_depth_score"],
                            "mattr": rec["mattr"],
                            "total_concepts": rec["total_concepts"],
                            "unique_concepts": rec["unique_concepts"],
                            "quantity_count": rec["quantity_count"],
                            "entity_count": rec["entity_count"],
                            "status": "MATTR"  # status will be updated to implement MATTR
                        }
                    }
                )
            )

        

        #once all the records gets the updation commands , now we have to fire them all together
        try:
            # 1. Execute bulk write and capture the acknowledgment result object
            result = await self.collection.bulk_write(operations, ordered=False)
            
            # 2. Extract acknowledgment metrics from the result object
            matched = result.matched_count
            modified = result.modified_count
            
            print(f"Bulk Write Acknowledged: Matched {matched}, Modified {modified} documents.")
            return modified

        except BulkWriteError as bwe:
            # 3. Handle partial failures if `ordered=False` encounters specific document errors
            details = bwe.details
            successful_modifications = details.get("nModified", 0)
            print(f"Bulk write completed with errors. Successfully modified: {successful_modifications}")
            print(f"Error details: {details.get('writeErrors')}")
            return successful_modifications

        except Exception as e:
            # 4. Handle catastrophic network or connection drops
            print(f"Unexpected database error during bulk write: {e}")
            return 0

    def _extract_content_and_quantities(self, doc: Doc) -> tuple[list[str], int, int]:

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


    def _compute_mattr(self, tokens: list[str]) -> float:
        """
        We will be implementing the actual mattr analysis of eah article here
        """

        n = len(tokens)
        if n == 0:
            return 0.0
        if n <= self.window_size:
            return len(set(tokens)) / n

        #now we have to implement the sliding window thing into the pipline.
        #we have to utitlize the Counter of python for avoiding the O(n2) time complexity
        #Counter when passed with a array into it it generates a dict with each unique element in the given array with there occurance number, by taking the len() property of the counter object we will get the no of unique entities.

        count = Counter(tokens[:self.window_size])  #for the inital window
        unique_count = len(count)
        ttr_sum = unique_count / self.window_size

        for i in range(self.window_size, n):

            #cleaning process of the left most element that is to be deleted.
            outgoing = tokens[i - self.window_size]
            count[outgoing] -= 1
            if count[outgoing] == 0: #which means the unique counter doesnt contains that word
                #so we have to upate such a way that the len(count) reduces ones since its deletes
                unique_count -= 1

            #we have to add the incoming token from the right
            incoming = tokens[i]
            #we have to ensure that the counter not have this token if so we will increment the unique else we will not change the unique
            if count[incoming] == 0:  #0 represts that the item is absent in counter.
                unique_count += 1
            #we have to update this token in the counter
            count[incoming] += 1

            #niw perform the ttr operation
            ttr_sum += unique_count / self.window_size  

        #once this loops completes the execution we have to takle the mean(average) and return them.

        return ttr_sum / (n - self.window_size + 1)  # this gives the possible window size.(DENOMINATOR)

    def process_batch(self, batch: list[tuple[str, str]]) -> list[dict]:
        """
        process batch is usd to run the batch operation of the scoring mechanism, this batch will be
        operated inside each cpu core by the processor
        """

        global _WORKER_NLP  #tells to take the re loaded global scapy configuration
        results = []

        #for ensuring the memmory safty, more than 25000 words will be get truncated, tis is used inorder to ensure that memmory spike will not get happened.
        text_stream = (
            (text[:25000].strip(), doc_id)
            for doc_id, text in batch
            if text and text.strip()
        )

        #for increasing the perfomrane, instead of a normal loop based nlp(text) we will be of using the .pipe() that process a batch of operations

        for doc, doc_id in _WORKER_NLP.pipe(text_stream, as_tuples=True, batch_size=self.batch_size):
            concepts, quantity_count, entity_count = self._extract_content_and_quantities(doc)
            total_concepts = len(concepts)
            mattr = self._compute_mattr(concepts)

            #once we get all this required components, as of next part we have to implement the calculation for 
            #the final ContentDepth score.

            #first we hae to handle a case like a short para with some uniqe words may get more more mattr while a long para with good amount of unique gets low
            #we will be using the log10 factor

            base_depth = mattr * math.log10(total_concepts + 1) if total_concepts > 0 else 0.0

            #now we have to encoperate the no of enitties and quantities that has beein  used in the article
            #thing to note is that mattr score should dominate , so that depth analysis stays relevant , therefore only 20% will be the other factors add to the final depth scoreee

            factuality_metric = quantity_count + (entity_count * 0.5) # entity is multiplid with 0.5 so that to prevent the bloating of the content just with random entity wordsss.
            density_bonus = min(0.20, factuality_metric * 0.02) #80% will be dominated by the mattr score inly 20% by these factoresssss

            final_depth_score = base_depth * (1.0 + density_bonus) #ensure even if deb=nsity bonus drops zero, the base depth doesnt breaks

            results.append({
                "doc_id": doc_id,
                "total_concepts": total_concepts,
                "unique_concepts": len(set(concepts)),
                "quantity_count": quantity_count,
                "entity_count": entity_count,
                "mattr": round(mattr, 4),
                "ranking_depth_score": round(final_depth_score, 4),
            })

        return results


    #the function that which initiates all the artciles
    async def run_pipeline(self) -> int:
        loop = asyncio.get_running_loop()
        total_processed = 0
        last_seen_id = None  #used to track the cursor of the last seen id

        # Boot up the ProcessPoolExecutor once for the entire pipeline run
        with ProcessPoolExecutor(
            max_workers=self.max_workers,
            initializer=_init_worker,
            initargs=(self.model_name,)
        ) as pool:
            
            # Use a while loop to pull and process batches until no articles remain
            while True:
                query: dict[str, Any] = {
                    "status": {"$ne": "MATTR"}
                }
                if last_seen_id:
                    query["_id"] = {"$gt": last_seen_id}

                # Fetch a controlled batch from MongoDB
                cursor = (
                    self.collection.find(query, {"body": 1})
                    .sort("_id", 1)
                    .limit(self.chunk_size)
                )
                
                chunk = []
                async for doc in cursor:
                    doc_id = str(doc.get("_id"))
                    text = doc.get("body") or doc.get("text", "")
                    
                    if text and text.strip():
                        chunk.append((doc_id, text))
                    
                    # Update the pagination anchor
                    last_seen_id = doc["_id"]

                # THE BREAK CONDITION: If the cursor found 0 articles, we are done!
                if not chunk:
                    break

                # Dispatch this exact chunk directly to the worker pool
                task = loop.run_in_executor(pool, self.process_batch, chunk) #handing the small chunks of the data to the saperate executor
                scored_results = await task
                
                if scored_results:
                    await self.save_scores_to_database(scored_results)
                    total_processed += len(scored_results)
                    print(f"Processed and saved batch of {len(scored_results)} articles...")

        return total_processed