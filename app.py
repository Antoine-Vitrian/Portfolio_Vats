import os
import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix

# Set up logging
logging.basicConfig(level=logging.DEBUG)

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)
login_manager = LoginManager()

# create the app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key-change-in-production")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# configure the database
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///portfolio.db")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}
app.config["UPLOAD_FOLDER"] = "static/uploads"
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16MB max file size

# initialize extensions
db.init_app(app)
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access this page.'

# Add custom Jinja2 filters
@app.template_filter('nl2br')
def nl2br_filter(s):
    """Convert newlines to HTML line breaks"""
    if s is None:
        return s
    return s.replace('\n', '<br>\n')

@app.template_filter('truncate_words')
def truncate_words_filter(s, length=50, end='...'):
    """Truncate text by word count"""
    if s is None:
        return s
    words = s.split()
    if len(words) <= length:
        return s
    return ' '.join(words[:length]) + end

@login_manager.user_loader
def load_user(user_id):
    from models import User
    return User.query.get(int(user_id))

with app.app_context():
    # Import models to ensure tables are created
    import models
    import routes
    
    db.create_all()
    
    # Create admin user if it doesn't exist
    admin_user = models.User.query.filter_by(email='admin@portfolio.com').first()
    if not admin_user:
        from werkzeug.security import generate_password_hash
        admin = models.User(
            username='admin',
            email='admin@portfolio.com',
            password_hash=generate_password_hash('admin123'),
            is_admin=True
        )
        db.session.add(admin)
        
        # Create default about content
        default_about = """<h3>Welcome to My Digital Portfolio</h3>
<p>I'm a passionate software developer with expertise in creating innovative web solutions. With several years of experience in full-stack development, I specialize in building scalable applications using modern technologies.</p>

<h4>Technical Skills</h4>
<ul>
<li><strong>Frontend:</strong> HTML5, CSS3, JavaScript, React, Vue.js, Bootstrap</li>
<li><strong>Backend:</strong> Python (Flask, Django), Node.js, Express</li>
<li><strong>Databases:</strong> PostgreSQL, MongoDB, SQLite</li>
<li><strong>Tools & Technologies:</strong> Git, Docker, AWS, Linux</li>
</ul>

<h4>What I Do</h4>
<p>I enjoy tackling complex problems and turning ideas into reality through code. My approach combines technical excellence with user-centered design to create applications that are both powerful and intuitive.</p>

<h4>Let's Connect</h4>
<p>I'm always interested in discussing new opportunities, collaborating on exciting projects, or simply connecting with fellow developers. Feel free to reach out!</p>"""

        about_content = models.About.query.first()
        if not about_content:
            about = models.About(content=default_about)
            db.session.add(about)
        
        # Create sample projects for demonstration
        sample_projects = [
            {
                'title': 'E-commerce Platform',
                'description': 'A full-stack e-commerce solution with user authentication, product management, shopping cart, and payment integration.',
                'content': '''<h3>Project Overview</h3>
<p>This comprehensive e-commerce platform was built using modern web technologies to provide a seamless shopping experience for users while offering powerful management tools for administrators.</p>

<h4>Key Features</h4>
<ul>
<li>User registration and authentication system</li>
<li>Product catalog with search and filtering</li>
<li>Shopping cart and wishlist functionality</li>
<li>Secure payment processing with Stripe</li>
<li>Order tracking and history</li>
<li>Admin dashboard for product and order management</li>
<li>Responsive design for all devices</li>
</ul>

<h4>Technical Implementation</h4>
<p>Built with React.js frontend, Node.js/Express backend, and PostgreSQL database. Implemented JWT authentication, integrated payment APIs, and deployed on AWS with CI/CD pipeline.</p>''',
                'category': 'web',
                'tags': 'React, Node.js, PostgreSQL, Stripe, AWS',
                'is_published': True,
                'is_featured': True
            },
            {
                'title': 'Task Management Mobile App',
                'description': 'A cross-platform mobile application for task management with real-time sync, team collaboration, and productivity analytics.',
                'content': '''<h3>About This Project</h3>
<p>A comprehensive task management solution designed to help teams and individuals organize their work efficiently with real-time collaboration features.</p>

<h4>Features</h4>
<ul>
<li>Create and organize tasks with priorities and due dates</li>
<li>Team collaboration with shared projects</li>
<li>Real-time synchronization across devices</li>
<li>Progress tracking and analytics</li>
<li>Offline functionality</li>
<li>Push notifications for deadlines</li>
</ul>

<h4>Development</h4>
<p>Developed using React Native for cross-platform compatibility, with Firebase for real-time database and authentication.</p>''',
                'category': 'mobile',
                'tags': 'React Native, Firebase, JavaScript, Mobile',
                'is_published': True,
                'is_featured': False
            },
            {
                'title': 'Data Analytics Dashboard',
                'description': 'Interactive dashboard for visualizing business metrics and KPIs with real-time data processing and custom reporting.',
                'content': '''<h3>Dashboard Overview</h3>
<p>An advanced analytics platform that transforms raw business data into actionable insights through interactive visualizations and comprehensive reporting.</p>

<h4>Capabilities</h4>
<ul>
<li>Real-time data ingestion and processing</li>
<li>Interactive charts and graphs</li>
<li>Custom KPI tracking</li>
<li>Automated report generation</li>
<li>User role management</li>
<li>Export functionality</li>
</ul>

<h4>Technology Stack</h4>
<p>Built with Python (Flask), D3.js for visualizations, and PostgreSQL for data storage. Implements data pipeline with ETL processes for various data sources.</p>''',
                'category': 'data',
                'tags': 'Python, Flask, D3.js, PostgreSQL, Analytics',
                'is_published': True,
                'is_featured': True
            }
        ]
        
        existing_projects = models.Project.query.count()
        if existing_projects == 0:
            for project_data in sample_projects:
                project = models.Project(**project_data)
                db.session.add(project)
        
        db.session.commit()
        print("Admin user and sample content created: admin@portfolio.com / admin123")
