from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import FormView, TemplateView, View
from .forms import *
from .models import CustomUserModel, UserFiles
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
from django.http import JsonResponse , HttpResponseNotFound
from django.contrib.auth import get_user_model

User = get_user_model()



class RegisterView(FormView):
    form_class = CustomUserCreationForm
    template_name = 'user/register.html'
    success_url = reverse_lazy('home')

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            messages.info(request, 'You are already registered and logged in.')
            return redirect('home')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        user = form.save(commit=False)

        if 'avatar' in self.request.FILES:
            user.avatar = self.request.FILES['avatar']
        else:
            user.avatar = None

        user.save()

        email = form.cleaned_data.get('email')
        raw_password = form.cleaned_data.get('password1')
        user = authenticate(email, password=raw_password)
        if user is not None:
            login(self.request, user)
            messages.success(self.request, 'Registration successful. You are now logged in.')
            return redirect(self.get_success_url())
        else:
            messages.error(self.request, 'Authentication failed. Please try again.')
            return redirect('register')

    def form_invalid(self, form):
        messages.error(self.request, 'Registration failed. Please correct the errors below.')
        return super().form_invalid(form)


class LoginView(FormView):
    form_class = CustomAuthenticationForm
    template_name = 'user/login.html'
    success_url = reverse_lazy('home')

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            messages.info(request, 'You are already logged in.')
            return redirect('home')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password')
        user = authenticate(username=username, password=password)
        if user is not None:
            login(self.request, user)
            messages.success(self.request, 'Login successful.')
            return redirect(self.get_success_url())
        else:
            messages.error(self.request, 'Invalid username or password. Please try again.')
            return self.form_invalid(form)


class LogoutView(View):
    def get(self, request, *args, **kwargs):
        logout(request)
        messages.success(request, 'You have successfully logged out.')
        return redirect('login')


class HomeView(LoginRequiredMixin, TemplateView):
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context['user_files'] = UserFiles.objects.filter(owner=user)
        context['shared_files'] = UserFiles.objects.filter(allowed_users=user)
        return context


class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = 'user/profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = self.request.user
        return context


class ProfileEditView(LoginRequiredMixin, UpdateView):
    model = CustomUserModel
    form_class = ProfileEditForm
    template_name = 'user/edit-user.html'
    success_url = reverse_lazy('profile')

    def get_object(self, queryset=None):
        return self.request.user

    def form_valid(self, form):
        messages.success(self.request, 'Profile updated successfully.')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Update failed. Please correct the errors below.')
        return super().form_invalid(form)


class UserDeleteView(LoginRequiredMixin, DeleteView):
    model = CustomUserModel
    success_url = reverse_lazy('login')
    template_name = 'user/user_confirm_delete.html'

    def get_object(self, queryset=None):
        return self.request.user

    def delete(self, request, *args, **kwargs):
        if self.request.user.avatar:
            self.request.user.avatar.delete()
        LogoutView.as_view()(self.request)
        messages.success(request, 'Your account has been deleted.')
        return super().delete(request, *args, **kwargs)


class UserFileListView(LoginRequiredMixin, TemplateView):
    template_name = 'user/userfile_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user_files'] = UserFiles.objects.filter(owner=self.request.user)
        return context


class UserFileCreateView(LoginRequiredMixin, View):
    def get(self, request):
        form = UserFileForm()
        return render(request, 'user/userfile_form.html', {'form': form})

    def post(self, request):
        form = UserFileForm(request.POST, request.FILES)
        if form.is_valid():
            user_file = form.save(commit=False)
            user_file.owner = request.user
            user_file.save()
            messages.success(request, 'File uploaded successfully.')
            return redirect('userfile_list')
        messages.error(request, 'File upload failed. Please correct the errors below.')
        return render(request, 'user/userfile_form.html', {'form': form})


class UserFileDetailView(LoginRequiredMixin, View):
    def get(self, request, pk):
        user_file = get_object_or_404(UserFiles, pk=pk)
        
        # Check permissions
        if user_file.owner != request.user and request.user not in user_file.allowed_users.all():
            messages.error(request, 'You do not have permission to view this file.')
            return redirect('userfile_list')
        
        # Determine file type based on file extension
        file_extension = user_file.file.name.split('.')[-1].lower()
        file_type = None
        
        if file_extension in ['jpg', 'jpeg', 'png', 'gif']:
            file_type = 'image'
        elif file_extension == 'pdf':
            file_type = 'pdf'
        elif file_extension in ['docx', 'xlsx', 'txt']:
            file_type = 'document'
        else:
            # Handle unsupported file types or unknown extensions
            return HttpResponseNotFound('File type not supported.')
        
        context = {
            'user_file': user_file,
            'file_type': file_type,
        }
        
        return render(request, 'user/userfile_detail.html', context)


class UserFileDeleteView(LoginRequiredMixin, DeleteView):
    model = UserFiles
    success_url = reverse_lazy('userfile_list')
    template_name = 'user/userfile_confirm_delete.html'

    def get_queryset(self):
        return self.model.objects.filter(owner=self.request.user)
    


class ShareFileView(View):
    def get(self, request, file_id):
        form = ShareFileForm(user=request.user)
        return render(request, 'user/share_file.html', {'form': form, 'file_id': file_id})

    def post(self, request, file_id):
        form = ShareFileForm(request.POST, user=request.user)
        if form.is_valid():
            recipient_user = form.cleaned_data['recipient']
            try:
                file_to_share = UserFiles.objects.get(pk=file_id, owner=request.user)
                file_to_share.allowed_users.add(recipient_user)
                messages.success(request, f'File shared with {recipient_user.username} successfully.')
            except UserFiles.DoesNotExist:
                messages.error(request, 'File not found or you do not have permission to share it.')
            return redirect('userfile_detail', pk=file_id)
        return render(request, 'user/share_file.html', {'form': form, 'file_id': file_id})
    


class AutocompleteUsersView(View):
    def get(self, request, *args, **kwargs):
        term = request.GET.get('term', None)
        if term:
            users = CustomUserModel.objects.filter(username__icontains=term)
            results = [{'label': user.username, 'value': user.username} for user in users]
            return JsonResponse(results, safe=False)
        return JsonResponse([], safe=False)
