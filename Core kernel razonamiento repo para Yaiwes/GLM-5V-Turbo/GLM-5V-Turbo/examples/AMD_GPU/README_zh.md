## AMD GPU 安装测试指南
### 请按照以下步骤运行,目前支持AMD MI300X GPU.
### 分步骤指南
#### 第一步
启动 Rocm-vllm docker:

```shell
docker run -d -it --ipc=host --network=host --privileged --cap-add=CAP_SYS_ADMIN --device=/dev/kfd --device=/dev/dri --device=/dev/mem --group-add video --cap-add=SYS_PTRACE --security-opt seccomp=unconfined -v /:/work -e SHELL=/bin/bash  --name vllm_GLM_V  rocm/vllm-dev:nightly
```

#### 第二步 登录huggingface
  Huggingface login

```shell
   huggingface-cli login 
```   

  Install pre-requisites:

```shell
pip install flash-attn
pip install transformers-v4.55.0-GLM-4.5V-preview
```

### 请确保以上依赖库已经成功安装。

#### 第三步 运行vllm在线推理

示例命令

```shell
VLLM_USE_V1=1 \
VLLM_USE_TRITON_FLASH_ATTN=0 \
SAFETENSORS_FAST_GPU=1 \
vllm serve zai-org/GLM-4.5V-FP8 \
     --tensor-parallel-size 4 \
     --tool-call-parser glm45 \
     --reasoning-parser glm45 \
     --enable-auto-tool-choice \
     --allowed-local-media-path / \
     --media-io-kwargs '{"video": {"num_frames": -1}}' \
     --no-enable-prefix-caching \
     --port 8800 
```
