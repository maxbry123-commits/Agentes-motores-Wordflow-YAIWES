# Puppeteer Demo

This is a typescript demo to show how to use Midscene.js with GLM-V to do some automation tasks.

## Steps

### Preparation

create `.env` file

```shell
# Replace with your own API key
MIDSCENE_MODEL_BASE_URL="https://open.bigmodel.cn/api/paas/v4" # or https://api.z.ai/api/paas/v4
MIDSCENE_MODEL_API_KEY="......"
MIDSCENE_MODEL_NAME="glm-4.6v"
MIDSCENE_MODEL_FAMILY="glm-v"
```

Refer to this document if your want to use other models: [https://midscenejs.com/model-strategy.html](https://midscenejs.com/model-strategy.html)

### Run demo

```bash
npm install
# Puppeteer needs download a compatible Chrome
npx puppeteer browsers install chrome
# run demo.ts
npx tsx demo.ts
```

# Reference

- [https://midscenejs.com/api.html](https://midscenejs.com/api.html)
- [https://midscenejs.com/integrate-with-puppeteer.html](https://midscenejs.com/integrate-with-puppeteer.html)
