from flask_pagedown.fields import PageDownField
from flask_wtf import FlaskForm
from wtforms import SelectField, SubmitField, StringField, BooleanField
from wtforms.validators import DataRequired, length

category_list = ['未分类', '前端相关', 'Python', 'Nodejs', 'Flask中译']

class PublishForm(FlaskForm):
    title = StringField('文章标题', [length(0,60, '文章标题过长，请限制在60个字符内')])
    category = SelectField('请选择文章分类', [DataRequired()], default=['未分类'], choices = category_list)
    is_public = BooleanField('私密文章')
    content = PageDownField('请输入文章正文', [DataRequired()])
    submit = SubmitField('发表')
