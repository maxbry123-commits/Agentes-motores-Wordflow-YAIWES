# MetaAgent: Automatically Building Multi-Agent System based on Finite State Machine
🌐 **[Website]](https://mercury7353.github.io/MetaAgent-Static-Demo/)**
🔗 **[Paper](TBD)**

<p align="center">
  <img src="/images/face.png" alt="image" width="250"/>
</p>

## 🎆 News
- [2025/5] Accepted to ICML2025.

## 👀 Overview  
![image](/images/compare.png)
MetaAgent is a framework that can be used to build your own multi-agent system  automatically by **one line of prompt**.  
The Open-Sourced framework 

The Multi-Agent System (MAS) is based on the Finite State Machine (FSM), which is shown in the figure.  

### Auto-generation of Multi-Agent System  
- Given a general task description(eg. Build a multi-agent system for software development), MetaAgent can automatically generate a multi-agent system with several agents.  
- Unlike other auto-generation framework, MetaAgent can generate a multi-agent system without external training data.  
- The generated multi-agent system is also able to solve every cases of the given task domain.   


### Why Finite State Machine?
![image](FSM.png)
The finite state machine has several features:   

🔧 **Tool Enabled**: The agent can use tools to help it complete tasks.  
🔄 **State Traceback**: The agent can traceback the state of the system when the task fails.   



## 📹 Demo Video  

<video src="https://github.com/Mercury7353/MetaAgent/assets/73fde677-fad0-4109-b18a-15f26fdcb42e"> </video> 

## 🚀 Quick Start    
### Install
To set up the environment of MetaAgent, please run the following command:
```bash
pip install -r requirements.txt
```

### Setup your API-Keys
```bash
export OPENAI_API_KEY='your-openai-api-key'
export SERP_API_KEY=''
... (Other API Keys for tools)

```

### Run
- In the code base:  
```bash
cd autodesign
python building_pipeline.py
```  

```bash
cd evaluate
python general_test.py # test any input on the designed FSM.
```

- In the interface:  
```bash
cd web
python app.py
```  

## Customize Your own FSM
- Use baseclass/FSM_GEN.py to auto-design your FSM  
- Use autodesign/Optimization.py to optimize the FSM  
- Use autodesign/evaluate/general_test.py to test the FSM  

## 🤝 Support  

### Contact Us  
📮 Email: zhangyaolun5@gmail.com  


