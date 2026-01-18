set -e

echo "Building Tailwind"
python manage.py tailwind build

echo "Collection static files"
python manage.py collectstatic --noinput

npm install

npx tailwindcss -i ./theme/static/src/styles.css -o ./theme/static/dist/styles.css --minify

python manage.py collectstatic --noinput