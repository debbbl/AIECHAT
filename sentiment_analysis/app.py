import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import json
import faculty
import drawFigure


from flask import Flask , render_template , redirect , request

app = Flask(__name__)


with open('overall_experience.json') as file:
    json_string = file.read()
    documents1 = json.loads(json_string)
    
with open('content_and_sessions.json') as file:
    json_string = file.read()
    documents2 = json.loads(json_string)
    
with open('networking_opportunities.json') as file:
    json_string = file.read()
    documents3 = json.loads(json_string)
    
with open('value_and_impact.json') as file:
    json_string = file.read()
    documents4 = json.loads(json_string)
    

label2category = {1: 'positive' , 0: 'neutral' , -1: 'negative'}
category2label = {cat:label for label , cat in label2category.items()}


categories1 = [category2label[category] for doc , category in documents1]
categories2 = [category2label[category] for doc , category in documents2]
categories3 = [category2label[category] for doc , category in documents3]
categories4 = [category2label[category] for doc , category in documents4]


corpus1 = [' '.join(document) for document , cat in documents1]
corpus2 = [' '.join(document) for document , cat in documents2]
corpus3 = [' '.join(document) for document , cat in documents3]
corpus4 = [' '.join(document) for document , cat in documents4]



@app.route('/')
def display():
    return render_template('sentiment_analyzer.html')


@app.route('/' , methods=['POST'])
def caption():

    if request.method == 'POST':

        f = request.files["file_name"]
        path = "./static/{}".format(f.filename)     
        f.save(path)

        category_no = int(request.form['Cate'])

        df = pd.read_csv(path)

        cols1 = []
        cols2 = []
        cols3 = []
        cols4 = []

        substring1 = ['event', 'experience', 'program', 'occasion', 'function', 'gathering', 'activity', 'happening', 
              'celebration', 'festivity', 'get-together', 'conference', 'workshop', 'seminar', 'symposium', 
              'meeting', 'exhibition', 'convention', 'ceremony', 'competition']
        substring2 = ['content', 'session', 'topic', 'agenda', 'subject', 'material', 'program', 'lecture', 
              'presentation', 'discussion', 'workshop', 'seminar', 'training', 'course', 'class', 
              'tutorial', 'demonstration', 'panel', 'talk', 'keynote']
        substring3 = ['networking', 'opportunities', 'connections', 'contacts', 'network', 'interaction', 
              'collaboration', 'engagement', 'meetings', 'socializing', 'relationship', 'community', 
              'mixer', 'gatherings', 'conversations', 'exchanges', 'partnerships', 'alliances', 
              'contacts', 'communication']
        substring4 = ['value', 'impact', 'benefits', 'worth', 'significance', 'importance', 'contribution', 
              'influence', 'effect', 'outcome', 'advantage', 'value-added', 'consequence', 'result', 
              'effectiveness', 'efficacy', 'success', 'import', 'worthiness', 'merit']


        for i in list(df.columns):
            for j in substring1:
                if j.casefold() in i.casefold():
                    cols1.append(df.columns.get_loc(i))
                    if cols1 != []:
                        break
                        
        for i in list(df.columns):
            for j in substring2:
                if j.casefold() in i.casefold():
                    cols2.append(df.columns.get_loc(i))
                    if cols2 != []:
                        break    

        for i in list(df.columns):
            for j in substring3:
                if j.casefold() in i.casefold():
                    cols3.append(df.columns.get_loc(i))
                    if cols3 != []:
                        break
                        
        for i in list(df.columns):
            for j in substring4:
                if j.casefold() in i.casefold():
                    cols4.append(df.columns.get_loc(i))
                    if cols4 != []:
                        break
                
                        
        cols = cols1+cols2+cols3+cols4
        cols = list(set(cols))
        
        df_form = pd.read_csv(path , usecols = cols)
        reviews = np.array(df_form)
        
        pos1 , n1 , neg1 = faculty.predict(corpus1 , categories1 , reviews[: , 0])
        pos2 , n2 , neg2 = faculty.predict(corpus1 , categories1 , reviews[: , 1])
        pos3 , n3 , neg3 = faculty.predict(corpus1 , categories1 , reviews[: , 2])
        pos4 , n4 , neg4 = faculty.predict(corpus1 , categories1 , reviews[: , 3])

        results = {
            'f1' : 'Overall Experience',
            'pos1' : pos1,
            'n1' : n1,
            'neg1' : neg1,
            'f2' : 'Content and Sessions',
            'pos2' : pos2,
            'n2' : n2,
            'neg1' : neg2,
            'f3' : 'Networking Opportunities',
            'pos3' : pos3,
            'n3' : n3,
            'neg3' : neg3,
            'f4' : 'Value and Impact',
            'pos4' : pos4,
            'n4' : n4,
            'neg4' : neg4,
        }

        values = list([[pos1 , n1 , neg1], [pos2 , n2 , neg2], [pos3 , n3 , neg3], [pos4 , n4 , neg4]])
        labels = list(['Overall Experience', 'Content and Sessions', 'Networking Opportunities','Value and Impact'])
        
        print(values[category_no-1] , labels[category_no-1] , category_no , category_no-1)
        
        if category_no == 1:
            results_1 = {
                'f1' : 'Overall Experience',
                'pos1' : pos1,
                'n1' : n1,
                'neg1' : neg1
            }

            drawFigure.make(values[category_no-1] , labels[category_no-1] , category_no)

            return render_template('sentiment_analyzer1.html' , result1 = results_1 , cat = category_no) 


        elif category_no == 2:
            results_2 = {
                'f2' : 'Content and Sessions',
                'pos2' : pos2,
                'n2' : n2,
                'neg2' : neg2
            }

            drawFigure.make(values[category_no-1] , labels[category_no-1] , category_no)

            return render_template('sentiment_analyzer1.html' , result2 = results_2 , cat = category_no)


        elif category_no == 3:
            results_3 = {
                'f3' : 'Networking Opportunities',
                'pos3' : pos3,
                'n3' : n3,
                'neg3' : neg3
            }

            drawFigure.make(values[category_no-1] , labels[category_no-1] , category_no)

            return render_template('sentiment_analyzer1.html' , result3 = results_3 , cat = category_no)


        elif category_no == 4:
            results_4 = {
                'f4' : 'Value and Impact',
                'pos4' : pos4,
                'n4' : n4,
                'neg4' : neg4
            }

            drawFigure.make(values[category_no-1] , labels[category_no-1] , category_no)

            return render_template('sentiment_analyzer1.html' , result4 = results_4 , cat = category_no)

        else:            
            for i in range(0 , 4):
                fig = plt.figure(figsize=(8,8) , edgecolor='red' , linewidth=10)
                plt.bar(x = ['Positive' , 'Neutral' , 'Negative'] , height = values[i] , color=['blue','gold','red'])
                plt.title(labels[i], fontsize = 24, weight = 'demibold', pad = 15, fontstyle = 'italic' , family = 'cursive')
                plt.xticks(rotation=0 , fontsize=16)
                plt.yticks([])
                plt.xlabel('Feedback Type',fontsize = 18, labelpad=17, weight= 550 , family = 'cursive')
                plt.ylabel('')
                fig.subplots_adjust(bottom = 0.14)
                ax = plt.gca()
                ax.spines['right'].set_visible(False)
                ax.spines['top'].set_visible(False)
                ax.spines['left'].set_visible(False)
                for p in ax.patches:
                    ax.annotate("%.1f%%" % (100*float(p.get_height()/sum(values[i]))), (p.get_x() + p.get_width() / 2., abs(p.get_height())),
                    ha='center', va='bottom', color='black', xytext=(0, 5),rotation = 'horizontal',
                    textcoords='offset points', fontsize = 16 , fontweight = 'medium')
                plt.savefig(f'static/plot{i+10}.jpg')

            return render_template('sentiment_analyzer1.html' , result = results)  
    
    else:
        return render_template('error.html')


if __name__ == '__main__':
    app.run(debug=True)