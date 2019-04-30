from django.shortcuts import render, redirect
from mysite import models, forms
from django.core.mail import EmailMessage
from django.contrib.sessions.models import Session
from django.contrib import messages

# Create your views here.
def index(request):
	if 'username' in request.session:
		username = request.session['username']
		useremail = request.session['useremail']
	return render(request, 'index.html', locals())

def listing(request):
	posts = models.Post.objects.filter(enabled=True).order_by('-pub_time')[:150]
	moods = models.Mood.objects.all()
	return render(request, 'listing.html', locals())

def posting(request):
	moods = models.Mood.objects.all()
	try:
		user_id = request.POST['user_id']
		user_pass = request.POST['user_pass']
		user_post = request.POST['user_post']
		user_mood = request.POST['mood']
	except:
		user_id = None
		message = '如要張貼訊息，則每一欄都要填寫...'
	
	if user_id != None:
		mood = models.Mood.objects.get(status=user_mood)
		post = models.Post.objects.create(mood=mood, nickname=user_id, del_pass=user_pass, message=user_post)
		post.save()
		message='儲存成功! 請記得你的編輯密碼 [{}]!，訊息審查後才會顯示。'.format(user_pass)
		
	return render(request, 'posting.html', locals())


def contact(request):
	if request.method == 'POST':
		form = forms.ContactForm(request.POST)
		if form.is_valid():
			message = "感謝您的來信"
			user_name = form.cleaned_data['user_name']
			user_city = form.cleaned_data['user_city']
			user_school = form.cleaned_data['user_school']
			user_email = form.cleaned_data['user_email']
			user_message = form.cleaned_data['user_message']
			
			mail_body = u'''
網友姓名:{}
居住城市:{}
是否在學:{}
反應意見如下:
{}'''.format(user_name, user_city, user_school, user_message)


			email = EmailMessage( '來自我的[心情告示板]網站的網友意見', mail_body, user_email, ['alex03108861@yahoo.com.tw'])
			email.send()
		else:
			message = "請檢查您輸入的資訊是否正確! "
	else:
		form = forms.ContactForm()
	return render(request, 'contact.html', locals())

def post2db(request):
	if request.method == 'POST':
		post_form = forms.PostForm(request.POST)
		if post_form.is_valid():
			message = "您的訊息已儲存，待審核。"
			post_form.save()
		else:
			message = "每個欄位都要填喔"
	else:
		post_form = forms.PostForm()
		message = '如要張貼訊息，則每一欄都要填寫'

	return render(request, 'post2db.html', locals())
	
def login(request):
	if request.method == 'POST':
		login_form = forms.LoginForm(request.POST)
		if login_form.is_valid():
			login_name = request.POST['username']
			login_password = request.POST['password']
			try:
				user = models.User.objects.get(name = login_name)
				if user.password == login_password:
					request.session['username'] = user.name
					request.session['useremail'] = user.email
					messages.add_message(request, messages.SUCCESS, "成功登入了")
					return redirect('/')
				else:
					messages.add_message(request, messages.WARNING, "密碼錯誤，請再檢查一次")
			except:
				messages.add_message(request, messages.WARNING, "找不到使用者")
		else:
			messages.add_message(request, messages.INFO, "請檢查輸入的欄位內容")
	else:
		login_form = forms.LoginForm()
		
	return render(request, 'login.html', locals())
	
def logout(request):
	Session.objects.all().delete()
	return redirect('/login/')
	
def userinfo(request):
	if 'username' in request.session:
		username = request.session['username']
	else:
		return redirect('/login/')
	try:
		userinfo = models.User.objects.get(name=username)
	except:
		pass
	return render(request, 'userinfo.html', locals())
