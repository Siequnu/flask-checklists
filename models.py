from flask import current_app
from app import db
from datetime import datetime

class Checklist (db.Model):
	__table_args__ = {'sqlite_autoincrement': True}
	id = db.Column(db.Integer, primary_key=True)
	title = db.Column(db.String(250))
	description = db.Column(db.String(500))
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
	
	def __repr__(self):
		return '<Checklist {}>'.format(self.id)

	def add (self):
		db.session.add(self)
		db.session.commit()

	def delete (self):
		# Find any checklist items tied to this list and delete them
		items = ChecklistItem.query.filter_by(checklist_id = self.id)
		for item in items:
			item.delete()

		db.session.delete(self)
		db.session.commit()

	def get_completed_progress_percentage (self):
		# How many checklist items are associated with this list?
		all_checklist_items = ChecklistItem.query.filter_by(checklist_id = self.id).all()
		completed_checklist_items = ChecklistItem.query.filter_by(
			checklist_id = self.id).filter_by(
			completed = True).all()
		if len(all_checklist_items) == 0:
			return 100
		else:
			return int(len(completed_checklist_items)/len(all_checklist_items) * 100)

	def get_remaining_items_count (self):
		return len(ChecklistItem.query.filter_by(
			checklist_id = self.id).filter_by(
			completed = True).all())


class ChecklistItem (db.Model):
	__table_args__ = {'sqlite_autoincrement': True}
	id = db.Column(db.Integer, primary_key=True)
	title = db.Column(db.String(250))
	description = db.Column(db.String(500))
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
	checklist_id = db.Column(db.Integer, db.ForeignKey('checklist.id'))
	completed = db.Column(db.Boolean, default=False)
	
	def __repr__(self):
		return '<Checklist item {}>'.format(self.id)

	def add (self):
		db.session.add(self)
		db.session.commit()

	def toggle_status(self):
		self.completed = not self.completed
		db.session.commit ()

	def delete (self):
		db.session.delete(self)
		db.session.commit()
		

# Returns all checklists, with their items and additional information appended to the array
def get_all_checklist_info (checklist_id = False):
	if checklist_id:
		checklists = Checklist.query.filter_by(id = checklist_id).all()
	else:
		checklists = Checklist.query.all()
	checklists_array = []
	for checklist in checklists:
		checklist_dict = checklist.__dict__
		checklist_dict['checklist_items'] = ChecklistItem.query.filter_by(checklist_id = checklist.id).all()
		checklist_dict['completed_progress_percentage'] = checklist.get_completed_progress_percentage ()
		checklist_dict['remaining_items'] = len(ChecklistItem.query.filter_by(
			checklist_id = checklist.id).filter_by(completed = False).all())
		checklists_array.append (checklist_dict)
	
	if checklist_id: return checklists_array.pop()
	else: return checklists_array