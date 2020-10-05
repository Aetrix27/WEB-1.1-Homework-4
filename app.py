from flask import Flask, request, redirect, render_template, url_for
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
import os

############################################################
# SETUP
############################################################

app = Flask(__name__)

host = os.environ.get('MONGODB_URI', 'mongodb://localhost:27017/plantprojectfirstdeployment') + "?retryWrites=false"
app.config["MONGO_URI"] = host
mongo = PyMongo(app)

############################################################
# ROUTES
############################################################

@app.route('/')
def plants_list():
    """Display the plants list page."""
  
    plants_data=mongo.db.plants.find({})
 
    context = {
        'plants': plants_data,
    }

    return render_template('plants_list.html', **context)

@app.route('/about')
def about():
    """Display the about page."""
    return render_template('about.html')

@app.route('/create', methods=['GET', 'POST'])
def create():
    """Display the plant creation page & process data from the creation form."""
    plant=request.form.get('plant_name')
    photo=request.form.get('photo')
    date_planted=request.form.get('date_planted')
    variety=request.form.get('variety')

    if request.method == 'POST':
        new_plant = {
            'name': plant,
            'photo_url': photo,
            'date_planted': date_planted,
            'variety' : variety
        }

        result=mongo.db.plants.insert_one(new_plant)
        inserted_id=result.inserted_id

        return redirect(url_for('detail', plant_id=inserted_id))
    else:
        return render_template('create.html')

@app.route('/plant/<plant_id>')
def detail(plant_id):
    """Display the plant detail page & process data from the harvest form."""

    plant_to_show = mongo.db.plants.find_one({ 
        "_id": ObjectId(plant_id)
    })

    harvests = mongo.db.harvests.find({
        "plant_id": ObjectId(plant_id)
    })

    context = {
        'plant': plant_to_show,
        'harvests': harvests,
        'plant_id': ObjectId(plant_id),
    }

    return render_template('detail.html', **context)

@app.route('/harvest/<plant_id>', methods=['POST'])
def harvest(plant_id):
    """Display the plant detail page & process data from the harvest form."""
    date_harvested = request.form.get("date_harvested")
    harvested_amount=request.form.get("harvested_amount")
    input_string= harvested_amount

    new_harvest = {
        'quantity': input_string,
        'date': date_harvested,
        'plant_id': ObjectId(plant_id)
    }

    mongo.db.harvests.insert_one(new_harvest)

    return redirect(url_for('detail', plant_id=plant_id))

@app.route('/edit/<plant_id>', methods=['GET', 'POST'])
def edit(plant_id):
    """Shows the edit page and accepts a POST request with edited data."""
    if request.method == 'POST':
        plant = request.form.get('plant_name')
        photo = request.form.get('photo')
        date_planted = request.form.get('date_planted')
        variety = request.form.get('variety')

        mongo.db.plants.update_one({
            '_id': ObjectId(plant_id)
        },
        {
            '$set': { 
                '_id': ObjectId(plant_id),
                'plant_name' : plant,
                'date_planted' : date_planted,
                'variety' : variety,
                'photo_url' : photo
            }
        })
        
        return redirect(url_for('detail', plant_id=plant_id))
    else:
        plant_to_show=mongo.db.plants.find_one({
            '_id': ObjectId(plant_id)
        })

        context = {
            'plant': plant_to_show
        }

        return render_template('edit.html', **context)

@app.route('/delete/<plant_id>', methods=['POST'])
def delete(plant_id):
    mongo.db.plants.delete_one({
        '_id': ObjectId(plant_id)
    })
    mongo.db.harvests.delete_many({
        'plant_id': ObjectId(plant_id)
    })

    return redirect(url_for('plants_list'))

if __name__ == '__main__':
    app.run(debug=True)