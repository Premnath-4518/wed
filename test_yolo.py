from ultralytics import YOLO

# Load model
model = YOLO('models/eye_model.pt')

# Predict
results = model('static/images/test_yolo.jpg')

# Print predictions using model class names
for box in results[0].boxes:
    class_id = int(box.cls[0])
    confidence = float(box.conf[0])
    predicted_class = model.names[class_id]  # <- use model.names instead of your own list
    print(f"Predicted Disease: {predicted_class}, Confidence: {confidence:.2f}")
