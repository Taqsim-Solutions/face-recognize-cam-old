from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
import base64

app = Flask(__name__, template_folder='', static_folder='static')
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:1234@localhost/postgres'
db = SQLAlchemy(app)

# Define the model for the face_recognition table
class FaceRecognition(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    time = db.Column(db.DateTime)
    image_data = db.Column(db.LargeBinary)

# Route to display face records with pagination
@app.route('/')
def show_face_records():
    page = request.args.get('page', 1, type=int)
    per_page = 7  # Number of records per page

    records = FaceRecognition.query.order_by(FaceRecognition.time.desc()).paginate(page=page, per_page=per_page)

    # Convert image data to Base64 and update the record
    records_with_images = []
    for record in records.items:
        image_data = record.image_data
        image_base64 = base64.b64encode(image_data).decode("utf-8")
        record_with_image = {
            'id': record.id,
            'name': record.name,
            'time': record.time.strftime("%Y-%m-%d %H:%M:%S"),
            'image_data': f"data:image/jpeg;base64,{image_base64}"
        }
        records_with_images.append(record_with_image)

    return render_template('records.html', records=records_with_images, pagination=records)

if __name__ == '__main__':
    app.run(port=5002, debug=True)