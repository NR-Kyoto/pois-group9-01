from django.shortcuts import render
from django.http import HttpResponse
import language_tool_python

check_categories = ['CONFUSED_WORDS', 'GRAMMAR', 'REPETITIONS']

def evaluationpage(request):

    # sentance = 'Last weak, I goed to the librery to borrow some bookes. I was very hungary so I eated some pizza on the way. When I arrived at the librery, I realized that I left my library card at home. So, I borowed a book without checking it out. The librery staff was very mad at me and asked me to leave immediately. I said I was sorry, but they didn\'t accepted my apology. After that, I goed home and sleeped for a few hours.'
    sentance = 'I goed to the market yesterdy to buy some apple. But they were very expensive, so I couldn\'t bought them. After that, I went to a cafe to eat a sandwich and drinked some coffee. While I was eating, I saw an old friend of mine. I goed to talk to him and we had a nice conversation. He told me that he had buyed a new car and he was very happy with it. After the conversation, I goed home and watched a movie. The movie was very boring, so I sleeped halfway through.'

    matches = evaluate_grammar(sentance)
    text = '<h3>' + sentance + '</h3>'
    for match in matches:

        # text += '<div>'
        # text += '<p>' + match.category + '</p>'
        # output = str(match)
        # text += output.replace('\n', '<br>')

        # text += '</div>'
        
        if match.category in check_categories:
            text += '<div>'
            text += '<p>' + match.category + '</p>'
            output = str(match)
            text += output.replace('\n', '<br>')

            text += '</div>'

    return HttpResponse(text)

def evaluate_grammar(text):
    
    tool = language_tool_python.LanguageTool('en-US')  # use a local server (automatically set up), language English
    
    matches = tool.check(text)

    tool.close()

    return matches

