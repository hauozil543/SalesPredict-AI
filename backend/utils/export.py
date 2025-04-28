import pickle

def load_encoders():
    """
    Tải item_encoder và store_encoder từ file pickle.
    """
    with open('utils/item_encoder.pkl', 'rb') as f:
        item_enc = pickle.load(f)
    with open('utils/store_encoder.pkl', 'rb') as f:
        store_enc = pickle.load(f)
    return item_enc, store_enc

def load_scaler():
    """
    Tải scaler từ file pickle.
    """
    with open('utils/scaler.pkl', 'rb') as f:
        scaler = pickle.load(f)
    return scaler