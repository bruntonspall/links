if [ -z "$VIRTUAL_ENV" ]; then
  if [ ! -d env ]; then 
    echo "Creating a virtual env"
    python -m venv env
    source env/bin/activate
    pip install -r requirements.txt
    pip install -r requirements-dev.txt
  else
    source env/bin/activate
  fi
fi
export PYTHONPATH=$(pwd)/app
pytest