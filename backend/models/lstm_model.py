import torch
import torch.nn as nn

class LSTMEmbForecast(nn.Module):
    def __init__(self, n_items, n_stores, embed_dim, num_feats, hidden_size):
        super().__init__()
        self.item_emb = nn.Embedding(n_items, embed_dim)
        self.store_emb = nn.Embedding(n_stores, embed_dim)
        self.lstm = nn.LSTM(
            input_size=num_feats + 2*embed_dim,
            hidden_size=hidden_size,
            num_layers=2,
            batch_first=True,
            dropout=0.3
        )
        self.fc = nn.Linear(hidden_size, 1)

    def forward(self, X_num, X_item, X_store):
        batch_size, seq_len, _ = X_num.size()
        emb_i = self.item_emb(X_item)
        emb_s = self.store_emb(X_store)
        x = torch.cat([X_num, emb_i, emb_s], dim=-1)
        out, _ = self.lstm(x)
        out = out[:, -1, :]
        return self.fc(out).squeeze()