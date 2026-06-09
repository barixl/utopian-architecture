import os
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, abort, session
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
from jinja2 import TemplateNotFound
from functools import wraps
from urllib.parse import quote
from werkzeug.utils import secure_filename

# Load environment variables from .env
load_dotenv()

app = Flask(__name__)

# Basic configurations
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev_secret_key_utopia_interior_2026')

# SQLite Database setup inside the 'instance' folder
# Make sure the instance folder exists dynamically
os.makedirs(app.instance_path, exist_ok=True)

# Vercel serverless has a read-only filesystem except for '/tmp'.
# For local development, we default to the standard instance/contacts.db.
# If running in a Vercel-like read-only serverless environment, the DB can be overridden via environment variables.
db_default_path = os.path.join(app.instance_path, 'contacts.db')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', f'sqlite:///{db_default_path}')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Setup Upload Folders
UPLOAD_FOLDER_SLIDER = os.path.join(app.root_path, 'static', 'uploads', 'slider')
UPLOAD_FOLDER_CATALOG = os.path.join(app.root_path, 'static', 'uploads', 'catalog')
os.makedirs(UPLOAD_FOLDER_SLIDER, exist_ok=True)
os.makedirs(UPLOAD_FOLDER_CATALOG, exist_ok=True)
app.config['UPLOAD_FOLDER_SLIDER'] = UPLOAD_FOLDER_SLIDER
app.config['UPLOAD_FOLDER_CATALOG'] = UPLOAD_FOLDER_CATALOG
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Initialize the SQLAlchemy instance
db = SQLAlchemy(app)

# Database Model for Contact Form Submissions
class Contact(db.Model):
    __tablename__ = 'contacts'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20))
    subject = db.Column(db.String(150))
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Contact {self.name} - {self.email}>"

class HeroSlider(db.Model):
    __tablename__ = 'hero_sliders'
    
    id = db.Column(db.Integer, primary_key=True)
    image_url = db.Column(db.String(255), nullable=False)
    heading = db.Column(db.String(255), nullable=False)
    sub_text = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<HeroSlider {self.id}>"

class CatalogProduct(db.Model):
    __tablename__ = 'catalog_products'
    
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(50), nullable=False) # e.g. furniture, home-decor
    name = db.Column(db.String(100), nullable=False)
    mrp = db.Column(db.String(50), nullable=False)
    image_url = db.Column(db.String(255), nullable=False)
    in_stock = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<CatalogProduct {self.name}>"

# Create the SQLite tables on application startup
with app.app_context():
    db.create_all()
    
    # Seed default sliders if the table is empty
    if HeroSlider.query.count() == 0:
        default_sliders = [
            {
                "image_url": "/static/img/hero/banner-1.jpg",
                "heading": 'MAKE YOUR <span class="secondary">HOME</span><br />FEEL LIKE <span class="secondary">HOME</span>',
                "sub_text": 'Your space should tell your story. We carefully blend textures, colors, and lighting to create interiors that bring comfort, warmth, and character — a perfect backdrop for moments and memories that matter.'
            },
            {
                "image_url": "https://images.pexels.com/photos/1571460/pexels-photo-1571460.jpeg?auto=compress&cs=tinysrgb&w=1920&q=80",
                "heading": 'LUXURY <span class="secondary">DESIGN</span><br />FOR MODERN <span class="secondary">LIVING</span>',
                "sub_text": 'Experience unparalleled elegance and sophistication. We specialize in crafting modern, bespoke interiors that elevate your lifestyle with premium furnishings and exquisite finishes.'
            },
            {
                "image_url": "https://images.pexels.com/photos/2988860/pexels-photo-2988860.jpeg?auto=compress&cs=tinysrgb&w=1920&q=80",
                "heading": 'CUSTOM <span class="secondary">FURNITURE</span><br />& OUTDOOR <span class="secondary">WORKS</span>',
                "sub_text": 'Transform your spaces with bespoke solutions. From expertly crafted custom furniture to stunning pergolas and outdoor retreats, we bring visionary designs to life.'
            }
        ]
        for slide_data in default_sliders:
            new_slide = HeroSlider(**slide_data)
            db.session.add(new_slide)
            
    # Seed default catalog products if the table is empty
    if CatalogProduct.query.count() == 0:
        default_products = [
            {"category": "furniture", "name": "Modern Sofa", "mrp": "$1,250", "image_url": "https://images.unsplash.com/photo-1555041469-a586c61ea9bc?auto=format&fit=crop&w=800&q=80"},
            {"category": "furniture", "name": "Luxury Dining Table", "mrp": "$2,400", "image_url": "https://images.unsplash.com/photo-1577140917170-285929fb55b7?auto=format&fit=crop&w=800&q=80"},
            {"category": "outdoor", "name": "Outdoor Pergola", "mrp": "$3,800", "image_url": "https://images.unsplash.com/photo-1600585154340-be6161a56a0c?auto=format&fit=crop&w=800&q=80"},
            {"category": "home-decor", "name": "Minimal Table Lamp", "mrp": "$180", "image_url": "https://images.unsplash.com/photo-1507473885765-e6ed057f782c?auto=format&fit=crop&w=800&q=80"},
            {"category": "home-decor", "name": "Luxury Wall Mirror", "mrp": "$420", "image_url": "https://images.unsplash.com/photo-1618220179428-22790b461013?auto=format&fit=crop&w=800&q=80"},
            {"category": "accessories", "name": "Decorative Vase Set", "mrp": "$140", "image_url": "https://images.unsplash.com/photo-1612196808214-b8e1d6145a8c?auto=format&fit=crop&w=800&q=80"}
        ]
        for prod_data in default_products:
            db.session.add(CatalogProduct(**prod_data))
            
    db.session.commit()

# --- USER ROUTES ---

@app.route('/')
def home():
    """Renders the Home Page."""
    sliders = HeroSlider.query.order_by(HeroSlider.created_at.asc()).all()
    catalog_products = CatalogProduct.query.order_by(CatalogProduct.created_at.desc()).all()
    
    # Get unique categories for frontend filters
    categories = db.session.query(CatalogProduct.category).distinct().all()
    unique_categories = [cat[0] for cat in categories]
    
    return render_template('pages/index.html', sliders=sliders, catalog_products=catalog_products, unique_categories=unique_categories)

@app.route('/about')
def about():
    """Renders the About Page."""
    return render_template('pages/about.html')

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    """
    Handles Contact Page rendering (GET) and Form Submissions (POST).
    Stores form inputs inside contacts.db.
    """
    if request.method == 'POST':
        # Retrieve form data
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        subject = request.form.get('subject')
        message = request.form.get('message')
        
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.headers.get('Accept') == 'application/json' or request.content_type == 'application/json'
        
        # Simple validations
        if not name or not email or not message:
            if is_ajax:
                return {"status": "error", "message": "Please fill out all required fields."}, 400
            flash("Please fill out all required fields.", "danger")
            return redirect(url_for('contact'))
            
        try:
            # Create a new Contact record
            new_contact = Contact(
                name=name,
                email=email,
                phone=phone,
                subject=subject,
                message=message
            )
            db.session.add(new_contact)
            db.session.commit()
            
            if is_ajax:
                return {"status": "success", "message": "Your message has been sent successfully! We will get back to you soon."}, 200
                
            flash("Your message has been sent successfully! We will get back to you soon.", "success")
        except Exception as e:
            db.session.rollback()
            app.logger.error(f"Error saving contact form: {e}")
            if is_ajax:
                return {"status": "error", "message": "An error occurred while sending your message. Please try again later."}, 500
                
            flash("An error occurred while sending your message. Please try again later.", "danger")
            
        return redirect(url_for('contact'))
        
    return render_template('pages/contact.html')

@app.route('/services')
def services():
    """Renders the Services Page."""
    return render_template('pages/services.html')

@app.route('/gallery')
def gallery():
    """Renders the Gallery Page."""
    return render_template('pages/gallery.html')

@app.route('/shop')
def shop():
    """Renders the Shop Page."""
    return render_template('pages/shop.html')

# --- DYNAMIC PAGE ROUTING FALLBACK ---

@app.route('/page/<slug>')
def dynamic_page(slug):
    """
    Dynamic page router. 
    Attempts to match templates under templates/pages/{slug}.html.
    """
    try:
        return render_template(f"pages/{slug}.html")
    except TemplateNotFound:
        abort(404)

# --- ADMIN PANEL ROUTES ---

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('admin_logged_in'):
            next_param = quote(request.path, safe='')
            return redirect(f"{url_for('admin_login')}?next={next_param}")
        return f(*args, **kwargs)
    return decorated_function

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        admin_user = os.getenv('ADMIN_USERNAME', 'admin')
        admin_pass = os.getenv('ADMIN_PASSWORD', 'admin123')
        
        if username == admin_user and password == admin_pass:
            session['admin_logged_in'] = True
            flash("Logged in successfully.", "success")
            next_url = request.args.get('next')
            return redirect(next_url or url_for('admin_dashboard'))
        else:
            flash("Invalid credentials.", "danger")
            
    return render_template('admin/login.html')

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    flash("Logged out successfully.", "success")
    return redirect(url_for('admin_login', next='/admin'))

@app.route('/admin')
@login_required
def admin_dashboard():
    """
    Displays the admin dashboard listing all contact submissions.
    """
    try:
        from datetime import date, timedelta
        # Fetch all submissions ordered by newest first
        submissions = Contact.query.order_by(Contact.created_at.desc()).all()
        today = date.today()
        yesterday = datetime.utcnow() - timedelta(days=1)
        return render_template(
            'admin/dashboard.html', 
            submissions=submissions, 
            datetime_today=today, 
            yesterday=yesterday
        )
    except Exception as e:
        app.logger.error(f"Error fetching admin submissions: {e}")
        return "An error occurred while loading the admin dashboard. Please verify database setup.", 500

@app.route('/admin/edit/<int:id>', methods=['POST'])
@login_required
def admin_edit_submission(id):
    """
    Endpoint for editing a contact submission (via POST from dashboard modal).
    """
    submission = Contact.query.get_or_404(id)
    submission.name = request.form.get('name')
    submission.email = request.form.get('email')
    submission.phone = request.form.get('phone')
    submission.subject = request.form.get('subject')
    submission.message = request.form.get('message')
    try:
        db.session.commit()
        flash("Submission updated successfully.", "success")
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Error updating submission: {e}")
        flash("Failed to update the submission.", "danger")
        
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/delete/<int:id>', methods=['POST'])
@login_required
def admin_delete_submission(id):
    """
    Endpoint for deleting a contact submission.
    """
    submission = Contact.query.get_or_404(id)
    try:
        db.session.delete(submission)
        db.session.commit()
        flash("Submission deleted successfully.", "success")
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Error deleting submission: {e}")
        flash("Failed to delete the submission.", "danger")
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/slider')
@login_required
def admin_slider():
    """Displays the admin dashboard listing all hero slides."""
    try:
        sliders = HeroSlider.query.order_by(HeroSlider.created_at.asc()).all()
        return render_template('admin/slider.html', sliders=sliders)
    except Exception as e:
        app.logger.error(f"Error fetching admin sliders: {e}")
        return "An error occurred while loading the sliders. Please verify database setup.", 500

@app.route('/admin/slider/add', methods=['POST'])
@login_required
def admin_add_slider():
    """Endpoint for adding a new hero slide."""
    heading = request.form.get('heading')
    sub_text = request.form.get('sub_text')
    
    if not heading or not sub_text:
        flash("Please fill out heading and sub text.", "danger")
        return redirect(url_for('admin_slider'))
        
    image_file = request.files.get('image')
    if not image_file or image_file.filename == '':
        flash("Please upload an image.", "danger")
        return redirect(url_for('admin_slider'))
        
    if image_file and allowed_file(image_file.filename):
        filename = secure_filename(f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{image_file.filename}")
        image_path = os.path.join(app.config['UPLOAD_FOLDER_SLIDER'], filename)
        image_file.save(image_path)
        image_url = url_for('static', filename=f"uploads/slider/{filename}")
    else:
        flash("Invalid file format for image.", "danger")
        return redirect(url_for('admin_slider'))
        
    try:
        new_slide = HeroSlider(
            image_url=image_url,
            heading=heading,
            sub_text=sub_text
        )
        db.session.add(new_slide)
        db.session.commit()
        flash("Slide added successfully.", "success")
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Error adding slide: {e}")
        flash("Failed to add the slide.", "danger")
        
    return redirect(url_for('admin_slider'))

@app.route('/admin/slider/edit/<int:id>', methods=['POST'])
@login_required
def admin_edit_slider(id):
    """Endpoint for editing a hero slide."""
    slide = HeroSlider.query.get_or_404(id)
    slide.heading = request.form.get('heading')
    slide.sub_text = request.form.get('sub_text')
    
    image_file = request.files.get('image')
    if image_file and image_file.filename != '':
        if allowed_file(image_file.filename):
            filename = secure_filename(f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{image_file.filename}")
            image_path = os.path.join(app.config['UPLOAD_FOLDER_SLIDER'], filename)
            image_file.save(image_path)
            slide.image_url = url_for('static', filename=f"uploads/slider/{filename}")
        else:
            flash("Invalid file format for image.", "danger")
            return redirect(url_for('admin_slider'))
            
    try:
        db.session.commit()
        flash("Slide updated successfully.", "success")
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Error updating slide: {e}")
        flash("Failed to update the slide.", "danger")
        
    return redirect(url_for('admin_slider'))

@app.route('/admin/slider/delete/<int:id>', methods=['POST'])
@login_required
def admin_delete_slider(id):
    """Endpoint for deleting a hero slide."""
    slide = HeroSlider.query.get_or_404(id)
    try:
        db.session.delete(slide)
        db.session.commit()
        flash("Slide deleted successfully.", "success")
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Error deleting slide: {e}")
        flash("Failed to delete the slide.", "danger")
    return redirect(url_for('admin_slider'))

@app.route('/admin/catalog')
@login_required
def admin_catalog():
    """Displays the catalog dashboard."""
    try:
        products = CatalogProduct.query.order_by(CatalogProduct.created_at.desc()).all()
        return render_template('admin/catalog.html', products=products)
    except Exception as e:
        app.logger.error(f"Error fetching admin catalog: {e}")
        return "An error occurred while loading the catalog. Please verify database setup.", 500

@app.route('/admin/catalog/add', methods=['POST'])
@login_required
def admin_add_catalog():
    """Endpoint for adding a new catalog product."""
    category = request.form.get('category')
    if category == 'other':
        custom_category = request.form.get('custom_category')
        if custom_category:
            category = custom_category.strip().lower().replace(' ', '-')
            
    name = request.form.get('name')
    mrp = request.form.get('mrp')
    in_stock = request.form.get('in_stock') == 'on'
    
    if not category or not name or not mrp:
        flash("Please fill out all product details.", "danger")
        return redirect(url_for('admin_catalog'))
        
    image_file = request.files.get('image')
    if not image_file or image_file.filename == '':
        flash("Please upload a product image.", "danger")
        return redirect(url_for('admin_catalog'))
        
    if image_file and allowed_file(image_file.filename):
        filename = secure_filename(f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{image_file.filename}")
        image_path = os.path.join(app.config['UPLOAD_FOLDER_CATALOG'], filename)
        image_file.save(image_path)
        image_url = url_for('static', filename=f"uploads/catalog/{filename}")
    else:
        flash("Invalid file format for image.", "danger")
        return redirect(url_for('admin_catalog'))
        
    try:
        new_prod = CatalogProduct(
            category=category,
            name=name,
            mrp=mrp,
            image_url=image_url,
            in_stock=in_stock
        )
        db.session.add(new_prod)
        db.session.commit()
        flash("Product added successfully.", "success")
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Error adding product: {e}")
        flash("Failed to add the product.", "danger")
        
    return redirect(url_for('admin_catalog'))

@app.route('/admin/catalog/edit/<int:id>', methods=['POST'])
@login_required
def admin_edit_catalog(id):
    """Endpoint for editing a catalog product."""
    prod = CatalogProduct.query.get_or_404(id)
    category = request.form.get('category')
    if category == 'other':
        custom_category = request.form.get('custom_category')
        if custom_category:
            category = custom_category.strip().lower().replace(' ', '-')
    
    if category:
        prod.category = category
        
    prod.name = request.form.get('name')
    prod.mrp = request.form.get('mrp')
    prod.in_stock = request.form.get('in_stock') == 'on'
    
    image_file = request.files.get('image')
    if image_file and image_file.filename != '':
        if allowed_file(image_file.filename):
            filename = secure_filename(f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{image_file.filename}")
            image_path = os.path.join(app.config['UPLOAD_FOLDER_CATALOG'], filename)
            image_file.save(image_path)
            prod.image_url = url_for('static', filename=f"uploads/catalog/{filename}")
        else:
            flash("Invalid file format for image.", "danger")
            return redirect(url_for('admin_catalog'))
            
    try:
        db.session.commit()
        flash("Product updated successfully.", "success")
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Error updating product: {e}")
        flash("Failed to update the product.", "danger")
        
    return redirect(url_for('admin_catalog'))

@app.route('/admin/catalog/delete/<int:id>', methods=['POST'])
@login_required
def admin_delete_catalog(id):
    """Endpoint for deleting a catalog product."""
    prod = CatalogProduct.query.get_or_404(id)
    try:
        db.session.delete(prod)
        db.session.commit()
        flash("Product deleted successfully.", "success")
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Error deleting product: {e}")
        flash("Failed to delete the product.", "danger")
    return redirect(url_for('admin_catalog'))

# --- CUSTOM 404 ERROR HANDLER ---

@app.errorhandler(404)
def page_not_found(e):
    """Handles 404 page rendering."""
    return render_template('404.html'), 404

# --- RUN LOCALLY ---
if __name__ == '__main__':
    # Local runtime port config
    app.run(host='0.0.0.0', port=5003, debug=True)
