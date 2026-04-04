from nlp.detector.inference import run_model_inference

def predict_with_model(model, tokenizer, text, return_details=False):
  device = next(model.parameters()).device
  encoded = tokenizer(text, return_tensors="pt", truncation=True, padding=True, max_length=512)
  encoded = {k: v.to(device) for k, v in encoded.items()}

  temperature = float(getattr(model, "_factify_temperature", 1.0))
  if temperature <= 0:
    temperature = 1.0
    
  inference = run_model_inference(model, encoded, temperature=temperature)
  
  mean_probs = inference["mean_probs"]
  prob_generated = float(mean_probs[0, 1].detach().cpu().item())
  
  if not return_details:
    return prob_generated
    
  raw_mean_probs = inference["raw_mean_probs"]
  std_probs = inference["std_probs"]
  entropy_values = inference["entropy"]
  variation_values = inference["variation"]
  
  entropy_value = float(entropy_values[0].detach().cpu().item()) if entropy_values.ndim > 0 else float(entropy_values.detach().cpu().item())
  variation_value = float(variation_values[0].detach().cpu().item()) if variation_values.ndim > 0 else float(variation_values.detach().cpu().item())

  return {
    "prob_generated": prob_generated,
    "prob_human": float(mean_probs[0, 0].detach().cpu().item()),
    "prob_generated_raw": float(raw_mean_probs[0, 1].detach().cpu().item()),
    "prob_human_raw": float(raw_mean_probs[0, 0].detach().cpu().item()),
    "prob_generated_std": float(std_probs[0, 1].detach().cpu().item()),
    "prob_human_std": float(std_probs[0, 0].detach().cpu().item()),
    "prob_entropy": entropy_value,
    "prob_variation_ratio": variation_value,
    "mc_dropout_passes": 16,
    "temperature": float(temperature),
  }
