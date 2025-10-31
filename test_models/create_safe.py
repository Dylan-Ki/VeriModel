import pickle

# Tạo một object an toàn (danh sách số)
safe_obj = [1, 2, 3, 4, 5]
with open("test_models/safe_model.pkl", "wb") as f:
    pickle.dump(safe_obj, f)
