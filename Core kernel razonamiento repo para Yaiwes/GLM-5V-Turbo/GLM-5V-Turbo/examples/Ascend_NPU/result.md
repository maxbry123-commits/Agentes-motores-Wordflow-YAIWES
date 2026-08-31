# 测试结果

以下数据在该测试环境中测试，vllm版本为`0.11.0`，仅使用 vllm bench用于测速，可以使用更高版本的vllm 进行测速。

## 测试环境

+ 镜像版本：xllm-dev
+ xllm版本：xllm/glm4.6v-preview
+ 模型 zai-org/GLM-4.6V (bf16)
+ 并行策略 TP8 (4卡8芯)， 未设置其他并行策略。

## 单并发VisionArena数据集测试

### 命令

```shell
vllm bench serve \
--backend openai-chat \
--endpoint /v1/chat/completions \
--model /path/to/GLM-4.6V-Air-1127/ \
--served-model-name GLM-4.6V-Air-1127 \
--base-url http://localhost:28000 \
--dataset-name hf \
--hf-name lmarena-ai/VisionArena-Chat \
--dataset-path /path/to/VisionArena-Chat \
--num-prompts 1000 \
--max-concurrency 1 \
--ready-check-timeout-sec 0
```

### 结果

```
============ Serving Benchmark Result ============
Successful requests:                     1000      
Maximum request concurrency:             1         
Benchmark duration (s):                  2342.54   
Total input tokens:                      90524     
Total generated tokens:                  126176    
Request throughput (req/s):              0.43      
Output token throughput (tok/s):         53.86     
Peak output token throughput (tok/s):    64.00     
Peak concurrent requests:                3.00      
Total Token throughput (tok/s):          92.51     
---------------Time to First Token----------------
Mean TTFT (ms):                          166.59    
Median TTFT (ms):                        162.54    
P99 TTFT (ms):                           272.57    
-----Time per Output Token (excl. 1st token)------
Mean TPOT (ms):                          17.39     
Median TPOT (ms):                        17.07     
P99 TPOT (ms):                           26.45     
---------------Inter-token Latency----------------
Mean ITL (ms):                           17.14     
Median ITL (ms):                         17.05     
P99 ITL (ms):                            26.05
==================================================
```
