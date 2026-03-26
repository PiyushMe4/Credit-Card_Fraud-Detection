import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from imblearn.over_sampling import SMOTE

# 1. Load and Clean
df = pd.read_csv('creditcard.csv')
df = df.drop_duplicates()

# 2. Scale Amount and save Scaler
scaler = StandardScaler()
df['Amount'] = scaler.fit_transform(df[['Amount']])
joblib.dump(scaler, 'scaler.pkl')

# 3. Prepare Data
df = df.drop(['Time'], axis=1)
X = df.drop('Class', axis=1)
y = df['Class']

# 4. Leakage-free Split
X_train_orig, X_test, y_train_orig, y_test = train_test_split(X, y, test_size=0.3, random_state=42, stratify=y)

# 5. Isolated Oversampling
smote = SMOTE(random_state=42)
X_train, y_train = smote.fit_resample(X_train_orig, y_train_orig)

# 6. Train Final Model
model = RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1)
model.fit(X_train, y_train)

# 7. Save Model
joblib.dump(model, 'credit_fraud_model.pkl')
print("Model and Scaler exported successfully!")
