from flask import render_template, request, jsonify, redirect, url_for
from flask_login import login_required
from flask_babel import _
from . import exercise_bp
from ...models.exercise import Exercise
from sqlalchemy import or_
from ...data.program_data import PROGRAM_EXERCISES

@exercise_bp.route('/exercises')
@login_required
def index():
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    muscle = request.args.get('muscle', '')
    level = request.args.get('level', '')
    equipment = request.args.get('equipment', '')
    
    query = Exercise.query
    
    if search:
        query = query.filter(Exercise.name.ilike(f'%{search}%'))
    
    if muscle:
        query = query.filter(or_(
            Exercise._primary_muscles.ilike(f'%{muscle}%'),
            Exercise._secondary_muscles.ilike(f'%{muscle}%')
        ))
        
    if level:
        query = query.filter(Exercise.level == level)
        
    if equipment:
        query = query.filter(Exercise.equipment == equipment)
        
    pagination = query.paginate(page=page, per_page=12, error_out=False)
    exercises = pagination.items
    
    # Get unique values for filters
    # In a real app, these could be cached or hardcoded
    muscles = ["abdominals", "abductors", "adductors", "biceps", "calves", "chest", "forearms", "glutes", "hamstrings", "lats", "lower back", "middle back", "neck", "quadriceps", "shoulders", "traps", "triceps"]
    levels = ["beginner", "intermediate", "expert"]
    equipments = ["body only", "dumbbell", "barbell", "kettlebells", "machine", "cable", "bands", "medicine ball", "exercise ball", "e-z curl bar"]

    return render_template('exercise/index.html', 
                           exercises=exercises, 
                           pagination=pagination,
                           muscles=muscles,
                           levels=levels,
                           equipments=equipments,
                           current_muscle=muscle,
                           current_level=level,
                           current_equipment=equipment,
                           search=search)

@exercise_bp.route('/api/program/<string:program_id>')
def api_program(program_id):
    program = PROGRAM_EXERCISES.get(program_id)
    if not program:
        return jsonify({"error": _("Program not found")}), 404
    
    # Translate content dynamically
    translated_program = {
        "title": _(program["title"]),
        "price": program.get("price", ""),
        "exercises": [
            {
                "name": _(ex["name"]),
                "desc": _(ex["desc"]),
                "icon": ex["icon"]
            } for ex in program["exercises"]
        ]
    }
    return jsonify(translated_program)

@exercise_bp.route('/api/exercises')
def api_index():
    category = request.args.get('category', '')
    muscle = request.args.get('muscle', '')
    equipment = request.args.get('equipment', '')
    
    query = Exercise.query
    if category:
        query = query.filter(Exercise.category == category)
    if muscle:
        query = query.filter(or_(
            Exercise._primary_muscles.ilike(f'%{muscle}%'),
            Exercise._secondary_muscles.ilike(f'%{muscle}%')
        ))
    if equipment:
        query = query.filter(Exercise.equipment == equipment)
        
    exercises = query.all()
    return jsonify([e.to_dict() for e in exercises])

@exercise_bp.route('/exercises/<string:exercise_id>')
@login_required
def detail(exercise_id):
    exercise = Exercise.query.get_or_404(exercise_id)
    # Recommended exercises (same muscle group)
    related = Exercise.query.filter(
        Exercise.id != exercise.id,
        Exercise._primary_muscles.ilike(f'%{exercise.primary_muscles[0]}%')
    ).limit(12).all()
    
    return render_template('exercise/detail.html', exercise=exercise, related=related)
