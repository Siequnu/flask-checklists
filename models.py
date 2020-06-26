from flask import current_app
from app import db
from datetime import datetime

from app.models import User

class Checklist (db.Model):
	__table_args__ = {'sqlite_autoincrement': True}
	id = db.Column(db.Integer, primary_key=True)
	title = db.Column(db.String(250))
	description = db.Column(db.String(500))
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
	checklist_group_id = db.Column(db.Integer, db.ForeignKey('checklist_group.id'), nullable=True)
	hue = db.Column(db.Integer)
	saturation = db.Column(db.Integer)
	lightness = db.Column(db.Integer)
	
	def __repr__(self):
		return '<Checklist {}>'.format(self.id)

	def add (self):
		db.session.add(self)
		db.session.commit()

	def save (self):
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
		return ChecklistItem.query.filter_by(
			checklist_id = self.id).filter_by(
			completed = False).count()

	def add_to_checklist_group (self, checklist_group_id):
		relationship = ChecklistGroupRelationship (
			checklist_id = self.id,
			checklist_group_id = checklist_group_id)
		db.session.add(relationship)
		db.session.commit()

	def remove_from_checklist_group (self, checklist_group_id):
		# This should only ever be one relationship, but search all() for robustness
		relationships = ChecklistGroupRelationship.query.filter_by(
			checklist_group_id = checklist_group_id).filter_by(
			checklist_id = self.id).all()
		if relationships is not None:
			for item in relationships:
				db.session.delete(item)
				db.session.commit()

	def set_hsl (self, hue, saturation, lightness):
		self.hue = int (hue)
		self.saturation = int (saturation)
		self.lightness = int (lightness)
		db.session.commit ()


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


class ChecklistGroup (db.Model):
	__table_args__ = {'sqlite_autoincrement': True}
	id = db.Column(db.Integer, primary_key=True)
	title = db.Column(db.String(250))
	description = db.Column(db.String(500))
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
	
	def __repr__(self):
		return '<Checklist group {}>'.format(self.id)

	def add (self):
		db.session.add(self)
		db.session.commit()

	def save (self):
		db.session.commit()

	def delete (self, delete_all_checklists = False):
		# Find any checklists associated with this group
		checklist_group_relationships = ChecklistGroupRelationship.query.filter_by(checklist_group_id = self.id)
		
		if delete_all_checklists:
			# Delete all checklists
			for relationship in checklist_group_relationships:
				checklist_id = relationship.checklist_id
				
				db.session.delete (relationship)
				db.session.commit()

				checklist = Checklist.query.get(checklist_id)
				checklist.delete()

			
		else:
			# Unset these checklists
			for relationship in checklist_group_relationships:
				db.session.delete(relationship)
				db.session.commit()

		db.session.delete(self)
		db.session.commit()

	def get_completed_progress_percentage (self):
		# How many checklists are associated with this group?
		all_checklists = db.session.query(Checklist, ChecklistGroupRelationship).join(
			ChecklistGroupRelationship, Checklist.id == ChecklistGroupRelationship.checklist_id).filter(
			ChecklistGroupRelationship.checklist_group_id == self.id).all()

		number_of_checklists = len(all_checklists)
		
		total_completed_progress_percentage = 0
		for checklist, checklist_group_relationship in all_checklists:
			total_completed_progress_percentage += checklist.get_completed_progress_percentage()
		
		if len(all_checklists) == 0:
			return 100
		else:
			return int(total_completed_progress_percentage/number_of_checklists)

	def get_group_remaining_items_count (self):
		# How many checklists are associated with this group?
		all_checklists = db.session.query(Checklist, ChecklistGroupRelationship).join(
			ChecklistGroupRelationship, Checklist.id == ChecklistGroupRelationship.checklist_id).filter(
			ChecklistGroupRelationship.checklist_group_id == self.id).all()
		
		remaining_items_count = 0
		
		for checklist, checklist_group_relationship in all_checklists:
			remaining_items_count += checklist.get_remaining_items_count()
		
		return remaining_items_count


def get_all_checklist_group_info (checklist_group_id = False):
	# Get the checklist group object or objects
	if checklist_group_id:
		checklist_groups = ChecklistGroup.query.filter_by(id = checklist_group_id).all()
	else:
		checklist_groups = ChecklistGroup.query.all()
	
	
	# Make a blank array for storing groups>checklists>items
	checklist_groups_array = []
	for group in checklist_groups:
		# Convert each group object into a dictionary
		group_dict = group.__dict__
		
		# For each group, get the corresponding checklists
		checklists_array = []
		checklists = db.session.query(Checklist, ChecklistGroupRelationship).join(
			ChecklistGroupRelationship, Checklist.id == ChecklistGroupRelationship.checklist_id).filter(
			ChecklistGroupRelationship.checklist_group_id == group.id).all()

		# For each checklist, assemble relevant information
		for checklist, checklist_group_relationship in checklists:
			checklist_dict = checklist.__dict__
			checklist_dict['completed_progress_percentage'] = checklist.get_completed_progress_percentage ()
			checklist_dict['checklist_info'] = get_all_checklist_info (checklist.id)
			checklists_array.append(checklist_dict)

		group_dict['checklists'] = checklists_array
		group_dict['group_completed_progress_percentage'] = group.get_completed_progress_percentage ()
		group_dict['group_remaining_items_count'] = group.get_group_remaining_items_count ()
		group_dict['created_by'] = User.query.get(group.user_id)
		checklist_groups_array.append(group_dict)

	
	if checklist_group_id: return checklist_groups_array.pop()
	else: return checklist_groups_array


class ChecklistGroupRelationship(db.Model):
	__table_args__ = {'sqlite_autoincrement': True}
	id = db.Column(db.Integer, primary_key=True)
	checklist_id = db.Column(db.Integer, db.ForeignKey('checklist.id'))
	checklist_group_id = db.Column(db.Integer, db.ForeignKey('checklist_group.id'))
	
	def __repr__(self):
		return '<Checklist group relationship {}>'.format(self.id)

	def add (self):
		db.session.add(self)
		db.session.commit()

	def delete (self):
		db.session.delete(self)
		db.session.commit()