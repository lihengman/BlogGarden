from django.shortcuts import render,redirect,HttpResponse

# Create your views here.
from django.contrib import auth
from blog.models import Article,UserInfo,Article2Tag
def login(request):
    if request.method=="POST":
        user=request.POST.get("user")
        pwd=request.POST.get("pwd")
        user=auth.authenticate(username=user,password=pwd)
        if user:
            auth.login(request,user)
            print(auth)
            return redirect("/cnblogs.com/")

    return render(request,"login.html")

def index(request):
    article_list=Article.objects.all()
    username_list=UserInfo.objects.all()
    return render(request, "index.html",{"article_list":article_list,"username_list":username_list})


def logout(request):
    auth.logout(request)
    return redirect("/index/")


def homesite(request,username,**kwargs):
    user=UserInfo.objects.filter(username=username).first()
    # print(user)
    if not user:
        return render(request,"not_found.html")
    blog=user.blog
    if not kwargs:
        article_list=Article.objects.filter(user__username=username)
    else:
        condition=kwargs.get("condition")
        params=kwargs.get("params")
        if condition=="category":
            article_list=Article.objects.filter(user__username=username).filter(category__title=params)
        elif condition=="tag":
            article_list=Article.objects.filter(user__username=username).filter(tags__title=params)
        else:
            year,month,day=params.split("/")
            article_list=Article.objects.filter(user__username=username).filter(create_time__year=year,create_time__month=month,create_time__day=day)
    if not article_list:
        return render(request, "not_found.html")

    return render(request,"homesite.html",locals())


def article_detail(request,username,article_id):
    user=UserInfo.objects.filter(username=username).first()
    blog=user.blog
    article_obj=Article.objects.filter(pk=article_id).first()
    comment_list = Comment.objects.filter(article_id=article_id)


    return render(request,"article_detail.html",locals())

from blog.models import ArticleUpDown,Comment,Category,Tag
import json
from django.http import JsonResponse
from django.db.models import F,Q
from django.db import transaction

def digg(request):
    is_up=json.loads(request.POST.get("is_up"))
    article_id=request.POST.get("article_id")
    user_id=request.user.pk
    response={"state":True,"msg":None}
    obj=ArticleUpDown.objects.filter(user_id=user_id,article_id=article_id).first()
    if obj:
        response["state"]=False
        response["handled"]=obj.is_up
    else:
        with transaction.atomic():
            new_obj=ArticleUpDown.objects.create(user_id=user_id,article_id=article_id,is_up=is_up)
            if is_up:
                Article.objects.filter(pk=article_id).update(up_count=F("up_count")+1)
            else:
                Article.objects.filter(pk=article_id).update(down_count=F("down_count")+1)

    return JsonResponse(response)


def comment(request):
    user_id=request.user.pk
    article_id=request.POST.get("article_id")
    content=request.POST.get("content")
    pid=request.POST.get("pid")
    with transaction.atomic():
        comment=Comment.objects.create(user_id=user_id,article_id=article_id,content=content,parent_comment_id=pid)
        Article.objects.filter(pk=article_id).update(comment_count=F("comment_count")+1)

    response={"state":True}
    response["timer"]=comment.create_time.strftime("%Y-%m-%d %X")
    response["content"]=comment.content
    response["user"]=request.user.username
    print(response)
    return JsonResponse(response)


def backend(request):
    user=request.user
    article_list=Article.objects.filter(user=user)
    return render(request,"backend/backend.html",locals())

from bs4 import BeautifulSoup
def add_article(request):
    if request.method=="POST":
        title=request.POST.get("title")
        user=request.user
        content=request.POST.get("content")
        print(content)
        cate_pk=request.POST.get("cate")
        tags_pk_list=request.POST.get("tags")

        soup = BeautifulSoup(content,"html.parser")

        for tag in soup.find_all():
            if tag.name in ["scrip"]:
                tag.decompose()
        desc=soup.text[0:150]
        article_obj=Article.objects.create(title=title,content=str(soup),user=user,category_id=cate_pk,desc=desc)

        for tag_pk in tags_pk_list:
            Article2Tag.objects.create(article_id=article_obj.pk,tag_id=tag_pk)

        return redirect("/backend/")

    else:
        blog=request.user.blog
        cate_list=Category.objects.filter(blog=blog)
        tags=Tag.objects.filter(blog=blog)

        return render(request, "backend/add_article.html", locals())

from BlogGarden import settings
import os
def upload(request):
    print(request.FILES)
    obj = request.FILES.get("upload_img")
    print(obj)
    # name=obj.name

    # # path=os.path.join(settings.BASE_DIR,"static","upload",name)
    # with open(path,"wb") as f:
    #     for line in obj:
    #         f.write(line)

    res={
        "error":0,
        "url":"/static/upload/"
    }
    return HttpResponse(json.dumps(res))

from blog import models
def edit_article(request,edit_article_id):
    article_obj=models.Article.objects.filter(pk=edit_article_id).first()
    blog=request.user.blog
    if request.method=="POST":
        title=request.POST.get("title")
        user=request.user
        content=request.POST.get("content")
        cate_pk=request.POST.get("cate")
        tags_pk_list=request.POST.get("tags")

        soup = BeautifulSoup(content,"html.parser")
        for tag in soup.find_all():
            if tag.name in ["scrip"]:
                tag.decompose()
        desc=soup.text[0:150]
        Article.objects.filter(pk=edit_article_id).update(title=title,content=str(soup),user=user,category_id=cate_pk,desc=desc)
        # new_article_obj =Article.objects.filter(pk=edit_article_id).first()
        # print(new_article_obj)

        Article2Tag.objects.filter(article_id=edit_article_id).delete()
        print(tags_pk_list,"******************")
        for tag_id in tags_pk_list:

            Article2Tag.objects.create(article_id=edit_article_id,tag_id=tag_id)

        return redirect("/backend/")

    else:
        blog=request.user.blog
        cate_list=Category.objects.filter(blog=blog)
        tags=Tag.objects.filter(blog=blog)

        return render(request, "backend/edit_article.html", locals())

def del_article(request,del_article_id):
    if request.method=="POST":
        del_article_pk=request.POST.get("del_article_id")
        models.Article.objects.filter(pk=del_article_id).delete()
    return redirect("/backend/")























