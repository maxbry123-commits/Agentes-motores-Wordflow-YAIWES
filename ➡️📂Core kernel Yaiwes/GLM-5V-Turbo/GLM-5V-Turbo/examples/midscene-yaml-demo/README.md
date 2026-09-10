# Yaml Scripts

This is a yaml demo to show how to use Midscene.js with GLM-V to do some automation tasks.

## Preparation

create `.env` file

```shell
# Replace with your own API key
MIDSCENE_MODEL_BASE_URL="https://open.bigmodel.cn/api/paas/v4" # or https://api.z.ai/api/paas/v4
MIDSCENE_MODEL_API_KEY="......"
MIDSCENE_MODEL_NAME="glm-4.6v"
MIDSCENE_MODEL_FAMILY="glm-v"
```

Refer to this document if your want to use other models: [https://midscenejs.com/model-strategy.html](https://midscenejs.com/model-strategy.html)

## Install

Ensure that Node.js is installed.

```shell
npm i @midscene/cli
```

## Run

> For windows, you need to replace `./` with `.\`, like `midscene .\midscene-scripts\`.

Perform a search on ebay.com

```shell
npx midscene ./midscene-scripts/search-headphone-on-ebay.yaml
```

## Debug

Run a script with headed mode (i.e. you can see the browser window when running)

```shell
npx midscene --headed ./midscene-scripts/search-headphone-on-ebay.yaml
```

Keep the browser window open after the script finishes

```shell
npx midscene --keep-window ./midscene-scripts/search-headphone-on-ebay.yaml
```

# Reference

- [https://midscenejs.com/automate-with-scripts-in-yaml.html](https://midscenejs.com/automate-with-scripts-in-yaml.html)