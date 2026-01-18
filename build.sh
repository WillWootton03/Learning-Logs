set -e

npm install

echo "Building Tailwind CSS"
npx tailwindcss -i ./theme/static/src/styles.css -o ./theme/static/dist/styles.css --minify

echo "Collection static files"
python manage.py collectstatic --noinput