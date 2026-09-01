export const modelOptions = [
  { value: 'weighted_lightgbm', label: 'Weighted LightGBM' },
  { value: 'random_forest', label: 'Random Forest' },
  { value: 'logistic_regression', label: 'Logistic Regression' },
  { value: 'weighted_xgboost', label: 'Weighted XGBoost' },
  { value: 'smote_lightgbm', label: 'SMOTE LightGBM' },
  { value: 'lgbm_eu_0.02', label: 'Easy Negative LGBM 0.02' },
  { value: 'lgbm_eu_0.05', label: 'Easy Negative LGBM 0.05' },
  { value: 'lgbm_eu_0.10', label: 'Easy Negative LGBM 0.10' },
]

export const datasetOptions = [
  { value: 'banksim', label: 'BankSim' },
  { value: 'sfindset', label: 'SFinDSet' },
  { value: 'global_bank', label: 'Global Bank' },
  { value: 'bank_marketing', label: 'Bank Marketing' },
  { value: 'synthetic', label: 'Synthetic' },
]

export const riskColors = {
  LOW: '#15803d',
  MEDIUM: '#ca8a04',
  HIGH: '#ea580c',
  CRITICAL: '#dc2626',
}

export const scenarioOptions = [
  'NORMAL',
  'HIGH_VELOCITY',
  'UNUSUAL_AMOUNT',
  'NEW_MERCHANT',
  'ACCOUNT_TAKEOVER',
  'CARD_TESTING',
]
