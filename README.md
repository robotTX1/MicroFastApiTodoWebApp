# Requirements
- Python > 3.13 - https://www.python.org/
- UV - https://docs.astral.sh/uv/getting-started/installation/
- Docker, Docker compose
- Node - https://nodejs.org/en

# Running the app
1. Create a `.env` file:
```bash
PROFILE=local
```
2. Create the `local-config` directory
```bash
mkdir local-config
```
3. DM me for config, paste the config in the `local-config` directory
4. Run the app:
```bash
uv run uvicorn src.microfastapitodowebapp.main:app --reload --no-access-log --port 8081
```
5. Run node in separate terminal:
```bash
cd src/frontend
npm run watch
```
6. Access the app at:
``http://localhost:8081``