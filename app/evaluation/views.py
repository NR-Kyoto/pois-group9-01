from django.shortcuts import render
from django.http import HttpResponse
import language_tool_python

def evaluationpage(request):

    sentance = 'Last weak, I goed to the librery to borrow some bookes. I was very hungary so I eated some pizza on the way. When I arrived at the librery, I realized that I left my library card at home. So, I borowed a book without checking it out. The librery staff was very mad at me and asked me to leave immediately. I said I was sorry, but they didn\'t accepted my apology. After that, I goed home and sleeped for a few hours.'

    matches = evaluate_grammar(sentance)
    text = '<h3>' + sentance + '</h3>'
    for match in matches:

        text += '<div>'
        # text += '<p>' + match.category + '</p>'
        # text += '<p>' + match.message + '</p>'
        output = str(match)
        text += output.replace('\n', '<br>')
        
        text += '</div>'
        print(match)

    return HttpResponse(text)

def evaluate_grammar(text):
    
    tool = language_tool_python.LanguageTool('en-US')  # use a local server (automatically set up), language English
    
    matches = tool.check(text)

    tool.close()

    return matches

