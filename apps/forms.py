from django import forms
from .models import ArticleComment

class ArticleCommentForm(forms.Form):
    body = forms.CharField(required=True,label="留言",
                              error_messages={'required':'好像空空阿，亲~','max_length':'想说的太多了，精简一些~','min_length':'再输入点内容吧'},
                              max_length=300,min_length=2,widget=forms.Textarea(attrs={'placeholder':'发表以下意见吧'}))

    user_name = forms.CharField(required=True,label="名字",
                               error_messages={'required':'好像空空阿，亲~','max_length':'有这么长的名字？？',},
                              max_length=300)
    class Meta:
        model = ArticleComment
        fields = ['body,user_name']


    def clean_body(self):
        message = self.cleaned_data['body']
        if "fuck" in message:
            raise forms.ValidationError('请文明用语')
        return message

    def clean_user_name(self):
        user_name = self.cleaned_data['user_name']
        if "admin" in user_name or "Admin" in user_name:
            raise forms.ValidationError('好像这名字不合适吧')
        return user_name