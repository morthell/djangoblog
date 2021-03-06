from django.shortcuts import render, get_object_or_404
from .models import Post, Comment
from django.core.paginator import  Paginator, EmptyPage, PageNotAnInteger
from django.views.generic import ListView
from .forms import EmailPostForm, CommentForm
from django.core.mail import send_mail

#widok oparty na klasie
class PostListView(ListView):
    queryset = Post.published.all()
    context_object_name = 'posts'
    paginate_by = 3
    template_name = 'blog/post/list.html'

def post_list(request):
    object_list = Post.published.all()
    paginator = Paginator(object_list, 3)  # Trzy posty na każdej stronie
    page = request.GET.get('page')
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        # Jeżeli zmienna page nie jest liczbą całkowitą,
        # wówczas pobierana jest pierwsza strona wyników.
        posts = paginator.page(1)
    except EmptyPage:
        # Jeżeli zmienna page ma wartość większą niż numer ostatniej strony
        # wyników, wtedy pobierana jest ostatnia strona wyników.
        posts = paginator.page(paginator.num_pages)

    return render(request,
                        'blog/post/list.html',
                        {'page': page,
                            'posts': posts})

def post_detail(request, year, month, day, post):
    post = get_object_or_404(Post,  slug=post,
                                    status='published',
                                    publish__year=year,
                                    publish__month=month,
                                    publish__day=day)

    #lista aktywnych komentarzy dla danego posta
    comments = post.comments.filter(active=True)

    if request.method == 'POST':
        comment_form = CommentForm(data=request.POST)
        if comment_form.is_valid():
            new_comment = comment_form.save(commit=False)
            new_comment.post = post
            new_comment.save()
    else:
        comment_form = CommentForm()



    return render(request,
                  'blog/post/detail.html',
                  {'post': post,
                   'comments': comments,
                    'comment_form': comment_form})


##Formularz wysylania emaila

def post_share(request, post_id):
    post = get_object_or_404(Post, id=post_id, status = 'published')
    sent = False

    if request.method == 'POST':
        #formularz zostal wyslany
        form = EmailPostForm(request.POST)
        if form.is_valid():
            #Weryfikacja pol formularza zakonczyla sie powodzeniem
            cd = form.cleaned_data
            post_url = request.build_absolute_uri(post.get_absolute_url())
            subject = '{} ({}) zacheca do przeczytania "{}"'.format(cd['name'], cd['email'], post.title)
            message = 'Przeczytaj post "{}" na stronie {}\n\n Komentarz dodany przez {}:{}'.format(post.title, post_url, cd['name'], cd['comments'])
            send_mail(subject, message, 'morthell@gmail.com', [cd['to']])
            sent = True
            #mozna wyslac wiadomosc email
    else:
        form = EmailPostForm()
    return render(request, 'blog/post/share.html', {'post': post,
                                                    'form': form,
                                                    'sent': sent})

