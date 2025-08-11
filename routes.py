import os
from flask import render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash
from app import app, db
from models import User, Project, Comment, Like, About, Notification
from forms import LoginForm, RegisterForm, ProjectForm, CommentForm, AboutForm

# Helper function for file uploads
def save_uploaded_file(file):
    if file and file.filename:
        filename = secure_filename(file.filename)
        # Add timestamp to prevent filename conflicts
        import time
        timestamp = str(int(time.time()))
        name, ext = os.path.splitext(filename)
        filename = f"{name}_{timestamp}{ext}"
        
        upload_path = os.path.join(app.config['UPLOAD_FOLDER'])
        os.makedirs(upload_path, exist_ok=True)
        
        file_path = os.path.join(upload_path, filename)
        file.save(file_path)
        return f"uploads/{filename}"
    return None

# Public routes
@app.route('/')
def index():
    featured_projects = Project.query.filter_by(is_published=True, is_featured=True).order_by(Project.created_at.desc()).limit(3).all()
    recent_projects = Project.query.filter_by(is_published=True).order_by(Project.created_at.desc()).limit(6).all()
    return render_template('index.html', featured_projects=featured_projects, recent_projects=recent_projects)

@app.route('/about')
def about():
    about_content = About.get_content()
    return render_template('about.html', about_content=about_content)

@app.route('/projects')
def projects():
    category = request.args.get('category')
    search = request.args.get('search')
    
    query = Project.query.filter_by(is_published=True)
    
    if category:
        query = query.filter_by(category=category)
    
    if search:
        query = query.filter(Project.title.contains(search) | Project.description.contains(search))
    
    projects = query.order_by(Project.created_at.desc()).all()
    categories = ['web', 'mobile', 'desktop', 'data', 'ai', 'other']
    
    return render_template('projects.html', projects=projects, categories=categories, 
                         current_category=category, search_term=search)

@app.route('/project/<int:id>')
def project_detail(id):
    project = Project.query.get_or_404(id)
    if not project.is_published and (not current_user.is_authenticated or not current_user.is_admin):
        flash('Project not found.', 'error')
        return redirect(url_for('index'))
    
    comments = Comment.query.filter_by(project_id=id, is_approved=True).order_by(Comment.created_at.desc()).all()
    comment_form = CommentForm()
    
    if comment_form.validate_on_submit() and current_user.is_authenticated:
        comment = Comment(
            content=comment_form.content.data,
            user_id=current_user.id,
            project_id=project.id
        )
        db.session.add(comment)
        
        # Create notification for admin
        notification = Notification(
            title='New Comment',
            message=f'{current_user.username} commented on "{project.title}"',
            user_id=current_user.id,
            project_id=project.id,
            comment_id=comment.id
        )
        db.session.add(notification)
        
        db.session.commit()
        flash('Comment added successfully!', 'success')
        return redirect(url_for('project_detail', id=id))
    
    return render_template('project_detail.html', project=project, comments=comments, comment_form=comment_form)

@app.route('/like_project/<int:id>', methods=['POST'])
@login_required
def like_project(id):
    project = Project.query.get_or_404(id)
    existing_like = Like.query.filter_by(user_id=current_user.id, project_id=id).first()
    
    if existing_like:
        db.session.delete(existing_like)
        liked = False
    else:
        like = Like(user_id=current_user.id, project_id=id)
        db.session.add(like)
        liked = True
    
    db.session.commit()
    return jsonify({'liked': liked, 'like_count': project.like_count})

# Authentication routes
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            return redirect(url_for('index'))
        flash('Invalid email or password', 'error')
    
    return render_template('auth/login.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = RegisterForm()
    if form.validate_on_submit():
        # Check if user already exists
        if User.query.filter_by(email=form.email.data).first():
            flash('Email already registered', 'error')
            return render_template('auth/register.html', form=form)
        
        if User.query.filter_by(username=form.username.data).first():
            flash('Username already taken', 'error')
            return render_template('auth/register.html', form=form)
        
        user = User(
            username=form.username.data,
            email=form.email.data,
            password_hash=generate_password_hash(form.password.data)
        )
        db.session.add(user)
        db.session.commit()
        
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))
    
    return render_template('auth/register.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

@app.route('/forgot_password')
def forgot_password():
    return render_template('auth/forgot_password.html')

# Admin routes
@app.route('/admin')
@login_required
def admin_dashboard():
    if not current_user.is_admin:
        flash('Access denied.', 'error')
        return redirect(url_for('index'))
    
    total_projects = Project.query.count()
    published_projects = Project.query.filter_by(is_published=True).count()
    total_comments = Comment.query.count()
    total_likes = Like.query.count()
    unread_notifications = Notification.query.filter_by(is_read=False).count()
    
    recent_projects = Project.query.order_by(Project.created_at.desc()).limit(5).all()
    recent_comments = Comment.query.order_by(Comment.created_at.desc()).limit(5).all()
    recent_notifications = Notification.query.order_by(Notification.created_at.desc()).limit(5).all()
    
    return render_template('admin/dashboard.html', 
                         total_projects=total_projects,
                         published_projects=published_projects,
                         total_comments=total_comments,
                         total_likes=total_likes,
                         unread_notifications=unread_notifications,
                         recent_projects=recent_projects,
                         recent_comments=recent_comments,
                         recent_notifications=recent_notifications)

@app.route('/admin/projects')
@login_required
def admin_projects():
    if not current_user.is_admin:
        flash('Access denied.', 'error')
        return redirect(url_for('index'))
    
    projects = Project.query.order_by(Project.created_at.desc()).all()
    return render_template('admin/projects.html', projects=projects)

@app.route('/admin/project/new', methods=['GET', 'POST'])
@login_required
def admin_new_project():
    if not current_user.is_admin:
        flash('Access denied.', 'error')
        return redirect(url_for('index'))
    
    form = ProjectForm()
    if form.validate_on_submit():
        image_url = None
        if form.image.data:
            image_url = save_uploaded_file(form.image.data)
        
        project = Project(
            title=form.title.data,
            description=form.description.data,
            content=form.content.data,
            category=form.category.data,
            tags=form.tags.data,
            image_url=image_url,
            demo_url=form.demo_url.data,
            github_url=form.github_url.data,
            is_published=form.is_published.data,
            is_featured=form.is_featured.data
        )
        db.session.add(project)
        db.session.commit()
        
        flash('Project created successfully!', 'success')
        return redirect(url_for('admin_projects'))
    
    return render_template('admin/project_form.html', form=form, title='New Project')

@app.route('/admin/project/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def admin_edit_project(id):
    if not current_user.is_admin:
        flash('Access denied.', 'error')
        return redirect(url_for('index'))
    
    project = Project.query.get_or_404(id)
    form = ProjectForm(obj=project)
    
    if form.validate_on_submit():
        form.populate_obj(project)
        
        if form.image.data:
            image_url = save_uploaded_file(form.image.data)
            if image_url:
                project.image_url = image_url
        
        db.session.commit()
        flash('Project updated successfully!', 'success')
        return redirect(url_for('admin_projects'))
    
    return render_template('admin/project_form.html', form=form, project=project, title='Edit Project')

@app.route('/admin/project/<int:id>/delete', methods=['POST'])
@login_required
def admin_delete_project(id):
    if not current_user.is_admin:
        flash('Access denied.', 'error')
        return redirect(url_for('index'))
    
    project = Project.query.get_or_404(id)
    db.session.delete(project)
    db.session.commit()
    
    flash('Project deleted successfully!', 'success')
    return redirect(url_for('admin_projects'))

@app.route('/admin/about', methods=['GET', 'POST'])
@login_required
def admin_about():
    if not current_user.is_admin:
        flash('Access denied.', 'error')
        return redirect(url_for('index'))
    
    form = AboutForm()
    if form.validate_on_submit():
        About.update_content(form.content.data)
        flash('About section updated successfully!', 'success')
        return redirect(url_for('admin_about'))
    
    form.content.data = About.get_content()
    return render_template('admin/about_form.html', form=form)

# LinkedIn sharing route
@app.route('/share_linkedin/<int:id>')
def share_linkedin(id):
    project = Project.query.get_or_404(id)
    if not project.is_published:
        flash('Project not found.', 'error')
        return redirect(url_for('index'))
    
    # Generate LinkedIn sharing URL
    project_url = url_for('project_detail', id=id, _external=True)
    linkedin_url = f"https://www.linkedin.com/sharing/share-offsite/?url={project_url}"
    
    return redirect(linkedin_url)

# Notifications management
@app.route('/admin/notifications')
@login_required
def admin_notifications():
    if not current_user.is_admin:
        flash('Access denied.', 'error')
        return redirect(url_for('index'))
    
    notifications = Notification.query.order_by(Notification.created_at.desc()).all()
    
    # Mark all as read
    Notification.query.filter_by(is_read=False).update({'is_read': True})
    db.session.commit()
    
    return render_template('admin/notifications.html', notifications=notifications)

@app.route('/admin/notification/<int:id>/delete', methods=['POST'])
@login_required
def admin_delete_notification(id):
    if not current_user.is_admin:
        flash('Access denied.', 'error')
        return redirect(url_for('index'))
    
    notification = Notification.query.get_or_404(id)
    db.session.delete(notification)
    db.session.commit()
    
    flash('Notification deleted successfully!', 'success')
    return redirect(url_for('admin_notifications'))
