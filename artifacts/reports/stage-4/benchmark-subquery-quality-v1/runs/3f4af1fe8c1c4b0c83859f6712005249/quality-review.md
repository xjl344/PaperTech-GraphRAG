# 拆分诊断：读取已有实测结果

程序校验失败不等于模型所有语义判断都错误；校验通过也不等于子查询可用。

```json
{
  "completed_model_calls": 4,
  "valid": 4,
  "invalid": 0,
  "validation_error_types": {},
  "model_wall_seconds": 174.3526828000322,
  "prompt_tokens": 1506,
  "completion_tokens": 656,
  "missing_usage_rows": [],
  "source_fragment_validity_is_not_semantic_accuracy": true,
  "mean_seconds": 43.58817070000805,
  "median_seconds": 40.49873010000738,
  "load_seconds": 15.170239700000002,
  "prompt_eval_seconds": 4.25753,
  "eval_seconds": 154.731144
}
```
