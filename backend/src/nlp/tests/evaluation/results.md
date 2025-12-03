## Testing with usage of "Human Written Text" dataset by Youssef Elebiary from kaggle.
Dataset file - ../resources/Shuffled_Human.csv
Failures are saved in ./model_prediction_failures_human.csv. We are only using random 300 records from dataset and the results are: 
  139 failed, 161 passed in 323.51s 
Therefore, the model has a little above 50% accuracy - 54%. Another thing is, the model in most cases has a high confidence in his wrong predictions. Code for tests in ../test_model_predictions_human.py

## Testing using mixed dataset "LLM - Detect AI Generated Text Dataset" by sunil thite on kaggle
Dataset file - ../resources/Training_Essay_Data.csv
Probably the dataset the model was trained on
300 passed in 168.45s (0:02:48) XD to ten sam co damian

## Testing using mixed dataset "AI Vs Human Text" by Shayan Gerami on kaggle
Very good results in comparison to the first test, probably was caused by a bad dataset
14 failed, 286 passed in 228.33s



