import torch
import torch.nn as nn

class LSTMEmbForecast(nn.Module):
    def __init__(self, n_items, n_stores, embed_dim, num_feats, hidden_size, num_layers=1, dropout=0.25):
        super().__init__()
        self.item_emb = nn.Embedding(n_items, embed_dim)
        self.store_emb = nn.Embedding(n_stores, embed_dim)
        input_size = embed_dim * 2 + num_feats
        self.feat_fc = nn.Linear(num_feats, num_feats * 2)
        self.lstm = nn.LSTM(input_size + num_feats, hidden_size, num_layers=num_layers, batch_first=True)
        self.dropout = nn.Dropout(dropout)
        self.fc = nn.Linear(hidden_size, 1)

    def forward(self, X_num, X_item, X_store):
        item_emb = self.item_emb(X_item)
        store_emb = self.store_emb(X_store)
        X_num_transformed = self.feat_fc(X_num)
        X = torch.cat((X_num_transformed, item_emb, store_emb), dim=-1)
        lstm_out, _ = self.lstm(X)
        lstm_out = self.dropout(lstm_out)
        out = self.fc(lstm_out[:, -1, :])
        return out.squeeze()