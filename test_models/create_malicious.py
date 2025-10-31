import pickle
import os

# Tạo một object có mã độc (sử dụng os.system để minh họa)
class Malicious:
    def __reduce__(self):
        return (os.system, ("echo MALICIOUS_CODE_EXECUTED > malicious.txt",))

malicious_obj = Malicious()
with open("test_models/malicious_model.pkl", "wb") as f:
    pickle.dump(malicious_obj, f)
