# Digital Portfolio System

## Overview

This is a Flask-based digital portfolio web application that allows a portfolio owner to showcase their projects and achievements. The system provides an administrative interface for content management, public project viewing, and user interaction features including comments and likes. Visitors can register accounts to engage with the content, while the portfolio owner has full administrative control over all content and user management.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Backend Framework
- **Flask Web Framework**: Chosen for its simplicity and flexibility in building web applications
- **SQLAlchemy ORM**: Provides database abstraction and relationship management
- **Flask-Login**: Handles user session management and authentication
- **WTForms**: Manages form validation and rendering with CSRF protection

### Database Design
- **SQLite Default**: Uses SQLite for development with PostgreSQL support via DATABASE_URL environment variable
- **User Model**: Stores user credentials, admin status, and relationships to comments/likes
- **Project Model**: Contains project details, metadata, publication status, and featured flags
- **Comment System**: Enables user engagement with projects
- **Like System**: Tracks user interactions and project popularity
- **About Model**: Manages portfolio owner's biographical content

### Authentication & Authorization
- **Role-based Access**: Distinguishes between regular users and administrators
- **Session Management**: Secure login/logout with remember me functionality
- **Password Security**: Uses Werkzeug's password hashing utilities
- **Protected Routes**: Admin functions require authentication and admin privileges

### File Upload System
- **Secure File Handling**: Uses werkzeug's secure_filename for safe uploads
- **Image Storage**: Stores project images in static/uploads directory
- **File Size Limits**: 16MB maximum file size restriction
- **Timestamp Prevention**: Adds timestamps to prevent filename conflicts

### Frontend Architecture
- **Bootstrap 5**: Responsive UI framework for consistent design
- **Jinja2 Templates**: Server-side rendering with template inheritance
- **Font Awesome**: Icon library for enhanced visual elements
- **Custom CSS**: Additional styling for portfolio-specific design elements
- **Vanilla JavaScript**: Client-side functionality for tooltips, alerts, and form enhancements

### Content Management
- **Admin Dashboard**: Statistics overview and project management interface
- **CRUD Operations**: Full create, read, update, delete capabilities for projects
- **Draft System**: Projects can be saved as drafts before publication
- **Featured Projects**: Special designation for highlighting important work
- **Category Organization**: Projects organized by development type (web, mobile, data science, etc.)
- **Tag System**: Comma-separated tags for flexible project categorization

### Public Interface
- **Portfolio Display**: Clean presentation of projects with filtering and search
- **Project Details**: Dedicated pages for each project with full content
- **User Interaction**: Comment system and like functionality for engagement
- **Responsive Design**: Mobile-friendly interface across all pages

## External Dependencies

### Frontend Libraries
- **Bootstrap 5.3.0**: UI framework loaded via CDN for responsive design
- **Font Awesome 6.4.0**: Icon library for enhanced visual elements

### Python Packages
- **Flask**: Core web framework
- **Flask-SQLAlchemy**: Database ORM integration
- **Flask-Login**: User session management
- **Flask-WTF**: Form handling and CSRF protection
- **WTForms**: Form validation and rendering
- **Werkzeug**: WSGI utilities and security functions

### Database Options
- **SQLite**: Default database for development and simple deployments
- **PostgreSQL**: Production database option via DATABASE_URL environment variable

### Development Tools
- **ProxyFix**: WSGI middleware for deployment behind reverse proxies
- **Python Logging**: Built-in logging for debugging and monitoring

### Environment Configuration
- **SESSION_SECRET**: Configurable secret key for session security
- **DATABASE_URL**: Optional environment variable for database configuration
- **Upload Directory**: Configurable file storage location