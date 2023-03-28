import wikipedia
import pandas as pd
import os
import spacy
from fuzzywuzzy import fuzz
import animation
from enum import Enum
import sys
import time
from unidecode import unidecode

modules = ["wikipedia","pandas","tqdm","spacy","fuzzywuzzy","animation","unidecode"]
for name in modules:
    if name not in sys.modules:
        print(f"<!> WARNING ({name}) : make sure you've installed all dependencies (pip install -r requirements.txt) <!>")

class Gamemode(Enum):
    LONG = "LONG"
    SHORT = "SHORT"

class LightPedantix():
    
    @animation.wait()
    def __init__(self) -> None:
        os.system("clear")
        self.gamemode_screen()
        print("Loading")
        self.page = self.retrieve_page()
        self.title = self.page.title
        self.original_summary = self.page.summary
        self.nlp = spacy.load('fr_core_news_md')
        doc = self.nlp(self.original_summary)
        self.entities = [ent.text for ent in doc.ents] 
        self.first_summary = self.replace_with_blank(self.original_summary,self.entities)
        self.summary = self.original_summary
        self.temp_summary = self.original_summary
        pass

    def show_image(self):
        from PIL import Image
        import urllib.request

        image_found = False
        for link in self.page.images:
            if str(link).endswith("jpg"):
                image_link = link
                image_found = True
                break
        if image_found:
            urllib.request.urlretrieve(image_link,f"data/{self.page.title}.jpg")
            img = Image.open(f"data/{self.page.title}.jpg")
            img.show()
            os.remove(f"data/{self.page.title}.jpg")


    def gamemode_screen(self):
        print("What gamemode would you like to play, long page or short page ? (long/short)")
        i = input()
        if i == 'long':
            self.gamemode = Gamemode.LONG
        else:
            self.gamemode = Gamemode.SHORT

    def page_is_ok(self,page : wikipedia.wikipedia.WikipediaPage):
        def nb_mots(txt : str):
            return len(txt.split(" "))
        
        ## ajouter le fait que le titre est pas contenu dans les entities    
        if self.gamemode == Gamemode.LONG:
            return (nb_mots(page.summary) > 200)
        else:
            return (nb_mots(page.summary) < 200)

    



    def retrieve_page(self):
        most_popular_pages = pd.read_csv('./data/pages_les_plus_consultees.csv').iloc[:,2]
        wikipedia.set_lang("fr")
        page_found = False
        while not page_found:
            try:
                random_article = most_popular_pages.sample(1)
                page = wikipedia.page(random_article)
                if self.page_is_ok(page):
                    page_found = True
            except wikipedia.exceptions.PageError:
                pass
        return page

    def check_end(self, f_pressed : bool):
        return (len(self.entities) == 0) or f_pressed
    
    def play(self):
        print(self.first_summary)
        f_pressed : bool = False
        while not self.check_end(f_pressed):
            print("<!> HELP <!>")
            print("Hit enter to fill one blank, hit f if you found")
            char_put = input()
            enter_pressed = (char_put == "")
            f_pressed = (char_put == 'f')
            if enter_pressed:
                self.show_summary_with_less_entities()
                print(self.summary)
        if f_pressed:
            print("What's your answer (don't be aware of the case) ?")
            answer = str(input())
            found = (fuzz.partial_ratio(unidecode(answer.lower()),unidecode(self.title.lower())) > 70)
            if found:
                print("\n\n")
                print(f"Well Done !! {self.title} ")
            else:
                print(f"No, the answer was {self.title} :/")
        else:
            print(f"The answer was {self.title} :/")
        self.show_image()


    def replace_with_blank(self,text : str,entities : list):
        for ent in entities:
            text = text.replace(ent,'-' * len(ent))
        return text

    def show_summary_with_less_entities(self):
        entity_shown = self.entities[-1]
        self.summary = self.temp_summary.replace(entity_shown,f'\033[1m{entity_shown} \033[0m')
        self.entities = self.entities[:-1]
        self.summary = self.replace_with_blank(self.summary,self.entities)
        print(f"{entity_shown} shown !")



pedantix = LightPedantix()
pedantix.play()





