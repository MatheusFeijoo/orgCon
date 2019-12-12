# -*- coding: utf-8 -*-
#sudo python3 -m pip install googletrans
import spotlight
import pandas
import re
import csv
import time
import emoji
from time import sleep
from googletrans import Translator
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

HOSTPT = 'http://api.dbpedia-spotlight.org/pt/annotate'
#HOSTEN = 'http://api.dbpedia-spotlight.org/en/annotate'

codUser = '1'
sentimentoPos = '0.0'
sentimentoNeg = '0.0'
urlDBP = 'www'
confEnt = '0'



HOSTPT = 'http://api.dbpedia-spotlight.org/pt/annotate'
def get_annotationsPT(text):
    while True:
        try:
            annotationsPT = spotlight.annotate(HOSTPT, text, confidence=0.35, support=10) 
        except spotlight.SpotlightException:
            return None
        return annotationsPT
   





def do_sentAnalysis (text):
    analyzer = SentimentIntensityAnalyzer()
    scores = analyzer.polarity_scores(text)
    return scores





def do_translation(text):
    translator = Translator()
    ex = translator.translate(text)
    return ex

def extract_emojis(text):
    return emoji.demojize(text)




def remove_emoji(text):
    return emoji.get_emoji_regexp().sub(u'', text)

#tweetsEmoji = [re.sub(RE_EMOJI, '', i) for i in tweets]



def adc_na_tripla (text):
    for i in range(len(tweets)):
        print(i)
        codTweet = str(tweets[0][i])
        tempo = str(tweets[1][i])
        texto = str(tweets[2][i])
        textoAUX = texto.replace('RT','')
        textoPT = emoji.demojize(textoAUX)
        rt = str(tweets[3][i])
        likes = str(tweets[4][i])
        
        with open("datasetBolsonaro.n3", "a") as f:
            #Base de todos os dados
            f.write('\n' + ':t' + codTweet + ' rdf:type sioc:Post ; dc:created "' + tempo + '"^^xsd:dateTime ; ' + 'sioc:id "' + codTweet + '" ; ' + 'sioc:has_creator :u' + codUser + ' ; onyx:hasEmotionSet :es' + codTweet + ' ; schema:interactionStatistic :i' + codTweet + '_1, :i' + codTweet + '_2 .' + '\n') 
            f.write(':u' + codUser + ' rdf:type sioc:UserAccount ; ' +  'sioc:id "' + codUser + '" .' + '\n')
            f.write(':i' + codTweet + '_1 rdf:type schema:InteractionCounter ; schema:interactionType schema:LikeAction ; schema:userInteractionCount "' + likes + '"^^xsd:integer .' + '\n')
            f.write(':i' + codTweet + '_2 rdf:type schema:InteractionCounter ; schema:interactionType schema:ShareAction ; schema:userInteractionCount "' + rt + '"^^xsd:integer .' + '\n')
            
            #Parte de emoções
            textoEN = do_translation(textoPT)
            traduzidoEN = re.search('text=(.*), pronunciation=', str(textoEN))
            var = traduzidoEN.group(1)
            senti = do_sentAnalysis(var)
            sentimentoPos = str(senti['pos'])
            sentimentoNeg = str(senti['neg'])
            f.write(':es' + codTweet + ' rdf:type onyx:EmotionSet ; onyx:hasEmotion :em' + codTweet + 'Pos, :em' + codTweet +'Neg .' + '\n')
            f.write(':em' + codTweet + 'Pos onyx:hasEmotionCategory wna:positive-emotion ; onyx:hasEmotionIntensity "' + sentimentoPos + '"^^xsd:double .' + '\n')
            f.write(':em' + codTweet + 'Neg onyx:hasEmotionCategory wna:negative-emotion ; onyx:hasEmotionIntensity "' + sentimentoNeg + '"^^xsd:double .' + '\n')
            
            spotlightPT = get_annotationsPT(textoPT)
            time.sleep(5)
            datasetSpolightPT = pandas.DataFrame(spotlightPT)
            #Se tiver alguma coisa da DBpedia
            if len(datasetSpolightPT) != 0:
                for varDatasetSpolightPT in range(len(datasetSpolightPT)):                    
                    URI = datasetSpolightPT.loc[varDatasetSpolightPT,"URI"]
                    pegou = datasetSpolightPT.loc[varDatasetSpolightPT,"surfaceForm"]
                    score = datasetSpolightPT.loc[varDatasetSpolightPT,"similarityScore"]                    
                    f.write(':t' + codTweet +' schema:mentions :e' + codTweet + '_'+ str(varDatasetSpolightPT) +' .' + '\n')
                    f.write(':e' + codTweet + '_' + str(varDatasetSpolightPT) + ' rdf:type nee:Entity ; nee:detectedAs "' + str(pegou) + '" ; nee:hasMatchedURI <' + str(URI) + '> ; nee:confidence "' + str(score) + '"^^xsd:double .' + '\n')
            
            #Se tiver alguma hashtag
            hashtag = re.findall(r'#(.*?)\ ', textoPT)
            if len(hashtag) != 0 :
                for varHashtag in range(len(hashtag)):
                    f.write(':t' + codTweet + ' schema:mentions :h' + codTweet + '_'+ str(varHashtag) +' .' + '\n')
                    f.write(':h' + codTweet + '_' + str(varHashtag) + ' rdf:type sioc_t:Tag ; rdfs:label "' + hashtag[varHashtag] + '" .' + '\n')        
            
            #Se cita algum usuário
            arroba = re.findall(r'@(.*?)\ ', textoPT)
            if len(arroba) != 0 :
                for varArroba in range(len(arroba)):
                    f.write(':t' + codTweet + ' schema:mentions :a' + codTweet + '_'+ str(varArroba) +' .' + '\n')
                    f.write(':a' + codTweet + '_' + str(varArroba) + ' rdf:type sioc_t:Microblog ; rdfs:label "' + arroba[varArroba] + '" .' + '\n')                
            f.close()
        
    return ('Feito')
    

tweets = pandas.read_csv('jairbolsonaro.csv', sep = ';', header = None)
status = adc_na_tripla(tweets)
print(status)
#s = 'asdf=5;iwantthis123jasd'
#result = re.search('text=(.*), pronunciation=', tran)
#print(result.group(1))

'''
for i in range(len(tweets)):
    tran = str(do_translation(tweets[2][i]))
    result = re.search('text=(.*), pronunciation=', tran)
    print(result.group(1))
'''

'''
##########  Pegando direto do arquivo
codTweet = str(tweets[0][1])
tempo = str(tweets[1][1])
texto = str(tweets[2][20])
rt = str(tweets[3][1])
likes = str(tweets[4][1])
###pega todas as hashtags
print('# citadas:' + str(re.findall(r'#(.*?)\ ', texto)))
print('@ citadas:' + str(re.findall(r'@(.*?)\ ', texto)))
##########

print(texto)
print('----------------')
varPT = get_annotationsPT(texto)
#print(varPT)
print('----------------')
varPTpanda = pandas.DataFrame(varPT)
#print(varPTpanda.loc[3,"URI"])
print('----------------')
#varEN = get_annotationsEN(texto)
#print (varEN)


for i in range(len(varPTpanda)):
    print(varPTpanda.loc[i,"URI"])


tran = do_translation(text)
print(tran)



'''


#curl http://api.dbpedia-spotlight.org/en/annotate  \
#>   --data-urlencode "text=President Obama called Wednesday on Congress to extend a tax break
#>   for students included in last year's economic stimulus package, arguing
#>   that the policy provides more generous assistance." \
#>   --data "confidence=0.35"