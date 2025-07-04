from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, JsonResponse
from .models import Blog
from django.db.models import Q


# GET: List all blogs for each pages 
# This functions dynamically call blogs for each page
def blog_dynamic():
    return Blog.objects.all().order_by('-created_at')


# GET: List all blogs
def blog_list(request):
    blogs = Blog.objects.all().order_by('-created_at')
    return render(request, 'blog/blog_list.html', {'blogs': blogs})

# GET: View single blog
def blog_detail(request, pk):
    blog = get_object_or_404(Blog, pk=pk)
    return render(request, 'blog/blog_detail.html', {'blog': blog})

# POST: Create blog manually
def blog_create(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        category = request.POST.get('category')
        image = request.FILES.get('image')  # Optional

        if title and description and category:
            blog = Blog.objects.create(
                title=title,
                description=description,
                category=category,
                image=image
            )
            return redirect('blog_detail', pk=blog.pk)
        else:
            return HttpResponse("Missing fields", status=400)

    return render(request, 'blog/blog_form.html')

# POST: Update blog manually
def blog_update(request, pk):
    blog = get_object_or_404(Blog, pk=pk)
    if request.method == 'POST':
        blog.title = request.POST.get('title')
        blog.description = request.POST.get('description')
        blog.category = request.POST.get('category')

        if request.FILES.get('image'):
            blog.image = request.FILES['image']

        blog.save()
        return redirect('blog_detail', pk=pk)

    return render(request, 'blog/blog_form.html', {'blog': blog})

# POST: Delete blog
def blog_delete(request, pk):
    blog = get_object_or_404(Blog, pk=pk)
    if request.method == 'POST':
        blog.delete()
        return redirect('blog_list')
    return render(request, 'blog/blog_confirm_delete.html', {'blog': blog})

# GET: Search blog
def blog_search(request):
    query = request.GET.get('q')
    blogs = Blog.objects.filter(
        Q(title__icontains=query) |
        Q(description__icontains=query) |
        Q(category__icontains=query)
    ) if query else Blog.objects.none()

    return render(request, 'blog/blog_list.html', {'blogs': blogs, 'query': query})
