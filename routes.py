from flask import render_template, flash, redirect, url_for, request, abort, current_app, session, Response
from flask_login import current_user, login_required

from . import bp, models
from .models import Checklist, ChecklistItem
from .forms import ChecklistForm, ChecklistItemForm

import app.models
from app.models import User


# Render this blueprint's javascript
@bp.route("/js/<filename>")
@login_required
def load_js(filename):
	filepath = 'js/' + filename
	# is send_from_directory('/templates/js/', path) a safer approach?
	return render_template(filepath)

# Main checklist overview
@bp.route("/")
@login_required
def view_checklists():
	if app.models.is_admin(current_user.username):
		checklists = models.get_all_checklist_info ()
		return render_template('view_checklists.html', checklists = checklists)


# View an individual checklist
@bp.route("/view/<int:checklist_id>")
@login_required
def view_checklist(checklist_id):
	checklist = Checklist.query.get(checklist_id)
	if checklist is None: abort (404)
	checklist_info = models.get_all_checklist_info (checklist_id = checklist_id)
	if app.models.is_admin(current_user.username):
		return render_template('view_checklist.html', checklist = checklist, checklist_info = checklist_info)
	abort(403)


# Add a new checklist item
@bp.route("/add", methods = ['GET', 'POST'])
@login_required
def add_checklist():
	if app.models.is_admin(current_user.username):
		form = ChecklistForm()
		if form.validate_on_submit():
			checklist = Checklist(
				title = form.title.data,
				description = form.description.data,
				user_id = current_user.id,
			)
			checklist.add()
			flash ('Checklist saved', 'success')
			return redirect(url_for('checklists.view_checklists'))
		return render_template('add_checklist.html', form = form, title = 'Add checklist goal')
	else:
		abort (403)


# Redirect route to remove a checklist
@bp.route("/remove/<int:checklist_id>")
@login_required
def remove_checklist(checklist_id):
	if app.models.is_admin(current_user.username):
		checklist = Checklist.query.get(checklist_id)
		if checklist is None:
			abort (404)
		checklist.delete()
		
		flash ('Checklist removed', 'success')
		return redirect(url_for('checklists.view_checklists'))
	else:
		abort (403)

# Add a new checklist item
@bp.route("/add/item/<checklist_id>", methods = ['GET', 'POST'])
@login_required
def add_checklist_item(checklist_id):
	if current_user.is_authenticated and app.models.is_admin(current_user.username):
		form = ChecklistForm()
		checklist = Checklist.query.filter_by(id=checklist_id).first()
		if checklist is None:
			flash('Could not locate this checklist.', 'error')
			return redirect(url_for('checklists.view_checklists'))
		else:
			if form.validate_on_submit():
				checklist_item = ChecklistItem(
					title = form.title.data,
					description = form.description.data,
					user_id = current_user.id,
					checklist_id = checklist_id,
				)
				checklist_item.add()
				flash ('Checklist item saved', 'success')
				return redirect(url_for('checklists.view_checklist', checklist_id = checklist.id))
			return render_template('add_goal.html', form = form, title = 'Add checklist item', checklist = checklist)
	else:
		abort (403)


# Redirect route to remove a checklist item
@bp.route("/remove/item/<int:checklist_item_id>")
@login_required
def remove_checklist_item(checklist_item_id):
	if app.models.is_admin(current_user.username):
		checklist_item = ChecklistItem.query.get(checklist_item_id)
		if checklist_item is None:
			abort (404)
		checklist_id = checklist_item.id
		checklist_item.delete()
		
		flash ('Checklist item removed', 'success')
		return redirect(url_for('checklists.view_checklist', checklist_id = checklist_id))
	else:
		abort (403)


# Admin redirect route to mark a checklist item as completed
@bp.route("/completed/<checklist_item_id>")
@login_required
def toggle_item_status(checklist_item_id):
	if app.models.is_admin(current_user.username):
		checklist = Checklist.query.get(checklist_item_id)
		if checklist is None:
			flash('Could not locate this checklist.', 'error')
			return redirect(url_for('checklists.view_checklists'))
		
		checklist_item = ChecklistItem.query.get(checklist_item_id)
		if checklist_item is None:
			flash('Could not locate this checklist item.', 'error')
			return redirect(url_for('checklist.view_checklists', checklist_id = checklist.id))
		checklist_item.toggle_status()
		return redirect(url_for('checklist.view_checklists', checklist_id = checklist.id))
	else:
		abort (403)