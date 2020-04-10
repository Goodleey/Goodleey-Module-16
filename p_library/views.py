import uuid
from django.shortcuts import render, redirect

# Create your views here.
from django.http import HttpResponse
from django.template import loader
from django.views.generic import CreateView, ListView, FormView
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy
from django.forms import formset_factory
from django.http.response import HttpResponseRedirect
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import auth
from django.core.exceptions import ObjectDoesNotExist
from allauth.socialaccount.models import SocialAccount
from p_library.models import Book, Publisher, Author, Friend, UserProfile
from p_library.forms import AuthorForm, BookForm, FriendForm, ProfileCreationForm


def books_list(request):
    books = Book.objects.all()
    return HttpResponse(books)


def get_context(request):
    context = {}
    if request.user.is_authenticated:
        context["username"] = request.user.username
        context["provider"] = SocialAccount.objects.get(user=request.user).provider
        context["age"] = SocialAccount.objects.get(user=request.user).extra_data["age"]
        if context["provider"] == "github":
            context['github_url'] = SocialAccount.objects.get(user=request.user).extra_data['html_url']
    return context


def home(request):
    try:
        context = get_context(request)
    except ObjectDoesNotExist:
        context = {}    
    template = loader.get_template('home.html')        
    return HttpResponse(template.render(context))


class CreateUserProfile(FormView):  

    form_class = ProfileCreationForm  
    template_name = 'profile-create.html'  
    success_url = reverse_lazy('app_root')  

    def dispatch(self, request, *args, **kwargs):  
        if self.request.user.is_anonymous:  
            return HttpResponseRedirect(reverse_lazy('login'))  
        return super(CreateUserProfile, self).dispatch(request, *args, **kwargs)  

    def form_valid(self, form):  
        instance = form.save(commit=False)  
        instance.user = self.request.user  
        instance.socacc, created = SocialAccount.objects.get_or_create(user=instance.user, defaults={"provider": "local", "uid": uuid.uuid1()})
        instance.socacc.extra_data["age"] = form.cleaned_data["age"]
        instance.socacc.save()
        if created:
            instance.save()  
        return super(CreateUserProfile, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)        
        try:
            context.update(get_context(self.request))
        except KeyError:
            pass
        except ObjectDoesNotExist:
            pass
        return context

    def get_initial(self):    
        initial = super().get_initial()        
        try:            
            initial['age'] = get_context(self.request)["age"]
        except KeyError:
            pass
        except ObjectDoesNotExist:
            pass
        return initial


def index(request):   
    if request.user.is_anonymous:
         return HttpResponseRedirect(reverse_lazy('login'))
    template = loader.get_template('index.html')    
    books = Book.objects.all()
    biblio_data = {
        "title": "мою библиотеку",        
        "books": books,        
    }
    biblio_data.update(get_context(request))
    return HttpResponse(template.render(biblio_data, request))


class indexL(ListView):    
    model = Book    
    context_object_name = "books"
    template_name = "index.html"     

    def dispatch(self, request, *args, **kwargs):  
        if self.request.user.is_anonymous:  
            return HttpResponseRedirect(reverse_lazy('login'))  
        return super(indexL, self).dispatch(request, *args, **kwargs)     

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(get_context(self.request))
        return context


def book_increment(request):
    if request.user.is_anonymous:
         return HttpResponseRedirect(reverse_lazy('login'))
    if request.method == 'POST':
        book_id = request.POST['id']
        if not book_id:
            return redirect('/index/')
        else:
            book = Book.objects.filter(id=book_id).first()
            if not book:
                return redirect('/index/')
            book.copy_count += 1
            book.save()
        return redirect('/index/')
    else:
        return redirect('/index/')


def book_decrement(request):
    if request.user.is_anonymous:
         return HttpResponseRedirect(reverse_lazy('login'))
    if request.method == 'POST':
        book_id = request.POST['id']
        if not book_id:
            return redirect('/index/')
        else:
            book = Book.objects.filter(id=book_id).first()
            if not book:
                return redirect('/index/')
            if book.copy_count < 1:
                book.copy_count = 0
            else:
                book.copy_count -= 1
            book.save()
        return redirect('/index/')
    else:
        return redirect('/index/')



def pubs(request):    
    if request.user.is_anonymous:
         return HttpResponseRedirect(reverse_lazy('login'))
    template = loader.get_template('pubs.html')    
    pubs = Publisher.objects.all()
    pub_data = {
        "pubs": pubs,
    }
    pub_data.update(get_context(request))
    return HttpResponse(template.render(pub_data, request))


class AuthorEdit(CreateView):  
    model = Author  
    form_class = AuthorForm  
    success_url = reverse_lazy('p_library:authors_list')  
    template_name = 'authors_edit.html'

    def dispatch(self, request, *args, **kwargs):  
        if self.request.user.is_anonymous:  
            return HttpResponseRedirect(reverse_lazy('login'))  
        return super(AuthorEdit, self).dispatch(request, *args, **kwargs)     

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(get_context(self.request))
        return context


class AuthorList(ListView):  
    model = Author  
    template_name = 'authors_list.html'

    def dispatch(self, request, *args, **kwargs):  
        if self.request.user.is_anonymous:  
            return HttpResponseRedirect(reverse_lazy('login'))  
        return super(AuthorList, self).dispatch(request, *args, **kwargs)     

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(get_context(self.request))
        return context


def author_create_many(request):  
    if request.user.is_anonymous:
         return HttpResponseRedirect(reverse_lazy('login'))
    AuthorFormSet = formset_factory(AuthorForm, extra=2)  #  Первым делом, получим класс, который будет создавать наши формы. Обратите внимание на параметр `extra`, в данном случае он равен двум, это значит, что на странице с несколькими формами изначально будет появляться 2 формы создания авторов.
    if request.method == 'POST':  #  Наш обработчик будет обрабатывать и GET и POST запросы. POST запрос будет содержать в себе уже заполненные данные формы
        author_formset = AuthorFormSet(request.POST, request.FILES, prefix='authors')  #  Здесь мы заполняем формы формсета теми данными, которые пришли в запросе. Обратите внимание на параметр `prefix`. Мы можем иметь на странице не только несколько форм, но и разных формсетов, этот параметр позволяет их отличать в запросе.
        if author_formset.is_valid():  #  Проверяем, валидны ли данные формы
            for author_form in author_formset:  
                author_form.save()  #  Сохраним каждую форму в формсете
            return HttpResponseRedirect(reverse_lazy('p_library:authors_list'))  #  После чего, переадресуем браузер на список всех авторов.
    else:  #  Если обработчик получил GET запрос, значит в ответ нужно просто "нарисовать" формы.
        author_formset = AuthorFormSet(prefix='authors')  #  Инициализируем формсет и ниже передаём его в контекст шаблона.
    return render(request, 'manage_authors.html', {'author_formset': author_formset})


def books_authors_create_many(request):  
    if request.user.is_anonymous:
         return HttpResponseRedirect(reverse_lazy('login'))
    AuthorFormSet = formset_factory(AuthorForm, extra=2)  
    BookFormSet = formset_factory(BookForm, extra=2)  
    if request.method == 'POST':  
        author_formset = AuthorFormSet(request.POST, request.FILES, prefix='authors')  
        book_formset = BookFormSet(request.POST, request.FILES, prefix='books')  
        if author_formset.is_valid() and book_formset.is_valid():  
            for author_form in author_formset:  
                author_form.save()  
            for book_form in book_formset:  
                book_form.save()  
            return HttpResponseRedirect(reverse_lazy('p_library:authors_list'))  
    else:  
        author_formset = AuthorFormSet(prefix='authors')  
        book_formset = BookFormSet(prefix='books')  
    return render(
	    request,  
		'manage_books_authors.html',  
		{  
	        'author_formset': author_formset,  
			'book_formset': book_formset,  
		}  
	)


class FriendEdit(CreateView):  
    model = Friend
    form_class = FriendForm  
    success_url = reverse_lazy('p_library:friends_list')  
    template_name = 'friends_edit.html'

    def dispatch(self, request, *args, **kwargs):  
        if self.request.user.is_anonymous:  
            return HttpResponseRedirect(reverse_lazy('login'))  
        return super(FriendEdit, self).dispatch(request, *args, **kwargs)     

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(get_context(self.request))
        return context


class FriendsList(ListView):  
    model = Friend  
    template_name = 'friends_list.html'

    def dispatch(self, request, *args, **kwargs):  
        if self.request.user.is_anonymous:  
            return HttpResponseRedirect(reverse_lazy('login'))  
        return super(FriendsList, self).dispatch(request, *args, **kwargs)     

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(get_context(self.request))
        return context


def lended(request):    
    if request.user.is_anonymous:
         return HttpResponseRedirect(reverse_lazy('login'))
    template = loader.get_template('lended.html')    
    lends = Book.objects.exclude(lendedto=None)
    lend_data = {
        "lends": lends,
    }
    lend_data.update(get_context(request))
    return HttpResponse(template.render(lend_data, request))


def lend_return(request):    
    if request.user.is_anonymous:
         return HttpResponseRedirect(reverse_lazy('login'))
    template = loader.get_template('lend_return.html')    
    books = Book.objects.all()
    friends = Friend.objects.all()
    biblio_data = {
        "title": "мою библиотеку",        
        "books": books,        
        "friends": friends,
    }
    biblio_data.update(get_context(request))
    return HttpResponse(template.render(biblio_data, request))


def do_lend_return(request):
    if request.user.is_anonymous:
         return HttpResponseRedirect(reverse_lazy('login'))
    if request.method == 'POST':
        book_id = request.POST['id'] # Получает book_id
        friend = request.POST.get("fid", None) # Получает friend id
        if not book_id:
            return redirect('/p_library/lend_return')
        else:
            book = Book.objects.filter(id=book_id).first()
            if not book:
                return redirect('/p_library/lend_return') # Если нет книги, возвращается на страницу
            if friend is None:
                book.lendedto = None # Если нет id друга, то возвращает книгу домой
            else:
                friend = Friend.objects.filter(id=friend).first() # Получает друга
                if not friend:
                    return redirect('/p_library/lend_return')                
                book.lendedto = friend # Одалживает книгу
            book.save()
        return redirect('/p_library/lend_return')
    else:
        return redirect('/p_library/lend_return')