from flask import Blueprint, render_template, redirect, url_for, flash
from app.forms import RegistrationForm, LoginForm
from app.models import User
from app import db, bcrypt
from flask_login import login_user, logout_user, login_required, current_user
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from flask import current_app

main = Blueprint('main', __name__)

@main.route('/')
def home():
    return redirect(url_for('main.login'))

@main.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        # Check if user already exists
        existing_user = User.query.filter(
            (User.email == form.email.data) | (User.username == form.username.data)
        ).first()
        if existing_user:
            flash('⚠️ Email or username already taken.', 'danger')
            return render_template('register.html', form=form)

        try:
            hashed_pw = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
            user = User(username=form.username.data, email=form.email.data, password=hashed_pw)
            db.session.add(user)
            db.session.commit()
            flash('✅ Account created! You can now log in.', 'success')
            return redirect(url_for('main.login'))
        except IntegrityError:
            db.session.rollback()
            flash('❌ Email already exists. Try another one.', 'danger')
        except SQLAlchemyError:
            db.session.rollback()
            flash('🚫 Database error. Please check your internet connection or try again later.', 'danger')
    return render_template('register.html', form=form)

@main.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        try:
            user = User.query.filter_by(email=form.email.data).first()
            if user and bcrypt.check_password_hash(user.password, form.password.data):
                login_user(user)
                return redirect(url_for('main.dashboard'))
            else:
                flash('Login failed. Check email and password.', 'danger')
        except SQLAlchemyError:
            flash('⚠️ Unable to connect. Please check your internet or database.', 'danger')
    return render_template('login.html', form=form)

@main.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')


@main.route('/logout')
@login_required
def logout():
    logout_user()
    flash("You’ve been logged out.", "success")
    return redirect(url_for('main.login'))

import os
from flask import request
from werkzeug.utils import secure_filename
from app.forms import LostItemForm
from app.models import LostItem


@main.route('/post-item', methods=['GET', 'POST'])
@login_required
def post_item():
    form = LostItemForm()
    if form.validate_on_submit():
        image_filename = None
        if form.image_file.data:
            image = form.image_file.data
            image_filename = secure_filename(image.filename)

            upload_folder = os.path.join(current_app.root_path, 'static', 'uploads')  # ✅ Moved here
            os.makedirs(upload_folder, exist_ok=True)
            image.save(os.path.join(upload_folder, image_filename))

        item = LostItem(
            title=form.title.data,
            description=form.description.data,
            location=form.location.data,
            contact_info=form.contact_info.data,
            image_file=image_filename,
            user_id=current_user.id
        )
        try:
            db.session.add(item)
            db.session.commit()
            flash('Item posted successfully!', 'success')
            return redirect(url_for('main.view_items'))
        except SQLAlchemyError as e:
            db.session.rollback()
            print(f"[DB ERROR] {e}")
            flash('🚫 Something went wrong while saving your item.', 'danger')

    return render_template('post_item.html', form=form)


@main.route('/items')
def view_items():
    items = LostItem.query.order_by(LostItem.date_posted.desc()).all()
    return render_template('items.html', items=items)

@main.route('/my-items')
@login_required
def my_items():
    items = LostItem.query.filter_by(user_id=current_user.id).order_by(LostItem.date_posted.desc()).all()
    return render_template('my_items.html', items=items)

@main.route('/delete-item/<int:item_id>', methods=['POST'])
@login_required
def delete_item(item_id):
    item = LostItem.query.get_or_404(item_id)
    if item.user_id != current_user.id:
        flash("⛔ You are not authorized to delete this item.", "danger")
        return redirect(url_for('main.my_items'))

    try:
        db.session.delete(item)
        db.session.commit()
        flash("✅ Item deleted successfully.", "success")
    except SQLAlchemyError:
        db.session.rollback()
        flash("⚠️ Error deleting item. Try again.", "danger")

    return redirect(url_for('main.my_items'))
