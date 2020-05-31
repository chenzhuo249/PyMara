"""
2020/5/22 修改
"""

from django.db import models

from user.models import User, UserHistory
from Public.publicmodel import PublicModel


class Blog(PublicModel):
    """
        博客核心表
        用户表一对多
    """
    BLOG_STATUS_CHOICES = (
        ('1', '已发布'),
        ('2', '编辑中'),
        ('3', '已删除'),
    )
    title = models.CharField(verbose_name='标题', max_length=32)
    abstract = models.CharField(verbose_name='摘要', max_length=96)
    original = models.BooleanField(verbose_name='原创', default=True)
    author = models.IntegerField(verbose_name='作者')
    status = models.CharField(verbose_name='状态', choices=BLOG_STATUS_CHOICES, max_length=1, default='1')
    category = models.CharField(verbose_name='分类', max_length=16, db_index=True)
    is_show = models.BooleanField(verbose_name='展示', default=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)


class Content(PublicModel):
    """
        内容表
        博客表一对一
    """
    content = models.TextField(verbose_name='博客内容')
    blog = models.OneToOneField(Blog, on_delete=models.CASCADE)


class Annex(PublicModel):
    """
        附件表
        博客表一对多
    """
    name = models.CharField(verbose_name='名字', max_length=16)
    filed = models.FileField(verbose_name='文件', upload_to='annex')
    price = models.DecimalField(verbose_name='价格', max_digits=5, decimal_places=1, default=1.0)
    blog = models.ForeignKey(Blog, on_delete=models.PROTECT)


class Tag(PublicModel):
    """
        标签表
        博客表一对多
    """
    tag = models.CharField(verbose_name='标签名', max_length=16)
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE)


class BlogHistory(PublicModel):
    """
        博客记录表
        博客表一对一
    """
    comment = models.IntegerField(verbose_name='评论', default=0)
    favorite = models.IntegerField(verbose_name='收藏', default=0)
    praise = models.IntegerField(verbose_name='点赞', default=0)
    browse = models.IntegerField(verbose_name='浏览', default=0)
    score = models.IntegerField(verbose_name='总分', default=0)
    blog = models.OneToOneField(Blog, on_delete=models.CASCADE)

    class Meta:
        ordering = ['score']


class BrowserHistory(PublicModel):
    """
        浏览记录表
        博客表一对多
        用户表一对多
    """
    praise = models.BooleanField(verbose_name='点赞', default=False)
    is_active = models.BooleanField(verbose_name='活跃', default=True)
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)


class Favorite(PublicModel):
    """
        收藏夹表
        用户表一对多
        博客表一对多
    """
    name = models.CharField(verbose_name='名字', max_length=7, default='默认收藏夹')
    public = models.BooleanField(verbose_name='公开', default=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE)


class Comment(PublicModel):
    """
        评论表
        博客表一对多
        用户记录表一对多
    """
    MESSAGE_GENRE_CHOICES = (
        ('text', '文本'),
        ('img', '图片'),
        ('link', '链接'),
    )
    genre = models.CharField(verbose_name='消息类型', choices=MESSAGE_GENRE_CHOICES, max_length=4)
    child_comment_id = models.IntegerField(verbose_name='子评论', null=True)
    blog = models.ForeignKey(Blog, on_delete=models.PROTECT)
    user_history = models.ForeignKey(UserHistory, on_delete=models.SET_NULL, null=True)


class CommentHistory(PublicModel):
    """
        评论内容表
        评论表一对一
    """
    text = models.CharField(verbose_name='文本', max_length=1024, null=True)
    img = models.ImageField(verbose_name='图片', upload_to='img/comment', null=True)
    link = models.CharField(verbose_name='链接', max_length=128, null=True)
    comment = models.OneToOneField(Comment, on_delete=models.CASCADE)
