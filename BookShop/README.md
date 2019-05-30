基于Django的旧时光书店项目
------------------------------------------------------------------

    项目描述：		
	    1.实现一个线上书店电商项目，让用户能够浏览选择并且生成订单进行购买；	
	    2.项目团队4人，使用MySQL数据库。负责功能：用户和权限模块、商品管理模块、数据接口模块等；	
    责任描述：		
        1.分析需求,明确项目职责。首先创建相关模型并且注册到管理后台中；	
        2.创建用户的身份验证系统提供注册、登录和登出等功能，然后将商品加入管理后台；	
        3.创建购物车系统，使用缓存框架来保存着用户的商品，最后能够生成订单；	
        4.创建一个简单的接口(RESTful API),方便与其它程序进行数据交互；
      

**用户模块**

  1.登陆视图
    
    def user_login(request):
        if request.method == "POST":
            form = LoginForm(request.POST)
            if form.is_valid():
                cd = form.cleaned_data
                user = authenticate(request, username=cd['username'], password=cd['password'])
                if user is not None:
                    if user.is_active:
                        login(request, user)
                        return HttpResponseRedirect('/', {'new_user': user})
                    else:
                        return HttpResponse("Disabled account")
                else:
                    return HttpResponse("Invalid login")
        else:
            form = LoginForm()
    
        return render(request, 'shop/account/login.html', {'form': form})

  2.注册视图

    def user_register(request):
        if request.method == "POST":
            user_form = UserRegistrationForm(request.POST)
            if user_form.is_valid():
                new_user = user_form.save(commit=False)
                # 设置密码
                new_user.set_password(user_form.cleaned_data['password'])
                # 保存User对象
                new_user.save()
                return HttpResponseRedirect('/login/')
        else:
            user_form = UserRegistrationForm()
        return render(request, 'shop/account/register.html', {'user_form': user_form})
    
  3.登出视图
  
    @login_required
    def user_logout(request):
        logout(request)
        return HttpResponseRedirect("/login/")


**接口设计**
  
  1.商品模块
    
    # 序列化
    class PostSerializer(serializers.ModelSerializer):
        class Meta:
            model = Post
            fields = '__all__'
            depth = 2
            
    # 视图
    class PostViewSet(viewsets.ModelViewSet):
        queryset = Post.objects.all()
        serializer_class = PostSerializer
        pagination_class = MyPagination

    #权限认证和分页操作
    REST_FRAMEWORK = {
        'DEFAULT_PERMISSION_CLASSES': [
            'rest_framework.permissions.DjangoModelPermissionsOrAnonReadOnly',
        ],
        'PAGINATE_BY': 10
    }

**商品列表页和详情页**
  
  1.列表页
  
    def product_list(request, category_slug=None):
        category = None
        categories = Category.objects.all()
        products = Product.objects.filter(available=True)
        if category_slug:
            category = get_object_or_404(Category, slug=category_slug)
            products = products.filter(category=category)
        return render(request,
                      'shop/product/list.html',
                      {'category': category,
                       'categories': categories,
                       'products': products})
  
  2.详情页
    
    def product_detail(request, id, slug):
        product = get_object_or_404(Product,
                                    id=id,
                                    slug=slug,
                                    available=True)
        cart_product_form = CartAddProductForm()
        return render(request,
                      'shop/product/detail.html',
                      {'product': product,
                       'cart_product_form': cart_product_form})

**购物车**
    
    def cart_add(request, product_id):
        cart = Cart(request)
        product = get_object_or_404(Product, id=product_id)
        form = CartAddProductForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            cart.add(product=product,
                     quantity=cd['quantity'],
                     update_quantity=cd['update'])
        return redirect('cart:cart_detail')


    def cart_remove(request, product_id):
        cart = Cart(request)
        product = get_object_or_404(Product, id=product_id)
        cart.remove(product)
        return redirect('cart:cart_detail')
    
    
    def cart_detail(request):
        cart = Cart(request)
        for item in cart:
            item['update_quantity_form'] = CartAddProductForm(
                initial={'quantity': item['quantity'],
                         'update': True})
        return render(request, 'cart/detail.html', {'cart': cart})

**个人博客**

   1. 模型
    
    # 博客
    class Post(models.Model): 
        STATUS_CHOICES = ( 
            ('draft', 'Draft'), 
            ('published', 'Published'), 
        ) 
        title = models.CharField(max_length=250) 
        slug = models.SlugField(max_length=250,  
                                unique_for_date='publish') 
        author = models.ForeignKey(User, 
                                   on_delete=models.CASCADE,
                                   related_name='blog_posts') 
        body = models.TextField() 
        publish = models.DateTimeField(default=timezone.now) 
        created = models.DateTimeField(auto_now_add=True) 
        updated = models.DateTimeField(auto_now=True) 
        status = models.CharField(max_length=10,  
                                  choices=STATUS_CHOICES, 
                                  default='draft') 
        
        objects = models.Manager() # The default manager. 
        published = PublishedManager() # Our custom manager.
        tags = TaggableManager()
    
        class Meta: 
            ordering = ('-publish',) 
    
        def __str__(self): 
            return self.title
    
        def get_absolute_url(self):
            return reverse('blog:post_detail',
                           args=[self.publish.year,
                                 self.publish.month,
                                 self.publish.day,
                                 self.slug])
    
    # 评论
    class Comment(models.Model): 
        post = models.ForeignKey(Post,
                                 on_delete=models.CASCADE,
                                 related_name='comments')
        name = models.CharField(max_length=80) 
        email = models.EmailField() 
        body = models.TextField() 
        created = models.DateTimeField(auto_now_add=True) 
        updated = models.DateTimeField(auto_now=True) 
        active = models.BooleanField(default=True) 
     
        class Meta: 
            ordering = ('created',) 
     
        def __str__(self): 
            return 'Comment by {} on {}'.format(self.name, self.post)
            
   
   2.视图
        
    class PostListView(ListView):
        queryset = Post.published.all()
        context_object_name = 'posts'
        paginate_by = 3
        template_name = 'blog/post/list.html'