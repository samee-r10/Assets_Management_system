import io
import csv
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app, Response
from flask_login import login_required, current_user
from app import db
from app.models import Inventory, Log, User
from app.forms import InventoryForm
from datetime import datetime
from flask import render_template, redirect, url_for, request, flash
from app.forms import ResetPasswordForm  # Create this form as needed
from werkzeug.security import generate_password_hash
from flask import Flask, render_template, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask import current_app, flash, redirect, render_template, request, url_for
from collections import Counter
import logging
logging.basicConfig(level=logging.DEBUG)


#from forms import ResetPasswordForm  # Update this import based on your project structure
#from models import User  # Update this import based on your project structure


# Define the main Blueprint
main = Blueprint('main', __name__)

# Dropdown options
ASSET_TYPES = ['Laptop', 'Monitors']
STATUS = ['Available', 'Sold', 'In Use', 'Retired', 'Dead']
BRANDS = ['Lenovo', 'Dell', 'HP', 'Apple', 'ViewSonic', 'Samsung', 'Microsoft']
OPERATING_SYSTEMS = ['Windows', 'Mac', 'Linux']
DEPARTMENTS = ['IT', 'Procurement', 'Legal', 'Project', 'O&M', 'Finance', 'BD', 'HR', 'Wind', 'Risk', 'Engineering', 'Corporate']
OFFICES = ['Mumbai', 'Pune', 'Delhi', 'Hyderabad', 'Chennai', 'Singapore', 'Thailand', 'Malaysia', 'Philippines', 'Vietnam', 'Cambodia', 'Indonesia', 'India']
COUNTRIES = ['Singapore', 'Thailand', 'Malaysia', 'Philippines', 'Vietnam', 'Cambodia', 'Indonesia', 'India']
VENDOR_LOCATIONS = ['Mumbai', 'Pune', 'Delhi', 'Hyderabad', 'Chennai', 'Singapore', 'Thailand', 'Malaysia', 'Philippines', 'Vietnam', 'Cambodia', 'Indonesia', 'India']

@main.route('/', methods=['GET', 'POST'])
@login_required
def home():

    # Get all items from the inventory
    items = Inventory.query.all()

    # Calculate brand counts
    brand_counts = Counter(item.brand for item in items)

    # Sort brand counts in descending order
    sorted_brand_counts = dict(sorted(brand_counts.items(), key=lambda x: x[1], reverse=True))

    # Calculate status counts
    status_counts = Counter(item.status for item in items)
    sorted_status_counts = dict(sorted(status_counts.items(), key=lambda x: x[1], reverse=True))

    # Total count of items
    total_count = len(items)

    # Get aggregated data
    asset_type_counts = db.session.query(Inventory.asset_type, db.func.count(Inventory.id)).group_by(Inventory.asset_type).all()
    department_counts = db.session.query(Inventory.department, db.func.count(Inventory.id)).group_by(Inventory.department).all()
    country_counts = db.session.query(Inventory.country, db.func.count(Inventory.id)).group_by(Inventory.country).all()
    status_counts = db.session.query(Inventory.status, db.func.count(Inventory.id)).group_by(Inventory.status).all()

    # Filters
    search_query = request.args.get('search_query', '')
    asset_type_filter = request.args.get('asset_type')
    department_filter = request.args.get('department')
    country_filter = request.args.get('country')
    status_filter = request.args.get('status')
    purchase_date_start = request.args.get('purchase_date_start')
    purchase_date_end = request.args.get('purchase_date_end')
    warranty_end_date_start = request.args.get('warranty_end_date_start')
    warranty_end_date_end = request.args.get('warranty_end_date_end')

    # Apply filters
    items_query = Inventory.query

    # Apply search query if provided
    if search_query:
        items_query = items_query.filter(
            Inventory.asset_tag.contains(search_query) |
            Inventory.brand.contains(search_query) |
            Inventory.model.contains(search_query) |
            Inventory.current_owner.contains(search_query) |
            Inventory.previous_owner.contains(search_query) |
            Inventory.serial_number.contains(search_query)
        )

    if asset_type_filter:
        items_query = items_query.filter_by(asset_type=asset_type_filter)
    if department_filter:
        items_query = items_query.filter_by(department=department_filter)
    if country_filter:
        items_query = items_query.filter_by(country=country_filter)
    if status_filter:
        items_query = items_query.filter_by(status=status_filter)
    if purchase_date_start:
        items_query = items_query.filter(Inventory.purchase_date >= datetime.strptime(purchase_date_start, '%Y-%m-%d'))
    if purchase_date_end:
        items_query = items_query.filter(Inventory.purchase_date <= datetime.strptime(purchase_date_end, '%Y-%m-%d'))
    if warranty_end_date_start:
        items_query = items_query.filter(Inventory.warranty_end_date >= datetime.strptime(warranty_end_date_start, '%Y-%m-%d'))
    if warranty_end_date_end:
        items_query = items_query.filter(Inventory.warranty_end_date <= datetime.strptime(warranty_end_date_end, '%Y-%m-%d'))

    # Pagination with 20 items per page
    page = request.args.get('page', 1, type=int)
    per_page = 20  # Number of items per page
    items = items_query.paginate(page=page, per_page=per_page, error_out=False)

    # Prepare a clean dictionary of query parameters
    query_params = request.args.copy()
    query_params.pop('page', None)  # Remove 'page' if it exists

    return render_template('home.html',
                           items=items.items,
                           asset_type_counts=asset_type_counts,
                           department_counts=department_counts,
                           country_counts=country_counts,
                           status_counts=status_counts,
                           asset_type_filter=asset_type_filter,
                           department_filter=department_filter,
                           country_filter=country_filter,
                           purchase_date_start=purchase_date_start,
                           purchase_date_end=purchase_date_end,
                           warranty_end_date_start=warranty_end_date_start,
                           warranty_end_date_end=warranty_end_date_end,
                           pagination=items,
                           query_params=query_params,
                           asset_types=ASSET_TYPES,
                           statuses=STATUS,
                           brands=BRANDS,
                           operating_systems=OPERATING_SYSTEMS,
                           departments=DEPARTMENTS,
                           offices=OFFICES,
                           countries=COUNTRIES,
                           vendor_locations=VENDOR_LOCATIONS,
                           device_counts=sorted_brand_counts,
                           sorted_status_counts=sorted_status_counts,
                           total_count=total_count,
                           search_query=search_query)
                           


@main.route('/add', methods=['GET', 'POST'])
@login_required
def add_item():
    form = InventoryForm()
    form.asset_type.choices = [(at, at) for at in ASSET_TYPES]
    form.status.choices = [(st, st) for st in STATUS]
    form.brand.choices = [(br, br) for br in BRANDS]
    form.operating_system.choices = [(os, os) for os in OPERATING_SYSTEMS]
    form.department.choices = [(dp, dp) for dp in DEPARTMENTS]
    form.office.choices = [(of, of) for of in OFFICES]
    form.country.choices = [(ct, ct) for ct in COUNTRIES]
    form.vendor_location.choices = [(vl, vl) for vl in VENDOR_LOCATIONS]

    if form.validate_on_submit():
        try:
            # Check if serial number already exists
            existing_item = Inventory.query.filter_by(serial_number=form.serial_number.data).first()
            if existing_item:
                flash(f'An item with serial number {form.serial_number.data} already exists!', 'danger')
                return redirect(url_for('main.add_item'))

            new_item = Inventory(
                asset_tag=form.asset_tag.data,
                asset_type=form.asset_type.data,
                status=form.status.data,
                brand=form.brand.data,
                model=form.model.data,
                fa_code=form.fa_code.data,
                serial_number=form.serial_number.data,
                operating_system=form.operating_system.data,
                purchase_date=form.purchase_date.data,
                age=form.age.data,
                current_owner=form.current_owner.data,
                previous_owner=form.previous_owner.data,
                warranty_end_date=form.warranty_end_date.data,
                condition_notes=form.condition_notes.data,
                department=form.department.data,
                office=form.office.data,
                country=form.country.data,
                vendor_location=form.vendor_location.data,
                updated_by=current_user.username
            )
            
            # Add the new item
            db.session.add(new_item)
            db.session.flush()  # This gets us the new item's ID before commit

            # Prepare item details for logging
            item_details = {
                'asset_tag': new_item.asset_tag,
                'asset_type': new_item.asset_type,
                'status': new_item.status,
                'brand': new_item.brand,
                'model': new_item.model,
                'serial_number': new_item.serial_number,
                'department': new_item.department,
                'current_owner': new_item.current_owner
            }

            # Create log entry with serial number
            log = Log(
                user_id=current_user.id,
                action="Added item",
                item_id=new_item.id,
                serial_number=new_item.serial_number,
                changes=f"User {current_user.username} added new item with details: {str(item_details)}"
            )
            
            db.session.add(log)
            db.session.commit()

            # Log success
            current_app.logger.info(
                f'User {current_user.username} added new item: {new_item.asset_tag} '
                f'with serial number: {new_item.serial_number}'
            )
            
            flash(f'Item added successfully! Serial Number: {new_item.serial_number}', 'success')
            return redirect(url_for('main.home'))

        except Exception as e:
            db.session.rollback()
            current_app.logger.error(
                f'Error adding item with serial number {form.serial_number.data}: {str(e)}',
                exc_info=True
            )
            flash(f'An error occurred while adding the item: {str(e)}. Please try again.', 'danger')
            
    elif request.method == 'POST':
        current_app.logger.warning(
            f'Form validation failed for user {current_user.username}: {form.errors}'
        )
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"Error in {getattr(form, field).label.text}: {error}", 'danger')

    return render_template(
        'add_item.html',
        form=form,
        asset_types=ASSET_TYPES,
        statuses=STATUS,
        brands=BRANDS,
        operating_systems=OPERATING_SYSTEMS,
        departments=DEPARTMENTS,
        offices=OFFICES,
        countries=COUNTRIES,
        vendor_locations=VENDOR_LOCATIONS
    )

@main.route('/edit/<int:item_id>', methods=['GET', 'POST'])
@login_required
def edit_item(item_id):
    item = Inventory.query.get_or_404(item_id)
    form = InventoryForm(obj=item)

    # Set form choices
    form.asset_type.choices = [(at, at) for at in ASSET_TYPES]
    form.status.choices = [(st, st) for st in STATUS]
    form.brand.choices = [(br, br) for br in BRANDS]
    form.operating_system.choices = [(os, os) for os in OPERATING_SYSTEMS]
    form.department.choices = [(dp, dp) for dp in DEPARTMENTS]
    form.office.choices = [(of, of) for of in OFFICES]
    form.country.choices = [(ct, ct) for ct in COUNTRIES]
    form.vendor_location.choices = [(vl, vl) for vl in VENDOR_LOCATIONS]
    
    if form.validate_on_submit():
        old_data = {field.name: getattr(item, field.name) for field in item.__table__.columns}
        form.populate_obj(item)
        item.updated_by = current_user.username
        
        # Detect changes
        changes = {}
        for field in item.__table__.columns:
            new_value = getattr(item, field.name)
            if old_data[field.name] != new_value:
                changes[field.name] = {'old': old_data[field.name], 'new': new_value}
        
        db.session.commit()
        
        # Log the update
        log = Log(
            user_id=current_user.id,
            action="Updated item",
            item_id=item.id,
            serial_number=item.serial_number,
            changes=str(changes)
        )
        db.session.add(log)
        db.session.commit()
        
        current_app.logger.info(f'{current_user.username} updated item: {item.asset_tag} with serial number: {item.serial_number}')
        flash('Item updated successfully!', 'success')
        return redirect(url_for('main.home'))
    
    return render_template(
        'edit_item.html',
        form=form,
        item=item,
        asset_types=ASSET_TYPES,
        statuses=STATUS,
        brands=BRANDS,
        operating_systems=OPERATING_SYSTEMS,
        departments=DEPARTMENTS,
        offices=OFFICES,
        countries=COUNTRIES,
        vendor_locations=VENDOR_LOCATIONS
    )

@main.route('/view_logs')
@login_required
def view_logs():
    # Get the filter parameter from the URL
    log_filter = request.args.get('filter', 'all')

    # Base query
    query = Log.query

    # Apply filter if specified
    if log_filter == 'csv_import':
        query = query.filter(Log.action == 'CSV Import')

    # Order logs by timestamp descending
    logs = query.order_by(Log.timestamp.desc()).all()

    current_app.logger.info(f"Fetched {len(logs)} logs")
    for log in logs:
        current_app.logger.debug(f"Log: ID {log.id}, Action {log.action}, Item ID {log.item_id}, Changes {log.changes}")

    return render_template('view_logs.html', logs=logs, current_filter=log_filter)

@main.route('/export_csv')
@login_required
def export_csv():
    # Fetch inventory items from the database
    items = Inventory.query.filter_by(is_deleted=False).all()

    
    # Create a CSV in memory
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write header row
    writer.writerow([
        'Asset Tag', 'Asset Type', 'Status', 'Brand', 'Model',
        'FA Code', 'Serial Number', 'Operating System', 'Purchase Date',
        'Age', 'Current Owner', 'Previous Owner', 'Warranty End Date',
        'Condition Notes', 'Department', 'Office', 'Country', 'Vendor Location', 'Updated By'
    ])
    
    # Write data rows
    for item in items:
        writer.writerow([
            item.asset_tag, item.asset_type, item.status, item.brand, item.model,
            item.fa_code, item.serial_number, item.operating_system, item.purchase_date,
            item.age, item.current_owner, item.previous_owner, item.warranty_end_date,
            item.condition_notes, item.department, item.office, item.country, item.vendor_location, item.updated_by
        ])
    
    # Create a response object with CSV content
    output.seek(0)
    return Response(
        output,
        mimetype='text/csv',
        headers={"Content-Disposition": "attachment;filename=inventory_data.csv"}
    )

@main.route('/export_logs_csv')
@login_required
def export_logs_csv():
    # Fetch logs from the database
    logs = Log.query.all()
    
    # Create a CSV in memory
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write header row
    writer.writerow([
        'Timestamp', 'User ID', 'Username', 'Action', 'Item ID', 'Changes'
    ])
    
    # Write data rows
    for log in logs:
        username = User.query.get(log.user_id).username if log.user_id else 'Unknown'
        writer.writerow([
            log.timestamp,
            log.user_id,
            username,
            log.action,
            log.item_id,
            log.changes
        ])
    
    # Create a response object with CSV content
    output.seek(0)
    return Response(
        output,
        mimetype='text/csv',
        headers={"Content-Disposition": "attachment;filename=logs_data.csv"}
    )


@main.route('/add_user', methods=['GET', 'POST'])
@login_required
def add_user():
    if current_user.username != 'Admin':
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('main.home'))
    
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if User.query.filter_by(username=username).first():
            flash('Username already exists.', 'danger')
            return redirect(url_for('main.add_user'))
        new_user = User(username=username)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        
        # Log the user addition
        log = Log(
            user_id=current_user.id,
            action="Added user",
            item_id=None,
            changes=f"Added user with username: {username}"
        )
        db.session.add(log)
        db.session.commit()
        
        flash('User added successfully.', 'success')
        return redirect(url_for('main.home'))
    
    return render_template('add_user.html')

@main.route('/delete_user/<int:user_id>', methods=['POST'])
@login_required
def delete_user(user_id):
    user = User.query.get(user_id)
    if user and user.username != 'Admin':
        # Delete all logs related to this user
        logs = Log.query.filter_by(user_id=user_id).all()
        for log in logs:
            db.session.delete(log)
        
        db.session.delete(user)
        db.session.commit()
        
        flash('User deleted successfully.', 'success')
    else:
        flash('Superuser cannot be deleted.', 'error')
    
    return redirect(url_for('main.view_users'))


@main.route('/view_users')
@login_required
def view_users():
    if current_user.username != 'Admin':
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('main.home'))

    users = User.query.all()
    return render_template('view_users.html', users=users)

@main.route('/reset_password/<int:user_id>', methods=['GET', 'POST'])
def reset_password(user_id):
    user = User.query.get_or_404(user_id)
    if request.method == 'POST':
        form = ResetPasswordForm(request.form)
        if form.validate():
            user.password_hash = generate_password_hash(form.new_password.data)
            db.session.commit()
            flash('Password reset successfully!', 'success')
            return redirect(url_for('main.view_users'))
        else:
            flash('Error resetting password. Please try again.', 'danger')
    else:
        form = ResetPasswordForm()
    return render_template('reset_password.html', form=form, user=user)

@main.route('/import_csv', methods=['GET', 'POST'])
@login_required
def import_csv():
    if request.method == 'POST':
        file = request.files['file']
        if not file:
            flash('No file selected!', 'danger')
            return redirect(request.url)

        try:
            # Read the CSV file
            stream = io.StringIO(file.stream.read().decode("UTF8"), newline=None)
            csv_input = csv.reader(stream)

            # Skip the header row if your CSV file has one
            next(csv_input, None)

            # Count imported rows
            imported_count = 0

            # Function to parse dates flexibly
            def parse_date(date_string):
                date_formats = ['%Y-%m-%d', '%d-%m-%Y', '%m-%d-%Y']
                for date_format in date_formats:
                    try:
                        return datetime.strptime(date_string, date_format)
                    except ValueError:
                        continue
                raise ValueError(f"Unable to parse date: {date_string}")

            # Iterate over the CSV rows
            for row in csv_input:
                # Assuming your CSV columns are in the same order as your Inventory model
                new_item = Inventory(
                    asset_tag=row[0],
                    asset_type=row[1],
                    status=row[2],
                    brand=row[3],
                    model=row[4],
                    fa_code=row[5],
                    serial_number=row[6],
                    operating_system=row[7],
                    purchase_date=parse_date(row[8]),
                    age=row[9],
                    current_owner=row[10],
                    previous_owner=row[11],
                    warranty_end_date=parse_date(row[12]),
                    condition_notes=row[13],
                    department=row[14],
                    office=row[15],
                    country=row[16],
                    vendor_location=row[17],
                    updated_by=current_user.username
                )
                db.session.add(new_item)
                imported_count += 1

            db.session.commit()

            # Log the import activity
            log_entry = Log(
                action="CSV Import",
                item_id=None,
                changes=f"Imported {imported_count} items",
                user_id=current_user.id
            )
            db.session.add(log_entry)
            db.session.commit()

            flash(f'CSV file imported successfully! {imported_count} items added.', 'success')
            return redirect(url_for('main.home'))

        except ValueError as e:
            db.session.rollback()
            current_app.logger.error(f'Error importing CSV file: {e}')
            flash(f'An error occurred while importing the file: {e}. Please check the date format and try again.', 'danger')
            return redirect(request.url)
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f'Error importing CSV file: {e}')
            flash('An unexpected error occurred while importing the file. Please check the format and try again.', 'danger')
            return redirect(request.url)
    
    return render_template('import_csv.html')

@main.route('/device_count', methods=['GET'])
@login_required
def device_count():
    # Get all items
    items = Inventory.query.all()

    # Calculate brand & Status counts
    brand_counts = Counter(item.brand for item in items)
    status_counts = Counter(item.status for item in items)

    # Sort brand counts in descending order
    sorted_brand_counts = dict(sorted(brand_counts.items(), key=lambda x: x[1], reverse=True))
    sorted_status_counts = dict(sorted(status_counts.items(), key=lambda x: x[1], reverse=True))

    # Total count of items
    total_count = len(items)

    return render_template('device_count.html',
                           brand_counts=sorted_brand_counts,
                           status_counts=sorted_status_counts,
                           total_count=total_count)


@main.route('/delete/<int:item_id>', methods=['POST'])
@login_required
def delete_item(item_id):
    # Check if the user has admin permissions
    if current_user.username != 'Admin':
        flash("You do not have permission to delete items.", "danger")
        return redirect(url_for('main.home'))

    # Retrieve the item to be deleted
    item = Inventory.query.get_or_404(item_id)

    try:
        # Log deletion details before deleting the item
        delete_log = Log(
            user_id=current_user.id,
            action="Deleted item",
            item_id=item_id,
            serial_number=item.serial_number,
            changes=f"Deleted item with asset tag: {item.asset_tag}, type: {item.asset_type}"
        )
        db.session.add(delete_log)

        # Physically delete the item from the database
        db.session.delete(item)

        # Commit both the log and the deletion
        db.session.commit()

        flash('Item deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Error deleting item: {e}')
        flash('An error occurred while deleting the item. Please try again.', 'danger')

    return redirect(url_for('main.home'))


@main.route('/delete_all', methods=['POST'])
@login_required
def delete_all_items():
    # Check if the user has admin permissions
    if current_user.username != 'Admin':
        flash("You do not have permission to delete all items.", "danger")
        return redirect(url_for('main.home'))

    try:
        # Get all items before deletion for logging purposes
        all_items = Inventory.query.all()
        item_count = len(all_items)

        # Log deletion for each item individually to preserve serial numbers
        for item in all_items:
            delete_log = Log(
                user_id=current_user.id,
                action="Bulk deletion",
                item_id=item.id,
                serial_number=item.serial_number,
                changes=f"Item deleted by {current_user.username} during bulk deletion: Asset Tag: {item.asset_tag}, Type: {item.asset_type}, Brand: {item.brand}, Model: {item.model}",
                timestamp=datetime.utcnow()
            )
            db.session.add(delete_log)

        # Physically delete all items from the inventory
        for item in all_items:
            db.session.delete(item)

        # Commit the changes
        db.session.commit()

        current_app.logger.info(f'User {current_user.username} deleted all items ({item_count} items)')
        flash(f'All items ({item_count}) have been deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Error deleting all items: {e}')
        flash('An error occurred while deleting all items. Please try again.', 'danger')

    return redirect(url_for('main.home'))
