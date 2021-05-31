from django.shortcuts import redirect, render
from .models import Document
from .forms import DocumentForm
import os
from .topic_model import Topic
from operator import itemgetter

def my_view(request):

    # 古いファイルを削除
    MAX_CNT = 20 #最大20ファイル, 
    num_del = 10 # 20ファイルになったら10ファイルを削除
    dir_path = "media/documents/"
    files = os.listdir(dir_path)
    filelists = []
    for file in files:
        full_path = dir_path + file
        filelists.append([full_path, os.path.getctime(full_path)])
    filelists.sort(key=itemgetter(1), reverse=True)
    if len(filelists) > MAX_CNT - 1:
        for i,file in enumerate(filelists):
            if i > MAX_CNT - 1 - num_del:
                os.remove(file[0])


    # print(f"Great! You're using Python 3.6+. If you fail here, use the right version.")
    message = '文書ファイルを選択してください。'
    # Handle file upload
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            newdoc = Document(docfile=request.FILES['docfile'])
            filepath = "media/documents/" + newdoc.docfile.name
            # print(filepath) 
            newdoc.save()

            # Redirect to the document list after POST
            # media/documents/example01.png
            # return redirect('my-view')

            # process text
            topic = Topic()
            num_topics = int(request.POST.get('num_topics'))
            no_below = int(request.POST.get('no_below'))
            no_above = float(request.POST.get('no_above'))
            separator = str(request.POST.get('separator'))
            
            visulize_path, vis_detail_path = topic.modeling(filepath, separator, num_topics=num_topics, no_below=no_below, no_above=no_above)

            # after processing delete hte file
            os.remove(filepath)

            # Load documents for the list page
            documents = Document.objects.all()

            # Render list page with the documents and the form
            context = {'documents': documents, 'form': form, 'message': message, 'vis_path': visulize_path, 'vis_detail_path': vis_detail_path}
            return render(request, 'list.html', context)

        else:
            message = 'The form is not valid. Fix the following error:'
    else:
        form = DocumentForm()  # An empty, unbound form

    # Load documents for the list page
    documents = Document.objects.all()

    # Render list page with the documents and the form
    context = {'documents': documents, 'form': form, 'message': message}
    return render(request, 'list.html', context)
